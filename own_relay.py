#create own relay. Use ot for publishing the messages.
# relay.py
import asyncio
import websockets
import json
import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket as FastAPIWebSocket
from fastapi.responses import HTMLResponse
import uvicorn

logging.basicConfig(level=logging.INFO)
subscriptions = {}  # Store client subscriptions
events = []  # Store all events
app = FastAPI()

# Existing WebSocket relay handler (unchanged)
async def handle_connection(websocket):
    client_id = f"client_{id(websocket)}"
    logging.info(f"New connection: {client_id}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data[0].upper()

                if msg_type == "EVENT":
                    event = data[1]
                    event["received_at"] = datetime.now().isoformat()
                    events.append(event)
                    logging.info(f"Received event: {event['id']}")
                    
                    for sub_id, (client, filters) in subscriptions.items():
                        if matches_filter(event, filters):
                            await client.send(json.dumps(["EVENT", sub_id, event]))

                elif msg_type == "REQ":
                    sub_id = data[1]
                    filters = data[2] if len(data) > 2 else {}
                    subscriptions[sub_id] = (websocket, filters)
                    logging.info(f"New subscription: {sub_id}")
                    
                    for event in events:
                        if matches_filter(event, filters):
                            await websocket.send(json.dumps(["EVENT", sub_id, event]))
                    await websocket.send(json.dumps(["EOSE", sub_id]))

                elif msg_type == "CLOSE":
                    sub_id = data[1]
                    if sub_id in subscriptions:
                        del subscriptions[sub_id]
                        logging.info(f"Closed subscription: {sub_id}")

            except json.JSONDecodeError:
                logging.error("Invalid JSON message received")
            except Exception as e:
                logging.error(f"Error processing message: {e}")

    except websockets.ConnectionClosed:
        logging.info(f"Connection closed: {client_id}")
    finally:
        subscriptions_to_remove = [sub_id for sub_id, (client, _) in subscriptions.items() 
                                 if client == websocket]
        for sub_id in subscriptions_to_remove:
            del subscriptions[sub_id]

def matches_filter(event, filters):
    if not filters:
        return True
    if "kinds" in filters and event.get("kind") not in filters["kinds"]:
        return False
    if "authors" in filters and event.get("pubkey") not in filters["authors"]:
        return False
    if "ids" in filters and event.get("id") not in filters["ids"]:
        return False
    return True

# Web app endpoints
@app.get("/", response_class=HTMLResponse)
async def get_web_app():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nostr Relay Hub</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .event-card { transition: all 0.2s ease-in-out; }
            .event-card:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        </style>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <header class="bg-indigo-600 text-white p-4 shadow-md">
            <div class="container mx-auto">
                <h1 class="text-2xl font-bold">Nostr Relay Hub</h1>
                <p class="text-sm">A decentralized message relay network</p>
            </div>
        </header>
        <main class="container mx-auto mt-8 px-4">
            <section class="mb-8">
                <h2 class="text-xl font-semibold mb-4 text-gray-800">Connected Relays</h2>
                <div id="relay-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
            </section>
            <section>
                <h2 class="text-xl font-semibold mb-4 text-gray-800">Event Feed</h2>
                <div id="events" class="space-y-4"></div>
            </section>
        </main>
        <script>
            async function fetchData() {
                // Fetch relays
                const relayResponse = await fetch('/relays');
                const relays = await relayResponse.json();
                document.getElementById('relay-list').innerHTML = relays.map(r => `
                    <div class="bg-white p-4 rounded-lg shadow">
                        <span class="font-medium text-indigo-600">${r.url}</span>
                        <span class="ml-2 text-sm ${r.status === 'active' ? 'text-green-500' : 'text-red-500'}">
                            (${r.status})
                        </span>
                    </div>
                `).join('');

                // Fetch events
                const eventResponse = await fetch('/events');
                const events = await eventResponse.json();
                document.getElementById('events').innerHTML = events.map(e => `
                    <div class="event-card bg-white p-6 rounded-lg shadow">
                        <div class="flex items-center mb-2">
                            <div class="w-10 h-10 bg-indigo-200 rounded-full flex items-center justify-center text-indigo-800 font-bold">
                                ${e.pubkey.slice(0, 2).toUpperCase()}
                            </div>
                            <div class="ml-3">
                                <p class="font-medium text-gray-800">${e.pubkey.slice(0, 8)}...</p>
                                <p class="text-sm text-gray-500">${new Date(e.received_at).toLocaleString()}</p>
                            </div>
                        </div>
                        <p class="text-gray-700">${e.content}</p>
                    </div>
                `).join('');
            }
            fetchData();
            setInterval(fetchData, 5000); // Refresh every 5 seconds
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/relays")
async def get_relays():
    return [{"url": "ws://localhost:8765", "status": "active"}]

@app.get("/events")
async def get_events():
    return events

# Run both WebSocket server and FastAPI
async def main():
    websocket_server = await websockets.serve(
        handle_connection,
        "localhost",
        8765
    )
    logging.info("Nostr relay running on ws://localhost:8765")
    
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
