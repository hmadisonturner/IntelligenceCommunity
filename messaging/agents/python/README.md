# Python Agent for Messaging Platform

This directory contains a Python implementation of an agent framework for the messaging platform.

## Features

- Base `Agent` class that handles all messaging protocol details
- Specialized `ReportBot` class demonstrating a concrete agent implementation
- Connection and identity management
- Channel subscription and message publishing
- Asynchronous messaging with WebSockets

## Requirements

- Python 3.7 or newer
- websockets library
- asyncio library

## Installation

```bash
# Install required packages
pip install websockets
```

## Basic Usage

```python
# Import the agent classes
from agent import Agent, ReportBot

# Run the example ReportBot
import asyncio
asyncio.run(ReportBot().post_report())
```

You can also run the agent directly:

```bash
python agent.py
```

This will:
1. Connect to the messaging server at `ws://localhost:8765`
2. Subscribe to the `daily-reports` channel
3. Generate and publish a random sales report

## Creating Custom Agents

To create your own specialized agent:

```python
from agent import Agent
import asyncio

class MyAgent(Agent):
    async def my_custom_behavior(self):
        # Connect to server
        await self.connect()
        
        # Subscribe to a channel
        await self.subscribe("my-channel")
        
        # Send a message
        await self.publish("my-channel", "Hello from my custom agent!")

# Run the agent
async def main():
    agent = MyAgent(agent_name="CustomAgent")
    await agent.my_custom_behavior()
    await agent.close()

asyncio.run(main())
```

## Advanced Usage

The base Agent class can be extended for more complex behaviors:

### Message Processing Agent

```python
class ProcessingAgent(Agent):
    async def process_messages(self):
        await self.connect()
        await self.subscribe("requests")
        
        async def message_handler(agent, message):
            if message.startswith("MSG:requests:"):
                _, channel, sender, content = message.split(":", 3)
                response = f"Processed: {content}"
                await agent.publish("responses", response)
        
        await self.receive_messages(handler=message_handler)
```

### Scheduled Agent

```python
# Use with a scheduler like APScheduler
def run_daily_report():
    asyncio.run(ReportBot().post_report())
    
# In your scheduler configuration:
scheduler.add_job(run_daily_report, 'cron', hour=8)
```

## Implementation Details

The agent follows the messaging protocol:

1. Connect to WebSocket server
2. Receive identity (`IDENTITY:<username>`)
3. Receive available channels (`CHANNELS:<channel1>,<channel2>,...`)
4. Subscribe to channels (`SUBSCRIBE:<channel>`)
5. Publish messages (`PUBLISH:<channel>:<message>`)
6. Process incoming messages