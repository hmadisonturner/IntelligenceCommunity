## Key Concept-Implementation Mappings

1. **Pub/Sub Pattern**:
   - `subscribers` dictionary tracks channel subscriptions
   - `PUBLISH:` commands trigger fan-out to all subscribers

2. **Message Broker**:
   - Central `handle_client` coroutine manages all routing
   - Maintains complete channel and subscriber state

3. **WebSocket Characteristics**:
   - Persistent connection via `async for message in websocket`
   - Full-duplex: client can send/receive simultaneously

4. **Channel/Topic System**:
   - Simple string-based channels (`general`, `news`, etc.)
   - Flexible subscription model with `SUBSCRIBE:` commands

5. **Delivery Semantics**:
   - Currently "at-most-once" delivery
   - No persistence if client disconnects (could be enhanced)


