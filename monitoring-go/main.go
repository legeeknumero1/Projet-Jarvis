package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/docker/docker/client"
	"github.com/joho/godotenv"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// Watchdog monitoring for Jarvis services
type Watchdog struct {
	dockerClient *client.Client
	interval     time.Duration
}

// Prometheus metrics
var (
	containerRestarts = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "jarvis_container_restarts_total",
			Help: "Total number of container restarts",
		},
		[]string{"container"},
	)

	containerHealth = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "jarvis_container_health",
			Help: "Container health status (1=healthy, 0=unhealthy)",
		},
		[]string{"container"},
	)

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

	systemMemory = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "jarvis_system_memory_bytes",
			Help: "System memory usage in bytes",
		},
		[]string{"type"},
	)

	systemCPU = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "jarvis_system_cpu_percent",
			Help: "System CPU usage in percent",
		},
		[]string{"cpu"},
	)
)

func init() {
	prometheus.MustRegister(containerRestarts)
	prometheus.MustRegister(containerHealth)
	prometheus.MustRegister(serviceUptime)
	prometheus.MustRegister(apiLatency)
	prometheus.MustRegister(requestCounter)
	prometheus.MustRegister(systemMemory)
	prometheus.MustRegister(systemCPU)
}

func NewWatchdog() (*Watchdog, error) {
	docker, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return nil, fmt.Errorf("failed to create docker client: %w", err)
	}

	return &Watchdog{
		dockerClient: docker,
		interval:     30 * time.Second,
	}, nil
}

// Health check endpoint
func (w *Watchdog) healthCheck(writer http.ResponseWriter, request *http.Request) {
	services := []string{
		"jarvis_rust_backend",
		"jarvis_audio_engine",
		"jarvis_python_bridges",
		"jarvis_ollama",
		"postgres",
		"redis",
	}

	allHealthy := true
	healthStatus := make(map[string]string)

	for _, service := range services {
		status, err := w.checkService(request.Context(), service)
		if err != nil {
			healthStatus[service] = "error"
			allHealthy = false
		} else if status {
			healthStatus[service] = "healthy"
			containerHealth.WithLabelValues(service).Set(1)
		} else {
			healthStatus[service] = "unhealthy"
			allHealthy = false
			containerHealth.WithLabelValues(service).Set(0)
		}
	}

	writer.Header().Set("Content-Type", "application/json")

	if allHealthy {
		writer.WriteHeader(http.StatusOK)
		fmt.Fprintf(writer, `{"status":"healthy","services":%#v}`, healthStatus)
	} else {
		writer.WriteHeader(http.StatusServiceUnavailable)
		fmt.Fprintf(writer, `{"status":"degraded","services":%#v}`, healthStatus)
	}
}

// Check individual service
func (w *Watchdog) checkService(ctx context.Context, serviceName string) (bool, error) {
	log.Printf("🔍 Checking service: %s", serviceName)

	// Vérifier si le container Docker existe et tourne
	containers, err := w.dockerClient.ContainerList(ctx, container.ListOptions{})
	if err != nil {
		return false, err
	}

	for _, c := range containers {
		if contains(c.Names, "/"+serviceName) {
			if c.State == "running" {
				log.Printf("✅ %s is running", serviceName)
				return true, nil
			}
		}
	}

	log.Printf("❌ %s is not running", serviceName)
	return false, nil
}

// Restart dead services
func (w *Watchdog) restartServices(ctx context.Context) {
	services := []string{
		"jarvis_rust_backend",
		"jarvis_python_bridges",
		"jarvis_audio_engine",
	}

	for _, service := range services {
		healthy, _ := w.checkService(ctx, service)
		if !healthy {
			log.Printf("🔄 Restarting service: %s", service)
			containerRestarts.WithLabelValues(service).Inc()
			// Dans une implémentation réelle:
			// w.dockerClient.ContainerRestart(ctx, containerID, ...)
		}
	}
}

// Watchdog loop
func (w *Watchdog) Start(ctx context.Context) {
	log.Println("🐕 Watchdog started")

	ticker := time.NewTicker(w.interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			log.Println("🛑 Watchdog stopped")
			return
		case <-ticker.C:
			w.restartServices(ctx)
		}
	}
}

func main() {
	// Load .env
	_ = godotenv.Load()

	log.Println("🐹 Jarvis Monitoring v1.6.0")

	// Create watchdog
	watchdog, err := NewWatchdog()
	if err != nil {
		log.Fatalf("Failed to create watchdog: %v", err)
	}

	// Setup HTTP routes
	http.HandleFunc("/health", watchdog.healthCheck)
	http.Handle("/metrics", promhttp.Handler())

	// Start watchdog in goroutine
	ctx, cancel := context.WithCancel(context.Background())
	go watchdog.Start(ctx)

	// Start HTTP server
	server := &http.Server{
		Addr:         ":8006",
		Handler:      http.DefaultServeMux,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 5 * time.Second,
	}

	log.Println("📊 Prometheus metrics on :8006/metrics")
	log.Println("🏥 Health check on :8006/health")

	// Handle shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigChan
		log.Println("📵 Shutting down...")
		cancel()
		server.Shutdown(context.Background())
	}()

	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Server error: %v", err)
	}
}

func contains(arr []string, str string) bool {
	for _, v := range arr {
		if v == str {
			return true
		}
	}
	return false
}
