# Intelligence Community Demo

This document guides you through running the multi-agent demonstration of the Intelligence Community platform.

## Overview

The demo showcases three specialized agents collaborating through a shared messaging infrastructure:

1. **SalesReportBot** (Python) - Generates daily sales figures across departments
2. **MarketAnalysisBot** (Go) - Provides competitor analysis and market trends
3. **ExecutiveSummaryBot** (Python/Claude API) - Synthesizes reports into executive insights

This demonstrates the core concept of the Intelligence Community: humans and automated systems operating as equal participants in an information ecosystem.

## Prerequisites

- Python 3.7+ installed
- Go 1.18+ installed
- [Anthropic API key](https://www.anthropic.com/) (for Claude integration)

### Required Python packages:

```bash
pip install websockets anthropic
```

### Required Go packages:

```bash
cd agents/go
go mod download github.com/gorilla/websocket
```

## Running the Demo

### 1. Set your Anthropic API key

The Claude agent requires an API key to function. Set it as an environment variable:

```bash
# Linux/macOS
export ANTHROPIC_API_KEY=your_api_key_here

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "your_api_key_here"
```

### 2. Run the demo script

Execute the demo script from the `agents/python` directory:

```bash
cd agents/python
python demo.py
```

The script will:
- Start the messaging broker
- Run each agent in sequence
- Show the progress of data generation and synthesis
- Provide instructions for viewing the results

### 3. View the results

Once the demo completes, open the web client to see the messages in each channel:

1. Open `messaging/client/index.html` in your browser
2. Join the following channels to see the different reports:
   - `dailyreports` - Sales data from the Python agent
   - `marketanalysis` - Competitive analysis from the Go agent
   - `executive` - AI-synthesized summary from the Claude agent

## Understanding the Demo

### Agent Architecture

Each agent follows the same pattern:
1. Connect to the message broker
2. Subscribe to relevant channels
3. Publish specialized information
4. Process messages (for the Claude agent)

### Information Flow

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ SalesReportBot │     │MarketAnalysisBot│    │ExecutiveSummaryBot│
└───────┬────────┘     └────────┬───────┘     └─────────┬──────┘
        │                       │                       │
        ▼                       ▼                       ▼
    dailyreports          marketanalysis           executive
        channel              channel               channel
        │                       │                       ▲
        │                       │                       │
        └───────────────┬───────┘                       │
                        │                               │
                        ▼                               │
                  ┌───────────┐                         │
                  │Claude Agent│─────────────────────────┘
                  │(Synthesis) │
                  └───────────┘
```

### What to Look For

1. **Channel Specialization** - Each agent publishes to its own topical channel
2. **Cross-Channel Monitoring** - The Claude agent subscribes to both report channels
3. **Information Synthesis** - Raw data is transformed into strategic insights
4. **Message Protocol** - All agents use the same underlying messaging protocol

## Agent Details

### SalesReportBot (Python)

- Generates random sales data across departments
- Simple example of a reporting agent
- Source: `agents/python/agent.py`

### MarketAnalysisBot (Go)

- Produces market share and competitor analysis
- Demonstrates cross-language agent implementation
- Source: `agents/go/agent.go`

### ExecutiveSummaryBot (Python/Claude)

- Monitors other agents' channels
- Collects and stores report information
- Uses Claude API to synthesize insights
- Publishes executive-ready summary
- Source: `agents/python/claude_agent.py`

## Extending the Demo

Here are some ways to extend this demo:

1. **Create a Human Agent** - Use the web client to join the conversation as a human agent
2. **Add a Query Agent** - Build an agent that responds to specific questions about the data
3. **Create a Visualization Agent** - Generate graphs based on the sales and market data
4. **Add Real Data Sources** - Connect to APIs for actual market and sales data
5. **Build a Notification Agent** - Create alerts based on specific thresholds or conditions

## Troubleshooting

### Common Issues

1. **Broker Connection Problems**
   - Ensure no other service is using port 8765
   - Check that the broker is running (`python messaging/server/broker.py`)

2. **Claude API Issues**
   - Verify your API key is set correctly
   - Check your API usage limits/quotas
   - Ensure your network allows connections to Anthropic's API

3. **Go Agent Errors**
   - Ensure Go is installed and in your PATH
   - Try building the Go agent explicitly: `cd agents/go && go build`
   - Check the Go dependencies are installed correctly

4. **Agent Communication Failures**
   - Confirm each agent shows successful connection messages
   - Verify channel names match exactly (case-sensitive)
   - Check that each agent subscribes before publishing

### Getting Help

If you encounter problems, check:
- The broker console output for connection issues
- Individual agent outputs for specific errors
- API response codes for Claude integration problems

## Conclusion

This demo illustrates the power of the Intelligence Community concept - multiple specialized agents (human and automated) working together through a common messaging framework to produce insights no single agent could provide alone.

By experimenting with this platform, you can explore patterns for agent collaboration, information synthesis, and human-machine teamwork that form the foundation of effective intelligence systems.