package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"github.com/joho/godotenv"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// Prometheus metrics
var (
	serviceUptime = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "jarvis_service_uptime_seconds",
			Help: "Total uptime of service in seconds",
		},
		[]string{"service"},
	)

	apiLatency = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "jarvis_api_latency_ms",
			Help:    "API response latency in milliseconds",
			Buckets: []float64{1, 5, 10, 50, 100, 500, 1000},
		},
		[]string{"endpoint"},
	)

	requestCounter = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "jarvis_requests_total",
			Help: "Total number of requests",
		},
		[]string{"method", "endpoint", "status"},
	)

	systemHealth = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "jarvis_system_health",
			Help: "System health status (1=healthy, 0=unhealthy)",
		},
		[]string{"component"},
	)

	serviceStatus = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "jarvis_service_status",
			Help: "Service status (1=up, 0=down)",
		},
		[]string{"service"},
	)
)

func init() {
	prometheus.MustRegister(serviceUptime)
	prometheus.MustRegister(apiLatency)
	prometheus.MustRegister(requestCounter)
	prometheus.MustRegister(systemHealth)
	prometheus.MustRegister(serviceStatus)
}

// HTTP Watchdog - checks health of Jarvis services
type Watchdog struct {
	services map[string]string // service name -> URL
}

func NewWatchdog() *Watchdog {
	return &Watchdog{
		services: map[string]string{
			"core":   "http://localhost:8100/health",
			"audio":  "http://localhost:8004/health",
			"bridges": "http://localhost:8005/health",
			"db":     "http://localhost:5432",
			"redis":  "http://localhost:6379",
		},
	}
}

// Check health of each service
func (w *Watchdog) CheckHealth() {
	for service, url := range w.services {
		go func(svc, u string) {
			resp, err := http.Get(u)
			if err != nil {
				log.Printf("❌ Service %s unavailable: %v", svc, err)
				serviceStatus.WithLabelValues(svc).Set(0)
				return
			}
			defer resp.Body.Close()

			if resp.StatusCode == http.StatusOK {
				serviceStatus.WithLabelValues(svc).Set(1)
				log.Printf("✅ Service %s is healthy", svc)
			} else {
				serviceStatus.WithLabelValues(svc).Set(0)
				log.Printf("⚠️ Service %s returned status %d", svc, resp.StatusCode)
			}
		}(service, url)
	}
}

// Start periodic health checks
func (w *Watchdog) Start(interval time.Duration) {
	ticker := time.NewTicker(interval)
	go func() {
		for range ticker.C {
			w.CheckHealth()
		}
	}()
	log.Printf("🔍 Watchdog started (interval: %v)", interval)
}

func main() {
	// Load env vars
	godotenv.Load()

	port := os.Getenv("MONITORING_PORT")
	if port == "" {
		port = "9090"
	}

	// Initialize watchdog
	watchdog := NewWatchdog()
	watchdog.Start(15 * time.Second)

	// Initial health check
	watchdog.CheckHealth()

	// Prometheus metrics endpoint
	http.Handle("/metrics", promhttp.Handler())

	// Health check endpoint
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"healthy","version":"1.6.0"}`))
	})

	// Status endpoint
	http.HandleFunc("/status", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"monitoring":"active","timestamp":"` + time.Now().String() + `"}`))
	})

	// Dashboard (minimal)
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		w.WriteHeader(http.StatusOK)
		html := `
<!DOCTYPE html>
<html>
<head>
	<title>Jarvis Monitoring (Phase 6)</title>
	<style>
		body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
		.header { color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }
		.metrics { background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
		.metric-item { margin: 10px 0; }
		.label { font-weight: bold; color: #0066cc; }
		a { color: #0066cc; text-decoration: none; }
		a:hover { text-decoration: underline; }
	</style>
</head>
<body>
	<div class="header">
		<h1>🔍 Jarvis Monitoring Dashboard (Phase 6)</h1>
		<p>Go Monitoring Service - Port 9090 - Prometheus + HTTP Watchdog</p>
	</div>

	<div class="metrics">
		<h2>📊 Metrics Endpoints</h2>
		<div class="metric-item"><span class="label">Prometheus:</span> <a href="/metrics">/metrics</a></div>
		<div class="metric-item"><span class="label">Health:</span> <a href="/health">/health</a></div>
		<div class="metric-item"><span class="label">Status:</span> <a href="/status">/status</a></div>
	</div>

	<div class="metrics">
		<h2>🚀 Jarvis Services</h2>
		<div class="metric-item">• Core Backend (8100) - Rust with Axum</div>
		<div class="metric-item">• Audio Engine (8004) - C++ DSP</div>
		<div class="metric-item">• Python Bridges (8005) - Whisper/Piper/Ollama</div>
		<div class="metric-item">• DB Layer - PostgreSQL + Redis + Tantivy</div>
		<div class="metric-item">• MQTT Automations - rumqttc event bus</div>
	</div>

	<div class="metrics">
		<h2>📈 Monitoring Capabilities</h2>
		<ul>
			<li>Service uptime tracking</li>
			<li>API latency histograms</li>
			<li>Request counters by endpoint/method/status</li>
			<li>System health gauges</li>
			<li>HTTP watchdog health checks (15s interval)</li>
		</ul>
	</div>
</body>
</html>
		`
		w.Write([]byte(html))
	})

	log.Printf("🚀 Jarvis Monitoring (Phase 6) starting on port %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("❌ Server error: %v", err)
	}
}
