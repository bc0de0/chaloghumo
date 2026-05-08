import httpx
import asyncio

URL = "https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_public.csv"

async def inspect():
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", URL) as response:
            count = 0
            async for line in response.aiter_lines():
                if count > 5:
                    break
                print(line)
                count += 1

if __name__ == "__main__":
    asyncio.run(inspect())
