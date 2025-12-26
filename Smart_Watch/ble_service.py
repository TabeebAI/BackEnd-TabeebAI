import asyncio
import platform
from datetime import datetime
from fastapi import FastAPI, HTTPException
from bleak import BleakClient, BleakScanner

app = FastAPI(title="GL-SWA55 Health Monitor")

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

NOTIFY_CHAR = "0000ff03-0000-1000-8000-00805f9b34fb"
WRITE_CHAR  = "0000ff02-0000-1000-8000-00805f9b34fb"

WAKE_CMD          = bytearray([0xBC, 0x48, 0x03, 0x01])
LIVE_HR_CMD       = bytearray([0xBC, 0x48, 0x02, 0x01]) 
LIVE_BP_CMD       = bytearray([0xBC, 0x48, 0x02, 0x02]) 
STOP_MEASURE_CMD  = bytearray([0xBC, 0x48, 0x02, 0x00])


def extract_health_data(pkt: bytearray, mode: str):
    data = list(pkt)
    if len(data) < 6:
        return None

    if mode == "hr":
        return {"hr": data[4]}
    
    elif mode == "bp":
        return {
            "systolic": data[4],
            "diastolic": data[5]
        }
    return None


async def live_measure(address: str, cmd: bytearray, mode: str, duration: int = 15):
    results = []
    start_time = datetime.now()

    async def handler(sender, data):
        parsed = extract_health_data(data, mode)
        if parsed:
            results.append(parsed)
            print(f"New Data ({mode}): {parsed}")

    try:
        async with BleakClient(address, timeout=25.0) as client:
            if not client.is_connected:
                raise HTTPException(status_code=400, detail="Device not connected")

            await client.write_gatt_char(WRITE_CHAR, WAKE_CMD)
            await asyncio.sleep(0.5)

            await client.write_gatt_char(WRITE_CHAR, cmd)
            await asyncio.sleep(0.2)

            await client.start_notify(NOTIFY_CHAR, handler)
            await asyncio.sleep(duration)

            await client.write_gatt_char(WRITE_CHAR, STOP_MEASURE_CMD)
            await client.stop_notify(NOTIFY_CHAR)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BLE Error: {str(e)}")

    return {
        "status": "success",
        "device": address,
        "mode": mode,
        "measurements_count": len(results),
        "latest_data": results[-1] if results else "No data received",
        "timestamp": start_time.isoformat()
    }


@app.get("/scan")
async def scan_devices():
    devices = await BleakScanner.discover(timeout=5)
    return [{"name": d.name or "Unknown", "address": d.address} for d in devices]

@app.get("/hr/{address}")
async def get_hr(address: str, duration: int = 15):
 
    return await live_measure(address, LIVE_HR_CMD, mode="hr", duration=duration)

@app.get("/bp/{address}")
async def get_bp(address: str, duration: int = 20):

    return await live_measure(address, LIVE_BP_CMD, mode="bp", duration=duration)