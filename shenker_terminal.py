import asyncio
from schenker_server import track_schenker

async def main():
    ref = input("Enter reference number: ")
    res = await track_schenker(ref)
    print(res)

asyncio.run(main())
