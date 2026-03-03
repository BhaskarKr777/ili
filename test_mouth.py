import asyncio
import websockets
import json
import time

TOKEN = open("vtube_token.txt").read().strip()

async def test():
    async with websockets.connect("ws://localhost:8002") as ws:

        async def send(p):
            await ws.send(json.dumps({
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "test",
                **p
            }))
            return json.loads(await ws.recv())

        # Auth
        await send({
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": "OffTute",
                "pluginDeveloper": "OffTuteAI",
                "authenticationToken": TOKEN
            }
        })
        print("Authenticated — watch the character!")

        # Open mouth wide
        print("Opening mouth...")
        await send({
            "messageType": "InjectParameterDataRequest",
            "data": {
                "faceFound": True,
                "mode": "set",
                "parameterValues": [
                    {"id": "ParamMouthOpen", "value": 1.0, "weight": 1.0}
                ]
            }
        })
        await asyncio.sleep(3)

        # Raise eyebrows
        print("Raising eyebrows...")
        await send({
            "messageType": "InjectParameterDataRequest",
            "data": {
                "faceFound": True,
                "mode": "set",
                "parameterValues": [
                    {"id": "ParamBrowLY", "value": 1.0, "weight": 1.0},
                    {"id": "ParamBrowRY", "value": 1.0, "weight": 1.0},
                    {"id": "ParamMouthOpen", "value": 0.0, "weight": 1.0}
                ]
            }
        })
        await asyncio.sleep(3)
        print("Done! Did you see it move?")

asyncio.run(test())