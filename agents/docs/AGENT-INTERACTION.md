# Agent-Human Interaction Patterns

This document outlines common interaction patterns between automated agents and human users within our messaging system.

## Basic Interaction Flow

```mermaid
sequenceDiagram
    participant H as Human User (Browser)
    participant B as Message Broker
    participant A as Agent (Python/Go)
    
    A->>B: Connect to WebSocket
    B->>A: IDENTITY:agent-123
    B->>A: CHANNELS:general,reports
    
    H->>B: Connect to WebSocket
    B->>H: IDENTITY:user-456
    B->>H: CHANNELS:general,reports
    
    A->>B: SUBSCRIBE:reports
    B->>A: SUB-ACK:reports
    
    H->>B: SUBSCRIBE:reports
    B->>H: SUB-ACK:reports
    
    A->>B: PUBLISH:reports:Daily Sales Report...
    B->>A: MSG:reports:agent-123:Daily Sales Report...
    B->>H: MSG:reports:agent-123:Daily Sales Report...
    
    H->>B: PUBLISH:reports:How does this compare to yesterday?
    B->>H: MSG:reports:user-456:How does this compare to yesterday?
    B->>A: MSG:reports:user-456:How does this compare to yesterday?
```

## Common Interaction Patterns

### 1. Scheduled Reporting

```mermaid
sequenceDiagram
    participant C as Cron Job
    participant A as Report Agent
    participant B as Message Broker
    participant H as Human Users
    
    C->>A: Trigger daily (8:00 AM)
    A->>B: Connect
    B->>A: IDENTITY:reporter-789
    A->>B: SUBSCRIBE:daily-reports
    A->>B: PUBLISH:daily-reports:Sales Report
    B->>H: MSG:daily-reports:reporter-789:Sales Report
    H->>B: PUBLISH:daily-reports:Thanks for the report!
    B->>A: MSG:daily-reports:user-123:Thanks for the report!
    A->>B: Close connection
```

### 2. Query-Response

```mermaid
sequenceDiagram
    participant H as Human User
    participant B as Message Broker
    participant A as Query Agent
    
    Note over A: Long-running connection
    
    A->>B: Connect
    B->>A: IDENTITY:query-bot
    A->>B: SUBSCRIBE:questions
    
    H->>B: Connect
    B->>H: IDENTITY:user-123
    H->>B: SUBSCRIBE:questions
    
    H->>B: PUBLISH:questions:@query-bot What's our top selling product?
    B->>H: MSG:questions:user-123:@query-bot What's our top selling product?
    B->>A: MSG:questions:user-123:@query-bot What's our top selling product?
    
    Note over A: Process query
    
    A->>B: PUBLISH:questions:@user-123 The top product is "Widgets" with 1,245 units
    B->>A: MSG:questions:query-bot:@user-123 The top product is "Widgets" with 1,245 units
    B->>H: MSG:questions:query-bot:@user-123 The top product is "Widgets" with 1,245 units
```

### 3. Multi-Agent Collaboration

```mermaid
sequenceDiagram
    participant H as Human User
    participant B as Message Broker
    participant A1 as Data Agent
    participant A2 as Analysis Agent
    
    H->>B: PUBLISH:projects:Need sales forecast for Q3
    
    B->>A1: MSG:projects:user-123:Need sales forecast for Q3
    B->>A2: MSG:projects:user-123:Need sales forecast for Q3
    
    A1->>B: PUBLISH:projects:@analysis-bot I'll provide historical data
    B->>A2: MSG:projects:data-bot:@analysis-bot I'll provide historical data
    
    A1->>B: PUBLISH:projects:Here's the Q1-Q2 data: {...}
    B->>A2: MSG:projects:data-bot:Here's the Q1-Q2 data: {...}
    
    A2->>B: PUBLISH:projects:@user-123 Based on the data, Q3 forecast is $1.2M
    B->>H: MSG:projects:analysis-bot:@user-123 Based on the data, Q3 forecast is $1.2M
```

## Implementing Agent Behaviors

### How Agents Recognize Commands

Agents can listen for specific patterns in messages:

```python
async def message_handler(agent, message):
    if message.startswith("MSG:"):
        _, channel, sender, content = message.split(":", 3)
        
        # Check for direct mention
        if content.startswith(f"@{agent.identity}"):
            command = content.split(" ", 1)[1]
            # Process command...
            
        # Look for specific keywords
        elif "report" in content.lower() and "generate" in content.lower():
            # Generate report...
```

### Agent Response Strategies

1. **Immediate Response**: Respond directly to the channel where the query was made
2. **Direct Message**: Send a response to a user-specific channel
3. **Broadcast**: Send information to all subscribers of a channel
4. **Staged Response**: Send acknowledgment first, then follow up with complete response

## Best Practices

### For Human-Agent Interaction

1. **Clear Command Structure**: Use consistent patterns like `@agent-name command`
2. **Help Commands**: Agents should recognize `help` to explain their capabilities
3. **Feedback Loop**: Agents should acknowledge command receipt before processing
4. **Status Updates**: For long-running tasks, provide progress reports
5. **Graceful Failures**: Clearly communicate when requests cannot be fulfilled

### For Agent Implementation

1. **Focused Purpose**: Each agent should have a clear, specific responsibility
2. **Meaningful Identity**: Agent names should reflect their function
3. **Stateless When Possible**: Minimize persistent state between interactions
4. **Respect Channels**: Only send messages relevant to the channel's purpose
5. **Rate Limiting**: Avoid flooding channels with messages