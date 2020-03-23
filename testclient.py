import asyncio
import logging
import websockets

logging.basicConfig(level=logging.DEBUG)


async def consumer_handler():
    # ----------- client 端 -----------
    headers = {"Authorization": "J3SyDLNFWpk89Q8Yausno3o1Ugb90WlFsqVVGIjt53%2BnrTj2RvIjtitJFunqPhToGuyg9l9C4i5ETM/JYCNgEjTT7Caj0NwaCvfAICGm8HhTBedvH1FWC2sl0bJmWY27tZcJFDedr/VH1x8Yve22xTvK4K3b62yxDWJcTOtWJarp5TFCIzBM93/R3MU2Bw4BwXlc/eTab0Na9g/k14s/n0a8LL6YOWcUqBiDEJ3PHqwHmfnDem8DehLBuXsR3nT1wI%2Bh/XS%2BWBZtX6wfYj7hsm6jMgAIN11C1SufVi5/hhiCopt/FzQqvduIw1LFth7fPRPciVyyoi/5d7S6YVyjMw%3D%3D"}
    async with websockets.connect('ws://127.0.0.1:9191', extra_headers=headers) as websocket:
        await websocket.send('{"access_token":"678901"}')
        async for message in websocket:
            print(message)


loop = asyncio.get_event_loop()

loop.run_until_complete(consumer_handler())