import websocket
import threading
import time
import sys

def on_message(ws, message):
    print(f"\n[SERVER]: {message}")

def on_error(ws, error):
    print(f"\n[ERROR]: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"\n[CLOSED] Code: {close_status_code}, Msg: {close_msg}")

def on_open(ws):
    print("\n[CONNECTED] Connection established successfully!")
    print("Waiting for messages... (Ctrl+C to exit)")

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws_url = "ws://localhost:3001"
    
    # Custom headers for our Authorizer
    headers = {
        "Authorization": "allow"
    }

    print(f"Connecting to {ws_url} with headers: {headers}")
    
    ws = websocket.WebSocketApp(
        ws_url,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    try:
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
