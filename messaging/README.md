# **Build Your Own Messaging Network**  
### A hands-on tutorial to understand messaging architectures with Python  

---

## **📌 Overview**  
This project demonstrates a **simple Pub/Sub messaging system** using:  
✅ **Python** (Broker)  
✅ **WebSockets** (Real-time communication)  
✅ **Vanilla JavaScript** (Web Client)  

You'll learn:
- How **message brokers** work
- The **Pub/Sub pattern** in action
- **WebSocket** communication
- Basic **message persistence**
- **Identity management** in messaging systems
- **Service discovery** for dynamic channels

---

## **🚀 Quick Start**  

### **1. Install Dependencies**  
```bash
cd server
pip install -r requirements.txt
```

### **2. Run the Message Broker**  
```bash
python server/broker.py
```
> **Broker starts at:** `ws://localhost:8765`  

### **3. Open the Web Client**  
Open `client/index.html` in multiple browser windows to test messaging.  

---

## **🧠 Core Concepts Explained**  

### **1. Pub/Sub Pattern**  
- **Publishers** send messages to **channels** (e.g., `PUBLISH:news:Hello!`)  
- **Subscribers** receive messages only from channels they joined (`SUBSCRIBE:news`)  

### **2. Message Broker**  
- Acts as a **central post office**  
- Routes messages from senders → receivers  
- Stores messages in memory (`defaultdict`)  

### **3. WebSocket Protocol**  
- **Full-duplex** (simultaneous send/receive)  
- **Persistent connection** (unlike HTTP)  

### **4. Identity System**
- Each client receives a **unique identity** on connection
- Messages are **attributed to senders**
- Enables personalized interactions

### **5. Channel Discovery**
- **Available channels** sent to clients on connection
- **Dynamic updates** when new channels are created
- Enables **service discovery** in distributed systems

---

## **🔍 How It Works**  

### **📡 Broker Internals** (`server/broker.py`)  
```python
# 1. Stores messages per channel with sender info
channels = defaultdict(list)  # e.g., {"news": [("user1", "Hello!"), ("user2", "Breaking!")]}

# 2. Tracks active subscribers with identities
subscribers = defaultdict(set)  # e.g., {"news": {("user1", websocket1), ("user2", websocket2)}}

# 3. Manages client identities
client_identities = {}  # e.g., {websocket1: "user1", websocket2: "user2"}

# 4. Handles incoming messages
async def handle_client(websocket):
    # Assign identity on connection
    username = f"user-{str(uuid.uuid4())[:8]}"
    await websocket.send(f"IDENTITY:{username}")
    
    # Subscribe handler
    if message.startswith("SUBSCRIBE:"):
        subscribers[channel].add((username, websocket))
        
    # Publish handler with identity
    elif message.startswith("PUBLISH:"):
        for sub_username, subscriber in subscribers[channel]:
            await subscriber.send(f"MSG:{channel}:{username}:{content}")
```

### **💻 Web Client** (`client/index.html`)  
```javascript
// Handle identity assignment
if (msg.startsWith("IDENTITY:")) {
  username = msg.split(":")[1];
}

// Receive channel list
if (msg.startsWith("CHANNELS:")) {
  availableChannels = msg.split(":")[1].split(",");
  // Update UI with available channels
}

// Subscribe to a channel
ws.send("SUBSCRIBE:news");

// Publish a message
ws.send("PUBLISH:news:Hello world!");

// Receive messages with sender info
if (msg.startsWith("MSG:")) {
  const [_, channel, sender, content] = msg.split(":", 4);
  // Display message with sender attribution
}
```

---

## **📈 Next Steps & Extensions**  

### **🔹 Add Persistent Storage**  
```python
# Replace defaultdict with SQLite
import sqlite3
db = sqlite3.connect("messages.db")
db.execute("CREATE TABLE IF NOT EXISTS messages (channel TEXT, sender TEXT, content TEXT)")
```

### **🔹 Add Authentication**  
```python
# Add simple auth
if message.startswith("AUTH:"):
    token = message.split(":")[1]
    if validate_token(token):
        authenticated = True
        # Associate authenticated identity
```

### **🔹 Direct Messaging**  
```python
# Private messaging
if message.startswith("DIRECT:"):
    _, recipient, content = message.split(":", 2)
    # Route to specific user rather than channel
```

---

## **📚 Documentation**  
- **[PROTOCOL.md](docs/PROTOCOL.md)** - Detailed message format specifications
- **[FLOW.md](docs/FLOW.md)** - System architecture and data flow diagrams
- **[SUMMARY.md](docs/SUMMARY.md)** - Key concept implementation mappings

---

## **🎯 Challenge Projects**  
**Try extending the system with:**  
1. **User presence indicators** (online/offline status)  
2. **Message delivery confirmations**  
3. **Channel metadata** (topic, member count)  
4. **Message edit/delete functionality**

---

**🌟 Happy Coding!**  
Try breaking, improving, and scaling this toy system.  
When you're ready, explore **Kafka, RabbitMQ, or NATS** for production systems!