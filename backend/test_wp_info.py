import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://wordpress.org/wp-json/")
        if r.status_code == 200:
            data = r.json()
            print("Name:", data.get("name"))
            print("Desc:", data.get("description"))

asyncio.run(main())
