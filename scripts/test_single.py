import httpx
import asyncio
import json

API_URL = "http://localhost:8000/api/v1/recommendations/"

payload = {
    "preferences": {"adventure": 0.9, "nature": 0.7},
    "constraints": [],
    "mood": "I want to climb mountains and feel the fresh air"
}

async def test_single():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(API_URL, json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_single())
