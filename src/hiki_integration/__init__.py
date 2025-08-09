import logging
import requests
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import json
import re

# === CONFIG ===
DEVICE_IP = "192.168.0.51"
USERNAME = "admin"
PASSWORD = "nokia113"


url = f"http://{DEVICE_IP}/ISAPI/Event/notification/alertStream?format=json"

auth = HTTPDigestAuth(USERNAME, PASSWORD)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

print(f"[+] Connecting to {url}...")

with requests.get(url, auth=auth, stream=True, timeout=60) as response:
    if response.status_code != 200:
        print(f"[!] Failed to connect: {response.status_code}")
    else:
        print("[✓] Connected. Waiting for events...\n")

        buffer = ""
        for line in response.iter_lines():
            try:
                logger.debug(line.decode())
            except Exception as e:
                pass
