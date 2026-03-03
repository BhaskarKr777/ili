"""
Run this to see all available parameters and hotkeys
for the currently loaded model in VTube Studio.
"""

import asyncio
import websockets
import json

TOKEN_FILE = "vtube_token.txt"
VTS_URL    = "ws://localhost:8002"


async def inspect():
    with open(TOKEN_FILE) as f:
        token = f.read().strip()

    async with websockets.connect(VTS_URL) as ws:

        async def send(payload):
            full = {
                "apiName":    "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID":  "inspect",
                **payload
            }
            await ws.send(json.dumps(full))
            return json.loads(await ws.recv())

        # Authenticate
        r = await send({
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName":          "OffTute",
                "pluginDeveloper":     "OffTuteAI",
                "authenticationToken": token,
            }
        })
        if not r.get("data", {}).get("authenticated"):
            print("❌ Auth failed. Re-run test_auth.py")
            return

        print("✅ Authenticated\n")

        # ── List hotkeys ──────────────────────────────────────────────
        print("=" * 50)
        print("HOTKEYS IN CURRENT MODEL:")
        print("=" * 50)
        r = await send({
            "messageType": "HotkeysInCurrentModelRequest",
            "data": {}
        })
        hotkeys = r.get("data", {}).get("availableHotkeys", [])
        if hotkeys:
            for hk in hotkeys:
                print(f"  ID: {hk.get('hotkeyID'):<30} Name: {hk.get('name')}")
        else:
            print("  No hotkeys found. Add them in VTube Studio settings.")

        print()

        # ── List parameters ───────────────────────────────────────────
        print("=" * 50)
        print("LIVE2D PARAMETERS:")
        print("=" * 50)
        r = await send({
            "messageType": "Live2DParameterListRequest",
            "data": {}
        })
        params = r.get("data", {}).get("parameters", [])
        if params:
            for p in params:
                print(
                    f"  {p.get('name'):<30} "
                    f"min={p.get('min'):<6} "
                    f"max={p.get('max'):<6} "
                    f"default={p.get('defaultValue')}"
                )
        else:
            print("  No parameters found. Make sure a model is loaded.")

asyncio.run(inspect())