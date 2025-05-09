### **Messaging Protocol Specification**  
**Version 1.0** – Simple Pub/Sub with Identity  

This defines the **exact message formats** for client-broker communication. All messages are plaintext over WebSocket, with colon-separated fields.

---

## **📜 Protocol Definitions**

### **1. Connection Initiation**
- **Broker → Client** (on connect):
  `IDENTITY:<username>`
  ```python
  # Broker assigns random ID
  await websocket.send(f"IDENTITY:user-{uuid.uuid4()[:8]}")
  ```

- **Broker → Client** (on connect, after identity):
  `CHANNELS:<channel1>,<channel2>,...`
  ```python
  # Broker sends available channels
  await websocket.send(f"CHANNELS:{','.join(active_channels)}")
  ```

---

### **2. Subscription Control**
| Direction       | Format                      | Example                     | Description                     |
|-----------------|----------------------------|-----------------------------|---------------------------------|
| **Client → Broker** | `SUBSCRIBE:<channel>`      | `SUBSCRIBE:news`            | Subscribe to a channel          |
| **Broker → Client** | `SUB-ACK:<channel>`        | `SUB-ACK:news`              | Subscription confirmed          |
| **Client → Broker** | `UNSUBSCRIBE:<channel>`    | `UNSUBSCRIBE:news`          | Leave a channel                 |
| **Broker → Client** | `UNSUB-ACK:<channel>`      | `UNSUB-ACK:news`            | Unsubscription confirmed        |

---

### **3. Message Publishing**
| Direction       | Format                                  | Example                             |
|-----------------|----------------------------------------|-------------------------------------|
| **Client → Broker** | `PUBLISH:<channel>:<message>`         | `PUBLISH:news:Hello world!`        |
| **Broker → Client** | `MSG:<channel>:<sender>:<message>`    | `MSG:news:alice@123:Hello world!`  |

---

### **4. Error Messages (Broker → Client)**
| Format                      | Example                     | Trigger Condition               |
|----------------------------|-----------------------------|---------------------------------|
| `ERROR:<code>:<details>`   | `ERROR:401:Not subscribed`  | Client tries to publish to unsubscribed channel |

---

## **🌐 Reference Implementations**

### **Python (Broker)**
```python
# Handling publish
async for message in websocket:
    if message.startswith("PUBLISH:"):
        _, channel, content = message.split(":", 2)
        for (sub_user, sub_ws) in subscribers[channel]:  # Fan-out
            await sub_ws.send(f"MSG:{channel}:{username}:{content}")
```

### **JavaScript (Client)**
```javascript
// Sending a message
function publish() {
    const message = input.value;
    ws.send(`PUBLISH:${currentChannel}:${message}`);
}

// Receiving messages
ws.onmessage = (event) => {
    const [type, channel, sender, content] = event.data.split(":", 3);
    if (type === "MSG") {
        console.log(`${sender}@${channel}: ${content}`);
    }
};
```

### **Go (Future Client)**
```go
// Example send in Go
conn.WriteMessage(websocket.TextMessage, []byte("SUBSCRIBE:news"))

// Receiving
_, msg, _ := conn.ReadMessage()
parts := strings.Split(string(msg), ":")
if parts[0] == "MSG" {
    fmt.Printf("%s@%s: %s\n", parts[2], parts[1], parts[3])
}
```

---

## **🔍 Protocol Rules**
1. **Field Separation**: Colons (`:`) delimit fields  
2. **No Spaces**: Avoid spaces in channels/usernames (`news` not `general chat`)  
3. **Case-Sensitive**: `News ≠ news`  
4. **Error Handling**: Unknown messages should be ignored (for forward compatibility)  

---

## **📈 Extensions (Future-Proofing)**
1. **Metadata Support**  
   `PUBLISH:news:Hello!||timestamp=1234567890`  
2. **Binary Data**  
   Base64-encoded payloads: `PUBLISH:images:${btoa(imageData)}`  
3. **Compression**  
   Add `COMPRESS:1` header for zlib-compressed messages  

