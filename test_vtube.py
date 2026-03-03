import asyncio
import websockets
import json

async def test():
    uri = "ws://localhost:8001"
    print("Connecting to VTube Studio...")
    
    async with websockets.connect(uri) as ws:
        print("Connected!")
        
        msg = json.dumps({
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "test123",
            "messageType": "APIStateRequest"
        })
        
        await ws.send(msg)
        print("Message sent. Waiting for response...")
        
        response = await ws.recv()
        data = json.loads(response)
        print("Response received!")
        print(json.dumps(data, indent=2))

asyncio.run(test())