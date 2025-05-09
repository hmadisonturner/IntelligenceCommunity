"""
Basic Agent Framework for Messaging System

This module provides a simple framework for creating automated agents
that connect to the messaging system.
"""

import asyncio
import json
import random
import websockets
from datetime import datetime

class Agent:
    """
    Base Agent class for the messaging system.
    
    Concept: Agent Abstraction
    - Encapsulates the messaging protocol details
    - Provides simple methods for agent functionality
    - Handles connection and identity management
    """
    
    def __init__(self, broker_url="ws://localhost:8765", agent_name="GenericAgent"):
        """Initialize the agent with connection settings."""
        self.broker_url = broker_url
        self.agent_name = agent_name
        self.identity = None
        self.available_channels = []
        self.subscribed_channels = set()
    
    async def connect(self):
        """
        Connect to the message broker and receive identity.
        
        Concept: Connection Management
        - Establishes WebSocket connection
        - Processes identity assignment
        - Receives available channels
        """
        self.websocket = await websockets.connect(self.broker_url)
        
        # Receive and process identity
        identity_msg = await self.websocket.recv()
        if identity_msg.startswith("IDENTITY:"):
            self.identity = identity_msg.split(":")[1]
            print(f"Connected as: {self.identity}")
        else:
            raise Exception(f"Unexpected response: {identity_msg}")
        
        # Receive available channels
        channels_msg = await self.websocket.recv()
        if channels_msg.startswith("CHANNELS:"):
            channels = channels_msg.split(":")[1]
            self.available_channels = channels.split(",") if channels else []
            print(f"Available channels: {self.available_channels}")
    
    async def subscribe(self, channel):
        """
        Subscribe to a channel to receive messages.
        
        Concept: Channel Subscription
        - Agents join specific channels of interest
        - Enables topical message filtering
        """
        await self.websocket.send(f"SUBSCRIBE:{channel}")
        response = await self.websocket.recv()
        
        if response.startswith("SUB-ACK:"):
            self.subscribed_channels.add(channel)
            print(f"Subscribed to: {channel}")
            return True
        else:
            print(f"Failed to subscribe: {response}")
            return False
    
    async def publish(self, channel, message):
        """
        Publish a message to a channel.
        
        Concept: Message Distribution
        - Agents communicate by publishing to channels
        - Messages distributed to all subscribers
        """
        if channel not in self.subscribed_channels:
            await self.subscribe(channel)
            
        await self.websocket.send(f"PUBLISH:{channel}:{message}")
        
        # Wait for the message to be echoed back as confirmation
        while True:
            response = await self.websocket.recv()
            if response.startswith("MSG:"):
                _, msg_channel, sender, content = response.split(":", 3)
                if sender == self.identity and channel == msg_channel:
                    print(f"Message published to {channel}")
                    return True
    
    async def receive_messages(self, handler=None):
        """
        Process incoming messages, optionally with a custom handler.
        
        Concept: Event Handling
        - Agents can process and react to messages
        - Enables interactive behavior
        """
        async for message in self.websocket:
            print(f"Received: {message}")
            
            # Call custom handler if provided
            if handler and callable(handler):
                await handler(self, message)
    
    async def close(self):
        """Close the connection to the broker."""
        await self.websocket.close()
        print(f"Agent {self.identity} disconnected")


class ReportBot(Agent):
    """
    Example agent that generates and publishes reports.
    
    Concept: Specialized Agents
    - Extends base agent with specific functionality
    - Implements domain-specific behavior
    """
    
    def __init__(self, report_channel="dailyreports", **kwargs):
        super().__init__(**kwargs)
        self.report_channel = report_channel
    
    def generate_sales_report(self):
        """Generate a mock sales report with random data."""
        departments = ["Electronics", "Clothing", "Food", "Books"]
        
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_sales": random.randint(5000, 20000),
            "departments": {}
        }
        
        for dept in departments:
            report["departments"][dept] = {
                "sales": random.randint(500, 5000),
                "transactions": random.randint(10, 100)
            }
        
        return report
    
    def format_report(self, report_data):
        """Format the report data as a readable message."""
        report_message = f"""
📊 DAILY SALES REPORT: {report_data['date']}
💰 Total Sales: ${report_data['total_sales']}

Department Breakdown:
{'-' * 30}
"""
        
        # Add each department to the message
        for dept, data in report_data["departments"].items():
            report_message += f"• {dept}: ${data['sales']} ({data['transactions']} transactions)\n"
            
        report_message += f"\nGenerated by {self.agent_name} at {datetime.now().strftime('%H:%M:%S')}"
        
        return report_message
    
    async def post_report(self):
        """Generate and post a report to the designated channel."""
        # Connect if not already connected
        if not hasattr(self, 'websocket'):
            await self.connect()
        
        # Subscribe to report channel if needed
        if self.report_channel not in self.subscribed_channels:
            await self.subscribe(self.report_channel)
        
        # Generate and format the report
        report_data = self.generate_sales_report()
        report_text = self.format_report(report_data)
        
        # Publish the report
        await self.publish(self.report_channel, report_text)
        
        return report_data


# Example usage
async def main():
    """Example of using the ReportBot."""
    # Create and configure the agent
    bot = ReportBot(agent_name="SalesReportBot")
    
    try:
        # Connect to the messaging system
        await bot.connect()
        
        # Post a report
        await bot.post_report()
        
        # Wait briefly to ensure message is processed
        await asyncio.sleep(2)
        
    finally:
        # Clean up
        await bot.close()


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
