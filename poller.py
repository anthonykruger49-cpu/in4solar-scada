import asyncio, time
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pymodbus.client import AsyncModbusTcpClient

app = FastAPI()
LTE_GW_IP = "10.8.0.12"   # Change to your LTE Gateway IP
LTE_GW_PORT = 502

telemetry_cache = {"timestamp": 0, "inverters": [], "meters": []}

async def poll_loop():
    client = AsyncModbusTcpClient(LTE_GW_IP, port=LTE_GW_PORT, timeout=2)
    while True:
        try:
            if not client.connected:
                await client.connect()
            # Poll Megarevo MPS Inverters (Slave IDs 1..4)
            # Poll Schneider PM5xxx Meters (Slave IDs 11..14)
            telemetry_cache["timestamp"] = int(time.time() * 1000)
        except Exception as e:
            print("Modbus poll error:", e)
        await asyncio.sleep(2.0)

@app.on_event("startup")
async def startup():
    asyncio.create_task(poll_loop())

@app.get("/")
async def serve_dashboard():
    return FileResponse("index.html")

@app.get("/api/telemetry")
async def get_telemetry():
    return telemetry_cache
