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

// SalesReport represents a daily sales report structure
type SalesReport struct {
	Date        string                      `json:"date"`
	TotalSales  int                         `json:"total_sales"`
	Departments map[string]DepartmentReport `json:"departments"`
}

// DepartmentReport contains sales data for a department
type DepartmentReport struct {
	Sales        int `json:"sales"`
	Transactions int `json:"transactions"`
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

// GenerateSalesReport creates a random sales report
func (a *Agent) GenerateSalesReport() SalesReport {
	// Initialize random source
	rand.Seed(time.Now().UnixNano())

	// Create departments
	departments := []string{"Electronics", "Clothing", "Food", "Books"}
	deptReports := make(map[string]DepartmentReport)

	for _, dept := range departments {
		deptReports[dept] = DepartmentReport{
			Sales:        rand.Intn(4500) + 500, // 500-5000
			Transactions: rand.Intn(90) + 10,    // 10-100
		}
	}

	// Create report
	report := SalesReport{
		Date:        time.Now().Format("2006-01-02"),
		TotalSales:  rand.Intn(15000) + 5000, // 5000-20000
		Departments: deptReports,
	}

	return report
}

// FormatReport converts a sales report into a readable message
func (a *Agent) FormatReport(report SalesReport) string {
	var sb strings.Builder

	sb.WriteString(fmt.Sprintf("\n📊 DAILY SALES REPORT: %s\n", report.Date))
	sb.WriteString(fmt.Sprintf("💰 Total Sales: $%d\n\n", report.TotalSales))
	sb.WriteString("Department Breakdown:\n")
	sb.WriteString("------------------------------\n")

	// Add each department
	for dept, data := range report.Departments {
		sb.WriteString(fmt.Sprintf("• %s: $%d (%d transactions)\n", 
			dept, data.Sales, data.Transactions))
	}

	sb.WriteString(fmt.Sprintf("\nGenerated by %s at %s", 
		a.AgentName, time.Now().Format("15:04:05")))

	return sb.String()
}

// PostReport generates and posts a sales report
func (a *Agent) PostReport(channel string) error {
	// Generate report
	report := a.GenerateSalesReport()
	
	// Format the report
	formattedReport := a.FormatReport(report)
	
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
	agent := NewAgent("ws://localhost:8765", "GoReportBot")
	
	// Connect to broker
	err := agent.Connect()
	if err != nil {
		log.Fatalf("Failed to connect: %v", err)
	}
	
	// Ensure we disconnect properly
	defer agent.Close()
	
	// Subscribe to reports channel
	reportChannel := "dailyreports"
	err = agent.Subscribe(reportChannel)
	if err != nil {
		log.Fatalf("Failed to subscribe: %v", err)
	}
	
	// Post a report
	err = agent.PostReport(reportChannel)
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
