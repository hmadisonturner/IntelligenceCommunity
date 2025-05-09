package main

import (
	"fmt"
	"log"
	"math/rand"
	"net/url"
	"os"
	"os/signal"
	"strings"
	"time"

	"github.com/gorilla/websocket"
)

// Agent represents a client that connects to the messaging system
type Agent struct {
	// Connection details
	BrokerURL     string
	AgentName     string
	Identity      string
	Conn          *websocket.Conn
	Subscriptions map[string]bool
	Channels      []string
}

// MarketReport represents competitive market analysis data
type MarketReport struct {
	Date           string                      `json:"date"`
	MarketSize     int                         `json:"market_size"`
	MarketGrowth   float64                     `json:"market_growth"`
	OurMarketShare float64                     `json:"our_market_share"`
	Competitors    map[string]CompetitorData   `json:"competitors"`
	Categories     map[string]CategoryAnalysis `json:"categories"`
}

// CompetitorData contains analysis of a competitor
type CompetitorData struct {
	MarketShare     float64 `json:"market_share"`
	GrowthRate      float64 `json:"growth_rate"`
	PriceComparison string  `json:"price_comparison"`
	Strengths       string  `json:"strengths"`
	Weaknesses      string  `json:"weaknesses"`
}

// CategoryAnalysis contains market analysis for a product category
type CategoryAnalysis struct {
	MarketSize      int     `json:"market_size"`
	MarketShare     float64 `json:"market_share"`
	YearlyTrend     string  `json:"yearly_trend"`
	ConsumerSentiment string `json:"consumer_sentiment"`
}

// NewAgent creates a new agent with the given configuration
func NewAgent(brokerURL, agentName string) *Agent {
	return &Agent{
		BrokerURL:     brokerURL,
		AgentName:     agentName,
		Subscriptions: make(map[string]bool),
	}
}

// Connect establishes a connection to the message broker
func (a *Agent) Connect() error {
	// Parse the URL
	u, err := url.Parse(a.BrokerURL)
	if err != nil {
		return fmt.Errorf("invalid URL: %v", err)
	}

	// Create dialer
	c, _, err := websocket.DefaultDialer.Dial(u.String(), nil)
	if err != nil {
		return fmt.Errorf("dial error: %v", err)
	}
	a.Conn = c

	// Process initial messages from the server (identity and channels)
	err = a.processInitialMessages()
	if err != nil {
		return err
	}

	log.Printf("Agent %s connected as %s", a.AgentName, a.Identity)
	return nil
}

// processInitialMessages handles the identity and channels messages on connection
func (a *Agent) processInitialMessages() error {
	// Receive identity message
	_, identityMsg, err := a.Conn.ReadMessage()
	if err != nil {
		return fmt.Errorf("error reading identity message: %v", err)
	}

	// Process identity
	identityParts := strings.SplitN(string(identityMsg), ":", 2)
	if len(identityParts) != 2 || identityParts[0] != "IDENTITY" {
		return fmt.Errorf("unexpected identity format: %s", identityMsg)
	}
	a.Identity = identityParts[1]
	log.Printf("Received identity: %s", a.Identity)

	// Receive channels message
	_, channelsMsg, err := a.Conn.ReadMessage()
	if err != nil {
		return fmt.Errorf("error reading channels message: %v", err)
	}

	// Process channels
	channelsParts := strings.SplitN(string(channelsMsg), ":", 2)
	if len(channelsParts) != 2 || channelsParts[0] != "CHANNELS" {
		return fmt.Errorf("unexpected channels format: %s", channelsMsg)
	}

	if channelsParts[1] != "" {
		a.Channels = strings.Split(channelsParts[1], ",")
		log.Printf("Available channels: %v", a.Channels)
	} else {
		log.Printf("No channels available")
	}

	return nil
}

// Subscribe makes the agent join a channel
func (a *Agent) Subscribe(channel string) error {
	// Send subscribe message
	err := a.Conn.WriteMessage(websocket.TextMessage, []byte("SUBSCRIBE:"+channel))
	if err != nil {
		return fmt.Errorf("error subscribing to channel: %v", err)
	}

	// Wait for subscription acknowledgment
	_, msg, err := a.Conn.ReadMessage()
	if err != nil {
		return fmt.Errorf("error reading subscription response: %v", err)
	}

	// Check if subscription was successful
	if strings.HasPrefix(string(msg), "SUB-ACK:") {
		a.Subscriptions[channel] = true
		log.Printf("Subscribed to channel: %s", channel)
		return nil
	}

	return fmt.Errorf("failed to subscribe: %s", msg)
}

// Publish sends a message to a channel
func (a *Agent) Publish(channel, message string) error {
	// Check if subscribed to the channel
	if !a.Subscriptions[channel] {
		err := a.Subscribe(channel)
		if err != nil {
			return fmt.Errorf("can't publish without subscription: %v", err)
		}
	}

	// Send publish message
	err := a.Conn.WriteMessage(websocket.TextMessage, []byte("PUBLISH:"+channel+":"+message))
	if err != nil {
		return fmt.Errorf("error publishing message: %v", err)
	}

	log.Printf("Published message to channel %s", channel)
	return nil
}

