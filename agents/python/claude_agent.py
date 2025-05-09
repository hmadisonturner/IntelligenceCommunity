"""
ClaudeAgent for the Intelligence Community
------------------------------------------

This agent monitors sales and market analysis channels, collects reports,
and uses Claude AI to synthesize an executive summary with key insights
and recommendations.

The agent demonstrates:
1. Subscribing to multiple channels
2. Collecting and storing information from other agents
3. Using an AI service to process and synthesize information
4. Publishing synthesized content to an executive channel
"""

import asyncio
import os
import json
import time
import re
from datetime import datetime

import anthropic
import websockets

from agent import Agent

class ClaudeAgent(Agent):
    """
    An agent that uses Claude to synthesize information from multiple sources.
    
    Concept: Multi-Agent Data Synthesis
    - Collects data from multiple agent sources
    - Uses AI to process and extract insights
    - Distributes synthesized information to decision makers
    """
    
    def __init__(
            self, 
            api_key=None, 
            claude_model="claude-3-opus-20240229", 
            exec_channel="executive", 
            source_channels=None,
            **kwargs
        ):
        """Initialize the Claude agent with API credentials and configuration."""
        super().__init__(**kwargs)
        
        # Claude API settings
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Claude API key is required. Set ANTHROPIC_API_KEY environment variable.")
        
        self.claude_model = claude_model
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Messaging configuration
        self.exec_channel = exec_channel
        self.source_channels = source_channels or ["dailyreports", "marketanalysis"]
        
        # Data collection
        self.collected_reports = {
            "sales": [],
            "market": []
        }
        self.last_synthesis_time = 0
        self.synthesis_interval = 60  # seconds between syntheses
    
    async def collect_reports(self):
        """
        Subscribe to all source channels and collect reports.
        
        Concept: Information Gathering
        - Agent subscribes to multiple information sources
        - Stores and categorizes incoming data
        """
        # Connect if not already connected
        if not hasattr(self, 'websocket'):
            await self.connect()
        
        # Subscribe to all data source channels
        for channel in self.source_channels:
            await self.subscribe(channel)
        
        # Subscribe to executive channel for posting
        await self.subscribe(self.exec_channel)
        
        print(f"Collecting reports from channels: {self.source_channels}")
    
    async def process_message(self, message):
        """
        Process incoming messages from the subscribed channels.
        
        Concept: Message Filtering and Storage
        - Categorizes messages by source and content
        - Maintains relevant context for synthesis
        """
        if not message.startswith("MSG:"):
            return False
        
        # Parse the message
        _, channel, sender, content = message.split(":", 3)
        
        # Store messages by channel/type
        if channel == "dailyreports" and "DAILY SALES REPORT" in content:
            print(f"Collected sales report from {sender}")
            self.collected_reports["sales"].append({
                "sender": sender,
                "timestamp": datetime.now().isoformat(),
                "content": content
            })
            return True
            
        elif channel == "marketanalysis" and "MARKET ANALYSIS REPORT" in content:
            print(f"Collected market analysis from {sender}")
            self.collected_reports["market"].append({
                "sender": sender,
                "timestamp": datetime.now().isoformat(),
                "content": content
            })
            return True
            
        return False
    
    def _extract_key_data(self):
        """
        Extract and structure key data from collected reports.
        
        Concept: Data Extraction
        - Pulls structured information from semi-structured text
        - Prepares data for synthesis
        """
        structured_data = {}
        
        # Process sales reports
        if self.collected_reports["sales"]:
            # Use the most recent sales report
            latest_sales = self.collected_reports["sales"][-1]["content"]
            
            # Extract total sales
            total_sales_match = re.search(r'Total Sales: \$(\d+)', latest_sales)
            if total_sales_match:
                structured_data["total_sales"] = total_sales_match.group(1)
            
            # Extract department data
            structured_data["departments"] = {}
            dept_matches = re.finditer(r'• (\w+): \$(\d+) \((\d+) transactions\)', latest_sales)
            for match in dept_matches:
                dept, sales, transactions = match.groups()
                structured_data["departments"][dept] = {
                    "sales": sales,
                    "transactions": transactions
                }
        
        # Process market reports
        if self.collected_reports["market"]:
            # Use the most recent market report
            latest_market = self.collected_reports["market"][-1]["content"]
            
            # Extract market size and share
            market_size_match = re.search(r'Total Market Size: \$(\d+) million', latest_market)
            if market_size_match:
                structured_data["market_size"] = market_size_match.group(1) + "M"
                
            market_share_match = re.search(r'Our Market Share: ([\d\.]+)%', latest_market)
            if market_share_match:
                structured_data["market_share"] = market_share_match.group(1) + "%"
                
            # Extract competitor data
            structured_data["competitors"] = {}
            competitor_sections = re.finditer(r'🏆 (\w+)\n\s+Market Share: ([\d\.]+)%', latest_market)
            for match in competitor_sections:
                competitor, share = match.groups()
                structured_data["competitors"][competitor] = {
                    "share": share + "%"
                }
                
            # Extract recommendations
            recommendations = []
            rec_matches = re.finditer(r'\d+\. (.+)', latest_market)
            for match in rec_matches:
                recommendations.append(match.group(1))
            
            if recommendations:
                structured_data["recommendations"] = recommendations
        
        return structured_data
    
    async def synthesize_reports(self):
        """
        Use Claude to synthesize collected reports into an executive summary.
        
        Concept: AI-Powered Synthesis
        - Combines multiple data sources into coherent analysis
        - Extracts key insights and actionable recommendations
        - Formats output for executive consumption
        """
        # Check if we have enough data and if enough time has passed
        current_time = time.time()
        if (
            not self.collected_reports["sales"] or 
            not self.collected_reports["market"] or
            current_time - self.last_synthesis_time < self.synthesis_interval
        ):
            return None
            
        self.last_synthesis_time = current_time
        
        # Extract structured data for context
        key_data = self._extract_key_data()
        
        # Prepare the prompt
        sales_report = self.collected_reports["sales"][-1]["content"]
        market_report = self.collected_reports["market"][-1]["content"]
        
        prompt = f"""
You are an executive assistant preparing a concise summary of sales and market analysis reports for C-level executives.

Here are the raw reports:

---SALES REPORT---
{sales_report}

---MARKET ANALYSIS---
{market_report}

Create a concise executive summary with the following sections:
1. Key Performance Indicators (2-3 bullet points)
2. Market Position (2-3 bullet points)
3. Critical Insights (3-4 bullet points)
4. Strategic Recommendations (3-4 bullet points)

Format the summary in a professional, concise manner suitable for executives.
Focus on actionable insights and strategic implications.
Total length should be around 300-400 words.
"""

        # Get synthesis from Claude
        try:
            print("Requesting synthesis from Claude...")
            response = self.client.messages.create(
                model=self.claude_model,
                max_tokens=1000,
                temperature=0.2,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            synthesis = response.content[0].text
            print("Received synthesis from Claude")
            
            # Format the executive summary with timestamp and attribution
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            executive_summary = f"""
📋 EXECUTIVE SUMMARY: {datetime.now().strftime("%Y-%m-%d")}
⏱️ Generated: {current_time}

{synthesis}

---
This summary was synthesized by ClaudeAgent from reports by:
- Sales data from {self.collected_reports["sales"][-1]["sender"]}
- Market analysis from {self.collected_reports["market"][-1]["sender"]}
"""
            return executive_summary
            
        except Exception as e:
            print(f"Error getting synthesis from Claude: {e}")
            return None
    
    async def run(self, run_once=False):
        """
        Main agent loop - collect reports, synthesize, and publish.
        
        Concept: Autonomous Agent Behavior
        - Continuous monitoring and processing
        - Periodic synthesis and distribution
        """
        # Ensure we're connected and subscribed
        await self.collect_reports()
        
        print(f"ClaudeAgent running, monitoring {self.source_channels}")
        print(f"Will publish synthesized reports to '{self.exec_channel}' channel")
        
        # Message processing loop
        try:
            while True:
                # Check if we should synthesize and publish
                executive_summary = await self.synthesize_reports()
                if executive_summary:
                    print(f"Publishing executive summary to {self.exec_channel}")
                    await self.publish(self.exec_channel, executive_summary)
                    
                    # If run_once flag is set, exit after publishing
                    if run_once:
                        break
                
                # Process any new messages
                try:
                    # Set a timeout to allow for periodic synthesis checks
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
                    report_processed = await self.process_message(message)
                    
                    # Print received message if it wasn't a report we processed
                    if not report_processed:
                        print(f"Received: {message}")
                        
                except asyncio.TimeoutError:
                    # This is expected - allows us to check for synthesis periodically
                    pass
                    
        except Exception as e:
            print(f"Error in agent run loop: {e}")
        finally:
            # Clean up
            await self.close()
            print("ClaudeAgent shut down")

async def main():
    """Run the Claude agent."""
    # Create the agent
    claude_agent = ClaudeAgent(
        agent_name="ExecutiveSummaryBot",
        exec_channel="executive"
    )
    
    try:
        # Run the agent (run_once=True for testing)
        await claude_agent.run(run_once=False)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await claude_agent.close()

if __name__ == "__main__":
    asyncio.run(main())