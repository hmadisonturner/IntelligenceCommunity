"""
MESSAGE BROKER IMPLEMENTATION WITH CORE CONCEPTS EXPLAINED

A simple WebSocket-based message broker demonstrating pub/sub architecture.
"""
import logging
import asyncio
import websockets
import uuid
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler("sample.log"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger(__name__)

# ======================
# DATA STRUCTURES
# ======================

# Concept: Message Broker State
# - 'channels' acts as a message history log (persistence would enhance this)
# - 'subscribers' tracks live connections per channel (pub/sub pattern)
# - 'client_identities' maps websockets to usernames (identity management)
channels = defaultdict(list)        # {channel_name: [(username, message1), (username, message2)]}
subscribers = defaultdict(set)      # {channel_name: set((username, websocket1), (username, websocket2))}
client_identities = {}              # {websocket: username}

# ======================
# CONNECTION HANDLER
# ======================
async def handle_client(websocket):
    """
    Handles the full-duplex WebSocket connection for a single client.

    Concept: Client-Server Architecture
    - Each client gets its own handler instance
    - Broker maintains centralized control

    Concept: WebSocket Protocol
    - Persistent connection unlike HTTP
    - Enables real-time bidirectional communication

    Concept: Identity Management
    - Each client is assigned a unique username on connection
    - Messages are attributed to their sender
    """
    try:
        # Assign identity on connection
        username = f"user-{str(uuid.uuid4())[:8]}"
        client_identities[websocket] = username

        # Send identity to client
        await websocket.send(f"IDENTITY:{username}")
        log.info(f"New client connected with identity: {username}")

        # Main message processing loop
        async for raw_message in websocket:
            log.info(f"Received message from {username}: {raw_message}")
            # ======================
            # SUBSCRIBE COMMAND
            # ======================
            if raw_message.startswith("SUBSCRIBE:"):
                # Concept: Pub/Sub Pattern
                # Client expresses interest in a channel
                channel = raw_message.split(":")[1]
                if not channel.isalnum(): # Basic validation
                    await websocket.send(f"ERROR:400:Invalid channel name")
                    continue

                # Store subscription with identity
                subscribers[channel].add((username, websocket))

                # Concept: Channel/Topic
                # Named pathway for message distribution
                await websocket.send(f"SUB-ACK:{channel}")

                # Optional: Send message history
                for sender, content in channels.get(channel, []):
                    await websocket.send(f"MSG:{channel}:{sender}:{content}")

            # ======================
            # PUBLISH COMMAND
            # ======================
            elif raw_message.startswith("PUBLISH:"):
                # Concept: Message Distribution with Identity
                # Broker receives and forwards messages with sender info
                _, channel, content = raw_message.split(":", 2)

                # Check if subscribed to channel before publishing
                if not any(ws_username == username for ws_username, _ in subscribers[channel]):
                    await websocket.send(f"ERROR:401:Not subscribed to channel")
                    continue

                # Store message with sender info (simple persistence)
                channels[channel].append((username, content))

                # Concept: Fan-out Delivery
                # Send to all subscribers of this channel
                for sub_username, subscriber in subscribers[channel]:
                    try:
                        await subscriber.send(f"MSG:{channel}:{username}:{content}")
                    except Exception as e:
                        log.error(f"Error sending message to {sub_username}: {e}")
                        subscribers[channel].discard((sub_username, subscriber))

            # ======================
            # UNSUBSCRIBE COMMAND
            # ======================
            elif raw_message.startswith("UNSUBSCRIBE:"):
                channel = raw_message.split(":")[1]
                # Find and remove the subscriber entry with this username
                to_remove = None
                for entry in subscribers[channel]:
                    if entry[0] == username:
                        to_remove = entry
                        break

                if to_remove:
                    subscribers[channel].discard(to_remove)
                await websocket.send(f"UNSUB-ACK:{channel}")

    finally:
        # Clean up when connection drops
        # Concept: Connection Management
        username = client_identities.pop(websocket, None)
        if username:
            log.info(f"Client disconnected: {username}")
            # Remove from all subscriber lists
            for channel in subscribers:
                to_remove = []
                for entry in subscribers[channel]:
                    if entry[0] == username:
                        to_remove.append(entry)
                for entry in to_remove:
                    subscribers[channel].discard(entry)

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
