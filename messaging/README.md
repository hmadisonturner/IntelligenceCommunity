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

---

## **🚀 Quick Start**  

### **1. Install Dependencies**  
```bash
sudo apt install python3-websockets  # Debian/Ubuntu
pip install websockets asyncio       # Other OS
```

### **2. Run the Message Broker**  
```bash
python3 broker.py
```
> **Broker starts at:** `ws://localhost:8765`  

### **3. Open the Web Client**  
Open `client.html` in multiple browser windows to test messaging.  

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

---

## **🔍 How It Works**  

### **📡 Broker Internals** (`broker.py`)  
```python
# 1. Stores messages per channel
channels = defaultdict(list)  # e.g., {"news": ["Hello!", "Breaking!"]}

# 2. Tracks active subscribers
subscribers = defaultdict(set)  # e.g., {"news": {websocket1, websocket2}}

# 3. Handles incoming messages
async def handle_client(websocket, path):
    if message.startswith("SUBSCRIBE:"):
        subscribers[channel].add(websocket)  # Add to subscription list
    elif message.startswith("PUBLISH:"):
        for subscriber in subscribers[channel]:  # Fan-out to subscribers
            await subscriber.send(f"MSG:{channel}:{content}")
```

### **💻 Web Client** (`client.html`)  
```javascript
let ws = new WebSocket("ws://localhost:8765");

// Subscribe to a channel
ws.send("SUBSCRIBE:news");  

// Publish a message
ws.send("PUBLISH:news:Hello world!");
```

---

## **📈 Extending the Project**  

### **🔹 Add Message Persistence**  
```python
# Replace defaultdict with SQLite
import sqlite3
db = sqlite3.connect("messages.db")
db.execute("CREATE TABLE IF NOT EXISTS messages (channel TEXT, content TEXT)")
```

### **🔹 Multiple Brokers (Federation)**  
- Brokers can forward messages to each other  
- Use a **topic exchange pattern** (e.g., `PUBLISH:news@broker2`)  

### **🔹 Authentication**  
```python
# Add simple auth
if message.startswith("AUTH:"):
    if validate_token(message.split(":")[1]):
        authenticated = True
```

---

## **📚 Learn More**  
- **[WebSocket RFC](https://tools.ietf.org/html/rfc6455)** (Protocol specs)  
- **[Redis Pub/Sub](https://redis.io/topics/pubsub)** (Production-grade messaging)  
- **[MQTT](https://mqtt.org/)** (IoT-focused messaging)  

---

## **🎯 Final Challenge**  
**Modify the broker to:**  
1. Store messages **even if no subscribers exist**  
2. Add **typing indicators** (e.g., `USER_TYPING:general`)  
3. Support **private messages** (`PUBLISH:@user2:Hi there!`)  

---

**🌟 Happy Coding!**  
Try breaking, improving, and scaling this toy system.  
When you’re ready, explore **Kafka, RabbitMQ, or NATS** for production systems!

