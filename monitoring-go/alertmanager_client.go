package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// AlertmanagerClient sends alerts to Prometheus Alertmanager
type AlertmanagerClient struct {
	URL    string
	Client *http.Client
}

// Alert represents a Prometheus alert
type Alert struct {
	Labels      map[string]string `json:"labels"`
	Annotations map[string]string `json:"annotations"`
	StartsAt    time.Time         `json:"startsAt,omitempty"`
	EndsAt      time.Time         `json:"endsAt,omitempty"`
}

// NewAlertmanagerClient creates a new Alertmanager client
func NewAlertmanagerClient(url string) *AlertmanagerClient {
	return &AlertmanagerClient{
		URL: url,
		Client: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// SendAlert sends an alert to Alertmanager
func (a *AlertmanagerClient) SendAlert(alert Alert) error {
	alerts := []Alert{alert}

	jsonData, err := json.Marshal(alerts)
	if err != nil {
		return fmt.Errorf("failed to marshal alert: %w", err)
	}

	req, err := http.NewRequest("POST", a.URL+"/api/v2/alerts", bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := a.Client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send alert: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("alertmanager returned status %d", resp.StatusCode)
	}

	return nil
}

// SendServiceDownAlert sends an alert for a down service
func (a *AlertmanagerClient) SendServiceDownAlert(serviceName string, severity string) error {
	alert := Alert{
		Labels: map[string]string{
			"alertname": "ServiceDown",
			"service":   serviceName,
			"severity":  severity,
			"job":       "jarvis",
		},
		Annotations: map[string]string{
			"summary":     fmt.Sprintf("Service %s is down", serviceName),
			"description": fmt.Sprintf("Jarvis service %s has failed health check", serviceName),
		},
		StartsAt: time.Now(),
	}

	return a.SendAlert(alert)
}

// SendHighLatencyAlert sends an alert for high latency
func (a *AlertmanagerClient) SendHighLatencyAlert(serviceName string, latencyMs float64) error {
	alert := Alert{
		Labels: map[string]string{
			"alertname": "HighLatency",
			"service":   serviceName,
			"severity":  "warning",
			"job":       "jarvis",
		},
		Annotations: map[string]string{
			"summary":     fmt.Sprintf("High latency on %s", serviceName),
			"description": fmt.Sprintf("Service %s latency is %.2fms (threshold: 100ms)", serviceName, latencyMs),
		},
		StartsAt: time.Now(),
	}

	return a.SendAlert(alert)
}

// ResolveAlert resolves an alert
func (a *AlertmanagerClient) ResolveAlert(alertName, serviceName string) error {
	alert := Alert{
		Labels: map[string]string{
			"alertname": alertName,
			"service":   serviceName,
			"job":       "jarvis",
		},
		EndsAt: time.Now(),
	}

	return a.SendAlert(alert)
}
