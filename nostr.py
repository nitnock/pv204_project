import asyncio
from nostr_sdk import Keys, Client, EventBuilder, NostrSigner

async def publish_event():
    private_key_hex = "npub1z25nn7mvs7jxp8ygyygqv534l6kxvj57qh5vr0dafkjm8szq2zas5v6mum"
    relay_url = "wss://nos.lol/"
    
    keys = Keys.parse(private_key_hex)
    signer = NostrSigner.keys(keys)
    client = Client(signer)
    
    await client.add_relay(relay_url)
    await client.connect()
    
    message = "Emergency Broadcast"
    event_builder = EventBuilder.text_note(message)
    res = await client.send_event_builder(event_builder)
    
    event_id = res.id.to_bech32() if res.id else None
    print(f"Message: {message}")
    print(f"Event ID: {event_id}")
    print(f"Sent to: {res.success}")
    print(f"Not sent to: {res.failed}")

if __name__ == "__main__":
    asyncio.run(publish_event())