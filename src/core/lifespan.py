import asyncio 
from contextlib import contextmanager
from fastapi import FastAPI 
from hiki_integration.connection import HikiVisionConnection

hikvision = HikiVisionConnection()

@contextmanager
def lifespan(app: FastAPI):
    asyncio.create_task(hikvision.stream_events())  
    yield