// Close disconnects the agent from the broker
func (a *Agent) Close() error {
	if a.Conn != nil {
		// Send close message
		err := a.Conn.WriteMessage(websocket.CloseMessage, websocket.FormatCloseMessage(websocket.CloseNormalClosure, ""))
		if err != nil {
			log.Printf("Error during close message: %v", err)
		}
		return a.Conn.Close()
	}
	return nil
}

// GenerateMarketReport creates a competitive market analysis report
func (a *Agent) GenerateMarketReport() MarketReport {
	// Initialize random source
	rand.Seed(time.Now().UnixNano())

	// Create competitors
	competitors := make(map[string]CompetitorData)
	
	// Major competitors with their analysis
	competitors["MegaRetail"] = CompetitorData{
		MarketShare:     getRandomFloat(15, 25),
		GrowthRate:      getRandomFloat(3, 8),
		PriceComparison: "10-15% higher",
		Strengths:       "Brand recognition, premium positioning",
		Weaknesses:      "Higher prices, slower to adapt",
	}
	
	competitors["ValueMart"] = CompetitorData{
		MarketShare:     getRandomFloat(20, 30),
		GrowthRate:      getRandomFloat(1, 4),
		PriceComparison: "5-10% lower",
		Strengths:       "Aggressive pricing, large scale",
		Weaknesses:      "Lower quality, poor customer service",
	}
	
	competitors["TechGiants"] = CompetitorData{
		MarketShare:     getRandomFloat(10, 18),
		GrowthRate:      getRandomFloat(8, 15),
		PriceComparison: "Similar",
		Strengths:       "Digital integration, logistics",
		Weaknesses:      "Limited physical presence",
	}

	// Categories analysis
	categories := map[string]CategoryAnalysis{
		"Electronics": {
			MarketSize:        rand.Intn(500000) + 1000000,
			MarketShare:       getRandomFloat(12, 22),
			YearlyTrend:       randomTrend(),
			ConsumerSentiment: randomSentiment(),
		},
		"Clothing": {
			MarketSize:        rand.Intn(400000) + 800000,
			MarketShare:       getRandomFloat(8, 18),
			YearlyTrend:       randomTrend(),
			ConsumerSentiment: randomSentiment(),
		},
		"Food": {
			MarketSize:        rand.Intn(300000) + 600000,
			MarketShare:       getRandomFloat(5, 15),
			YearlyTrend:       randomTrend(),
			ConsumerSentiment: randomSentiment(),
		},
		"Books": {
			MarketSize:        rand.Intn(100000) + 300000,
			MarketShare:       getRandomFloat(15, 25),
			YearlyTrend:       randomTrend(),
			ConsumerSentiment: randomSentiment(),
		},
	}

	// Create report
	report := MarketReport{
		Date:           time.Now().Format("2006-01-02"),
		MarketSize:     rand.Intn(3000000) + 7000000, // 7-10M
		MarketGrowth:   getRandomFloat(2.5, 7.5),     // 2.5-7.5%
		OurMarketShare: getRandomFloat(12, 20),       // 12-20%
		Competitors:    competitors,
		Categories:     categories,
	}

	return report
}

// Helper functions for generating random data
func getRandomFloat(min, max float64) float64 {
	return min + rand.Float64()*(max-min)
}

func randomTrend() string {
	trends := []string{"Strong upward", "Moderate growth", "Stable", "Slight decline", "Volatile growth"}
	return trends[rand.Intn(len(trends))]
}

func randomSentiment() string {
	sentiments := []string{"Very positive", "Positive", "Neutral", "Mixed", "Concerned"}
	return sentiments[rand.Intn(len(sentiments))]
}

