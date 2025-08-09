import asyncio
import httpx
import os
from datetime import datetime
import json
import traceback
from schemas import EnterEvent

from core.models.user import User
from core.config import settings
from core.utils.get_user import get_user_by_username
from core.utils.db_helper import session
from .service import UserLogsService


class HikiVisionConnection:
    def __init__(self):
        self.device_ip = settings.camera.device_ip
        self.username = settings.camera.username
        self.password = settings.camera.password
        self.url = settings.camera.url
        self.boundary = b"--MIME_boundary"
        self.last_user_id = None  
        self.session = session
        self.service = UserLogsService(db=session)

    async def connection_stream(self):
        """Connect to Hikvision device and yield each multipart 'part' as bytes."""
        auth = httpx.DigestAuth(self.username, self.password)

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", self.url, auth=auth) as response:
                if response.status_code != 200:
                    print(f"[ERROR] Failed to connect: {response.status_code}")
                    return

                print("[INFO] Connected. Waiting for events...")

                buffer = b""
                async for chunk in response.aiter_bytes():
                    buffer += chunk
                    while True:
                        boundary_index = buffer.find(self.boundary)
                        if boundary_index == -1:
                            break

                        part = buffer[:boundary_index]
                        buffer = buffer[boundary_index + len(self.boundary):]
                        part = part.lstrip(b"\r\n")

                        if part.strip():
                            yield part

    def save_image(self, image_bytes: bytes, user_id: int):
        """Save image to images/ with timestamp and update user log."""
        os.makedirs("images", exist_ok=True)
        filename = f"images/{datetime.now():%Y%m%d_%H%M%S_%f}.jpg"
        with open(filename, "wb") as f:
            f.write(image_bytes)

        print(f"[📷] Image saved: {filename}")

        # Update user log with image path if user_id is valid
        if user_id is not None:
            self.service.update_user_log_by_id(user_id=user_id, field_name="user_face_path", field_value=filename)

        return filename

    async def process_part(self, part: bytes):
        """Process one part of the multipart stream."""
        header_end = part.find(b"\r\n\r\n")
        if header_end == -1:
            return

        headers_raw = part[:header_end].decode(errors="ignore")
        content = part[header_end + 4:]

        if "application/json" in headers_raw:
            try:
                json_data = json.loads(content.decode(errors="ignore"))
                event_type = json_data.get("eventType")
                dt = json_data.get("dateTime")

                if event_type == "AccessControllerEvent":
                    name = json_data.get("AccessControllerEvent", {}).get("name")
                    person = name if name else "unknown"

                    user_data: User = await get_user_by_username(session=self.session, username=person)
                    if user_data:
                        event = EnterEvent(user_id=user_data.id, enter_time=dt)
                        self.service.create_user_logs(user_log=event)

                        self.last_user_id = user_data.id  # Store last user id safely
                        print(f"[✅] Parsed AccessControllerEvent: {event.model_dump()}, data: {json_data}")
                    else:
                        print(f"[WARN] User '{person}' not found in database.")
                        self.last_user_id = None
                else:
                    event = EnterEvent(user_id=None, enter_time=dt)
                    print(f"[📨] Non-AccessControllerEvent: {event.model_dump()}, data: {json_data}")

            except Exception as e:
                print(f"[ERROR] Failed to parse JSON: {e}")
                print(traceback.format_exc())

        elif "image/jpeg" in headers_raw:
            if self.last_user_id is not None:
                self.save_image(content, user_id=self.last_user_id)
            else:
                print("[WARN] Received image but no associated user found (last_user_id is None).")
        else:
            print("[WARN] Unknown content type in part")

    async def stream_events(self):
        """Main loop: read parts from the stream and process them."""
        try:
            async for part in self.connection_stream():
                await self.process_part(part)
        except Exception as e:
            print(f"[ERROR] Streaming error: {e}")
            print(traceback.format_exc())


async def main():
    hikvision = HikiVisionConnection()
    await hikvision.stream_events()


if __name__ == "__main__":
    asyncio.run(main())
