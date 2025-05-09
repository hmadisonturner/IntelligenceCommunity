# Go Agent for Messaging Platform

This directory contains a Go implementation of an agent that connects to the messaging platform.

## Features

- Connect to the messaging platform with WebSocket
- Receive identity from the broker
- Subscribe to channels
- Publish messages to channels
- Generate and publish sample sales reports
- Process incoming messages

## Requirements

- Go 1.15 or newer
- Gorilla WebSocket library

## Installation

```bash
# Navigate to the directory
cd agents/go

# Get dependencies
go mod download
```

## Usage

To run the agent:

```bash
go run agent.go
```

This will:
1. Connect to the messaging server at `ws://localhost:8765`
2. Subscribe to the `daily-reports` channel
3. Generate and publish a random sales report
4. Listen for incoming messages until interrupted

## Customization

You can modify the agent to:

- Connect to a different server by changing the URL in `NewAgent()`
- Subscribe to different channels
- Generate different types of reports
- Implement more sophisticated message processing

## Implementation Details

The agent follows the same protocol as the Python agent and any other client of the messaging system:

1. Connect to the WebSocket server
2. Receive identity (`IDENTITY:<username>`)
3. Receive available channels (`CHANNELS:<channel1>,<channel2>,...`)
4. Subscribe to channels (`SUBSCRIBE:<channel>`)
5. Publish messages (`PUBLISH:<channel>:<message>`)
6. Process incoming messages