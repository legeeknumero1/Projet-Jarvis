package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// LokiClient pushes logs to Grafana Loki
type LokiClient struct {
	URL    string
	Client *http.Client
}

// LokiStream represents a Loki log stream
type LokiStream struct {
	Stream map[string]string `json:"stream"`
	Values [][]string        `json:"values"`
}

// LokiPushRequest is the request format for Loki
type LokiPushRequest struct {
	Streams []LokiStream `json:"streams"`
}

// NewLokiClient creates a new Loki client
func NewLokiClient(url string) *LokiClient {
	return &LokiClient{
		URL: url,
		Client: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// PushLog sends a log entry to Loki
func (l *LokiClient) PushLog(labels map[string]string, message string) error {
	timestamp := fmt.Sprintf("%d", time.Now().UnixNano())

	stream := LokiStream{
		Stream: labels,
		Values: [][]string{
			{timestamp, message},
		},
	}

	pushReq := LokiPushRequest{
		Streams: []LokiStream{stream},
	}

	jsonData, err := json.Marshal(pushReq)
	if err != nil {
		return fmt.Errorf("failed to marshal log: %w", err)
	}

	req, err := http.NewRequest("POST", l.URL+"/loki/api/v1/push", bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := l.Client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to push log: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusNoContent && resp.StatusCode != http.StatusOK {
		return fmt.Errorf("loki returned status %d", resp.StatusCode)
	}

	return nil
}

// PushServiceLog pushes a service-specific log
func (l *LokiClient) PushServiceLog(service, level, message string) error {
	labels := map[string]string{
		"job":     "jarvis",
		"service": service,
		"level":   level,
	}
	return l.PushLog(labels, message)
}