// FormatMarketReport converts a market report into a readable message
func (a *Agent) FormatMarketReport(report MarketReport) string {
	var sb strings.Builder

	sb.WriteString(fmt.Sprintf("\n🌐 MARKET ANALYSIS REPORT: %s\n", report.Date))
	sb.WriteString(fmt.Sprintf("📈 Total Market Size: $%d million\n", report.MarketSize/1000000))
	sb.WriteString(fmt.Sprintf("📊 Market Growth Rate: %.1f%%\n", report.MarketGrowth))
	sb.WriteString(fmt.Sprintf("🏢 Our Market Share: %.1f%%\n\n", report.OurMarketShare))

	// Competitor Analysis
	sb.WriteString("COMPETITOR ANALYSIS:\n")
	sb.WriteString("====================\n")
	
	for competitor, data := range report.Competitors {
		sb.WriteString(fmt.Sprintf("🏆 %s\n", competitor))
		sb.WriteString(fmt.Sprintf("   Market Share: %.1f%%\n", data.MarketShare))
		sb.WriteString(fmt.Sprintf("   Growth Rate: %.1f%%\n", data.GrowthRate))
		sb.WriteString(fmt.Sprintf("   Pricing: %s\n", data.PriceComparison))
		sb.WriteString(fmt.Sprintf("   Strengths: %s\n", data.Strengths))
		sb.WriteString(fmt.Sprintf("   Weaknesses: %s\n\n", data.Weaknesses))
	}

	// Category Analysis
	sb.WriteString("CATEGORY PERFORMANCE:\n")
	sb.WriteString("=====================\n")
	
	for category, data := range report.Categories {
		sb.WriteString(fmt.Sprintf("📦 %s\n", category))
		sb.WriteString(fmt.Sprintf("   Market Size: $%d million\n", data.MarketSize/1000000))
		sb.WriteString(fmt.Sprintf("   Our Market Share: %.1f%%\n", data.MarketShare))
		sb.WriteString(fmt.Sprintf("   Yearly Trend: %s\n", data.YearlyTrend))
		sb.WriteString(fmt.Sprintf("   Consumer Sentiment: %s\n\n", data.ConsumerSentiment))
	}

	// Strategic Recommendations
	sb.WriteString("STRATEGIC RECOMMENDATIONS:\n")
	sb.WriteString("=========================\n")
	
	// Generate random strategic recommendations
	recommendations := generateRecommendations(report)
	for i, rec := range recommendations {
		sb.WriteString(fmt.Sprintf("%d. %s\n", i+1, rec))
	}

	sb.WriteString(fmt.Sprintf("\nGenerated by %s at %s", 
		a.AgentName, time.Now().Format("15:04:05")))

	return sb.String()
}

// generateRecommendations creates strategic recommendations based on the report
func generateRecommendations(report MarketReport) []string {
	// Pool of possible recommendations
	possibleRecs := []string{
		"Increase marketing spend in categories with positive consumer sentiment",
		"Develop competitive pricing strategy against ValueMart in key categories",
		"Leverage digital channels to counter TechGiants' growing market share",
		"Focus on quality improvements to differentiate from ValueMart",
		"Expand product range in categories showing strong upward trends",
		"Reduce inventory in categories with declining market trends",
		"Invest in customer service to address our competitive weaknesses",
		"Develop premium product lines to compete with MegaRetail",
		"Focus on efficiency to improve margins while maintaining competitive pricing",
		"Explore strategic partnerships to increase market share in lower-performing categories",
	}
	
	// Randomly select 3-5 recommendations
	numRecs := rand.Intn(3) + 3
	if numRecs > len(possibleRecs) {
		numRecs = len(possibleRecs)
	}
	
	// Randomize and select recommendations
	recommendations := make([]string, 0)
	for i := 0; i < numRecs; i++ {
		idx := rand.Intn(len(possibleRecs))
		recommendations = append(recommendations, possibleRecs[idx])
		// Remove selected recommendation to avoid duplicates
		possibleRecs = append(possibleRecs[:idx], possibleRecs[idx+1:]...)
	}
	
	return recommendations
}

// PostMarketReport generates and posts a market analysis report
func (a *Agent) PostMarketReport(channel string) error {
	// Generate report
	report := a.GenerateMarketReport()
	
	// Format the report
	formattedReport := a.FormatMarketReport(report)
	
	// Publish to channel
	return a.Publish(channel, formattedReport)
}

// ListenForMessages processes incoming messages until interrupted
func (a *Agent) ListenForMessages() {
	for {
		_, message, err := a.Conn.ReadMessage()
		if err != nil {
			log.Printf("Read error: %v", err)
			return
		}
		log.Printf("Received: %s", message)
	}
}

func main() {
	// Create a new agent
	agent := NewAgent("ws://localhost:8765", "MarketAnalysisBot")
	
	// Connect to broker
	err := agent.Connect()
	if err != nil {
		log.Fatalf("Failed to connect: %v", err)
	}
	
	// Ensure we disconnect properly
	defer agent.Close()
	
	// Subscribe to reports channel
	reportChannel := "marketanalysis"
	err = agent.Subscribe(reportChannel)
	if err != nil {
		log.Fatalf("Failed to subscribe: %v", err)
	}
	
	// Also subscribe to the sales report channel to monitor sales data
	err = agent.Subscribe("dailyreports")
	if err != nil {
		log.Printf("Failed to subscribe to daily reports: %v", err)
	}
	
	// Post a market analysis report
	err = agent.PostMarketReport(reportChannel)
	if err != nil {
		log.Fatalf("Failed to post report: %v", err)
	}
	
	// Set up interrupt handler
	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, os.Interrupt)
	
	// Process messages until interrupted
	msgDone := make(chan struct{})
	go func() {
		agent.ListenForMessages()
		close(msgDone)
	}()
	
	// Wait for interrupt or message processing to end
	select {
	case <-interrupt:
		log.Println("Interrupt received, closing connection")
	case <-msgDone:
		log.Println("Message processing ended")
	}
	
	log.Println("Agent completed successfully")
}