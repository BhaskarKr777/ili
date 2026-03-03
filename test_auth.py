import asyncio
import websockets
import json

PLUGIN_NAME = "OffTute"
PLUGIN_DEV  = "OffTuteAI"
TOKEN_FILE  = "vtube_token.txt"

async def authenticate():
    uri = "ws://localhost:8002"
    
    async with websockets.connect(uri) as ws:
        
        # ── Request a token ───────────────────────────────────────────
        print("Requesting authentication token...")
        await ws.send(json.dumps({
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "auth1",
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": PLUGIN_NAME,
                "pluginDeveloper": PLUGIN_DEV,
            }
        }))
        
        # ── VTube Studio will show a popup — click ALLOW ───────────────
        print(">>> CHECK VTUBE STUDIO — click ALLOW on the popup! <<<")
        response = json.loads(await ws.recv())
        
        if "authenticationToken" not in response.get("data", {}):
            print("Failed! Response:", json.dumps(response, indent=2))
            return
            
        token = response["data"]["authenticationToken"]
        print(f"Token received: {token[:20]}...")
        
        # Save token for later use
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        print(f"Token saved to {TOKEN_FILE}")
        
        # ── Authenticate using token ───────────────────────────────────
        await ws.send(json.dumps({
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "auth2",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": PLUGIN_NAME,
                "pluginDeveloper": PLUGIN_DEV,
                "authenticationToken": token
            }
        }))
        
        result = json.loads(await ws.recv())
        authenticated = result.get("data", {}).get("authenticated", False)
        
        if authenticated:
            print("✅ Authentication successful!")
        else:
            print("❌ Authentication failed:", json.dumps(result, indent=2))

asyncio.run(authenticate())