"""
MESSAGE BROKER IMPLEMENTATION WITH CORE CONCEPTS EXPLAINED

A simple WebSocket-based message broker demonstrating pub/sub architecture.
"""
import asyncio
import websockets
from collections import defaultdict

# ======================
# DATA STRUCTURES
# ======================

# Concept: Message Broker State
# - 'channels' acts as a message history log (persistence would enhance this)
# - 'subscribers' tracks live connections per channel (pub/sub pattern)
channels = defaultdict(list)        # {channel_name: [message1, message2]}
subscribers = defaultdict(set)      # {channel_name: set(websocket1, websocket2)}

# ======================
# CONNECTION HANDLER
# ======================
async def handle_client(websocket, path):
    """
    Handles the full-duplex WebSocket connection for a single client.
    
    Concept: Client-Server Architecture
    - Each client gets its own handler instance
    - Broker maintains centralized control
    
    Concept: WebSocket Protocol
    - Persistent connection unlike HTTP
    - Enables real-time bidirectional communication
    """
    try:
        # Main message processing loop
        async for raw_message in websocket:
            # ======================
            # SUBSCRIBE COMMAND
            # ======================
            if raw_message.startswith("SUBSCRIBE:"):
                # Concept: Pub/Sub Pattern
                # Client expresses interest in a channel
                channel = raw_message.split(":")[1]
                if not channel.isalnum(): # Basic validation
                    print("Invalid channel name")
                    return
                subscribers[channel].add(websocket)
                
                # Concept: Channel/Topic
                # Named pathway for message distribution
                await websocket.send(f"SUB-ACK:{channel}")
                
                # Optional: Send message history
                for msg in channels.get(channel, []):
                    await websocket.send(f"MSG:{channel}:{msg}")

            # ======================
            # PUBLISH COMMAND
            # ======================
            elif raw_message.startswith("PUBLISH:"):
                # Concept: Message Distribution
                # Broker receives and forwards messages
                _, channel, content = raw_message.split(":", 2)
                
                # Store message (simple persistence)
                channels[channel].append(content)
                
                # Concept: Fan-out Delivery
                # Send to all subscribers of this channel
                for subscriber in subscribers[channel]:
                    try:
                        await subscriber.send(f"MSG:{channel}:{content}")
                    except Exception as e:
                        print(f"Error sending message to {subscriber}: {e}") # Log the error
                        subscribers[channel].remove(subscriber)

            # ======================
            # UNSUBSCRIBE COMMAND
            # ======================
            elif raw_message.startswith("UNSUBSCRIBE:"):
                channel = raw_message.split(":")[1]
                if websocket in subscribers[channel]:
                    subscribers[channel].remove(websocket)
                await websocket.send(f"UNSUB-ACK:{channel}")

    finally:
        # Clean up when connection drops
        # Concept: Connection Management
        for channel in subscribers:
            subscribers[channel].discard(websocket)

# ======================
# SERVER INITIALIZATION
# ======================
async def main():
    """
    Concept: Message Broker Core
    - The central message routing component
    - Maintains all active connections
    - Manages channel subscriptions
    """
    # Start WebSocket server
    # Concept: Network Endpoint
    # Clients connect to ws://localhost:8765
    async with websockets.serve(
        handle_client, 
        "localhost", 
        8765, 
        ping_interval=None
    ):
        print("Broker running on ws://localhost:8765")
        await asyncio.Future()  # Run indefinitely

# Start the broker
if __name__ == "__main__":
    asyncio.run(main())
