"""
Demo Script for Intelligence Community System
---------------------------------------------

This script demonstrates the complete workflow of multiple agents working together:

1. Python ReportBot (Sales Data Generator)
2. Go MarketAnalysisBot (Market & Competitor Analysis)
3. Claude Agent (Executive Summary Generator)

Run this script to see how multiple agents can collaborate through the messaging system.
"""

import asyncio
import os
import subprocess
import sys
import time
from agent import ReportBot
from claude_agent import ClaudeAgent

async def start_broker():
    """Start the message broker in a subprocess."""
    print("📡 Starting message broker...")
    broker_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "messaging", "server", "broker.py")
    
    broker_process = subprocess.Popen(
        [sys.executable, broker_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    # Give the broker time to start
    await asyncio.sleep(2)
    return broker_process

async def run_sales_agent():
    """Run the Python sales reporting agent."""
    print("🔢 Starting Sales Report Agent...")
    sales_bot = ReportBot(agent_name="SalesReportBot")
    await sales_bot.connect()
    await sales_bot.post_report()
    await sales_bot.close()
    print("✅ Sales report posted")

async def run_market_agent():
    """Run the Go market analysis agent."""
    print("📊 Starting Market Analysis Agent...")
    go_agent_path = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "go")
    
    # Make sure the Go agent is properly compiled
    try:
        go_process = subprocess.run(
            ["go", "run", "agent.go"],
            cwd=go_agent_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        if go_process.returncode != 0:
            print(f"⚠️ Go agent error: {go_process.stderr}")
        else:
            print("✅ Market analysis posted")
    except subprocess.TimeoutExpired:
        print("⚠️ Go agent timed out")
    except Exception as e:
        print(f"⚠️ Error running Go agent: {e}")

async def run_claude_agent():
    """Run the Claude synthesis agent."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️ ANTHROPIC_API_KEY not set, Claude agent will not run")
        print("   Set this environment variable to enable the executive summary")
        return

    print("🧠 Starting Claude Executive Summary Agent...")
    claude_bot = ClaudeAgent(agent_name="ExecutiveSummaryBot")
    await claude_bot.connect()
    
    # Subscribe to data sources and executive channel
    for channel in ["dailyreports", "marketanalysis", "executive"]:
        await claude_bot.subscribe(channel)
    
    # Wait for reports to be collected
    print("👂 Listening for reports...")
    listening_time = 0
    sales_found = False
    market_found = False
    
    while listening_time < 30 and not (sales_found and market_found):
        await asyncio.sleep(1)
        listening_time += 1
        
        if claude_bot.collected_reports["sales"] and not sales_found:
            print("📝 Sales report collected")
            sales_found = True
            
        if claude_bot.collected_reports["market"] and not market_found:
            print("📝 Market report collected")
            market_found = True
    
    if sales_found and market_found:
        # Generate and publish executive summary
        print("💭 Generating executive summary...")
        summary = await claude_bot.synthesize_reports()
        if summary:
            await claude_bot.publish("executive", summary)
            print("✅ Executive summary posted to 'executive' channel")
        else:
            print("⚠️ Failed to generate executive summary")
    else:
        missing = []
        if not sales_found:
            missing.append("sales report")
        if not market_found:
            missing.append("market analysis")
        print(f"⚠️ Did not receive {' and '.join(missing)} within timeout period")
    
    # Close the connection
    await claude_bot.close()

async def main():
    """Run the complete demo with all agents."""
    print("=" * 50)
    print("Intelligence Community Agent Demo")
    print("=" * 50)
    
    # Check for Claude API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n⚠️  Warning: ANTHROPIC_API_KEY environment variable not set.")
        print("   The Claude Executive Summary Agent will be skipped.\n")
    
    # Start the broker
    broker_process = await start_broker()
    
    try:
        print("\n📣 Starting multi-agent demonstration...\n")
        
        # Wait a moment for the broker to initialize fully
        await asyncio.sleep(2)
        
        # Run the sales agent
        await run_sales_agent()
        
        # Short pause between agents
        await asyncio.sleep(1)
        
        # Run the market analysis agent
        await run_market_agent()
        
        # Short pause to ensure reports are processed
        await asyncio.sleep(2)
        
        # Run the Claude agent to generate an executive summary
        if os.environ.get("ANTHROPIC_API_KEY"):
            await run_claude_agent()
        
        print("\n🎉 Demo complete! The following channels have been populated:")
        print("  - 'dailyreports': Sales data from Python ReportBot")
        print("  - 'marketanalysis': Competitive analysis from Go MarketAnalysisBot")
        if os.environ.get("ANTHROPIC_API_KEY"):
            print("  - 'executive': AI-synthesized summary from ClaudeAgent")
        
        print("\n💡 To see these messages, open the web client at:")
        print("   messaging/client/index.html in your browser\n")
        
    finally:
        # Clean up - terminate the broker
        print("🛑 Shutting down broker...")
        broker_process.terminate()
        broker_process.wait()
        print("✅ Broker shut down")
        print("\n" + "=" * 50)
        print("Demo finished. Thank you for exploring the Intelligence Community!")
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())