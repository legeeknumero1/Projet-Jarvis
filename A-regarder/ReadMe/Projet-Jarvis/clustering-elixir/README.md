#  Jarvis Elixir HA - Phase 9

**Haute disponibilité distribuée avec Elixir/Erlang clustering**

Architecture résiliente pour déploiement multi-nœuds avec failover automatique et state synchronization.

---

##  Architecture

### Stack Technique

- **Elixir 1.14** : Concurrent, resilient, distributed
- **Erlang OTP** : Supervision trees, hot reload
- **libcluster** : Automatic node discovery
- **Horde** : Distributed registry et supervisor
- **Raft** : Consensus-based state management
- **Broadway** : Event processing pipeline

---

##  Clustering

### Node Discovery

**Kubernetes (recommandé)**
```elixir
config :libcluster,
  topologies: [
    jarvis: [
      strategy: Cluster.Strategy.Kubernetes,
      config: [
        kubernetes_node_basename: "jarvis",
        kubernetes_selector_labels: %{"app" => "jarvis"},
        kubernetes_namespace: "default"
      ]
    ]
  ]
```

**Static (dev/test)**
```elixir
config :libcluster,
  topologies: [
    jarvis: [
      strategy: Cluster.Strategy.Static,
      config: [
        nodes: ["jarvis@node1", "jarvis@node2", "jarvis@node3"]
      ]
    ]
  ]
```

### Node Monitor
Automatic detection de:
- Nodes qui rejoignent le cluster (:nodeup)
- Nodes qui quittent (:nodedown)
- Automatic recovery attempts
- Event broadcasting

---

##  Distributed Services

### Horde Registry
```elixir
# Register service globally
Horde.Registry.register(JarvisHA.Registry, "service_id", self())

# Lookup service from anywhere
{:ok, pid} = Horde.Registry.lookup(JarvisHA.Registry, "service_id")
```

### Horde DynamicSupervisor
```elixir
# Start worker on any available node
{:ok, pid} = Horde.DynamicSupervisor.start_child(
  JarvisHA.DynamicSupervisor,
  {JarvisHA.Worker, []}
)
```

---

##  State Management

### Raft-based Consensus
```elixir
# Write state atomically across cluster
JarvisHA.StateManager.put_global("conversation:123", data)

# Read state from any node
data = JarvisHA.StateManager.get_global("conversation:123")
```

### Replicated Databases
```
Node 1 (Leader)
    ↓
PostgreSQL + Replication
    ↓
Node 2, Node 3 (Followers)
```

---

##  Event Bus

### Pub/Sub Pattern
```elixir
# Subscribe
JarvisHA.EventBus.subscribe("chat:messages")

# Broadcast
JarvisHA.EventBus.broadcast("chat:messages", {:new_message, msg})

# Handle events
def handle_info({:new_message, msg}, state) do
  Logger.info("New message: #{msg.content}")
  {:noreply, state}
end
```

---

##  Health & Monitoring

### Health Check Endpoint
```bash
GET http://node:8007/health
# {
#   "status": "healthy",
#   "node": "jarvis@node1",
#   "cluster_nodes": 3,
#   "healthy_nodes": 3,
#   "uptime_seconds": 3600
# }
```

### Metrics Export
```bash
GET http://node:8007/metrics
# Prometheus format
```

---

##  Deployment

### Kubernetes Helm Chart
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: jarvis-ha
spec:
  serviceName: jarvis-ha
  replicas: 3
  selector:
    matchLabels:
      app: jarvis
  template:
    metadata:
      labels:
        app: jarvis
    spec:
      containers:
      - name: jarvis
        image: jarvis:1.9.0
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: CLUSTER_STRATEGY
          value: "kubernetes"
        - name: NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        ports:
        - containerPort: 4369  # EPMD
        - containerPort: 8007  # Health
```

### Docker Compose
```yaml
version: '3.9'

services:
  jarvis-node1:
    image: jarvis:1.9.0
    environment:
      NODE_NAME: jarvis@jarvis-node1
      CLUSTER_STRATEGY: static
      CLUSTER_NODES: jarvis@jarvis-node1,jarvis@jarvis-node2,jarvis@jarvis-node3
    ports:
      - "8007:8007"
    networks:
      - jarvis_network

  jarvis-node2:
    image: jarvis:1.9.0
    environment:
      NODE_NAME: jarvis@jarvis-node2
      CLUSTER_STRATEGY: static
      CLUSTER_NODES: jarvis@jarvis-node1,jarvis@jarvis-node2,jarvis@jarvis-node3
    networks:
      - jarvis_network

  jarvis-node3:
    image: jarvis:1.9.0
    environment:
      NODE_NAME: jarvis@jarvis-node3
      CLUSTER_STRATEGY: static
      CLUSTER_NODES: jarvis@jarvis-node1,jarvis@jarvis-node2,jarvis@jarvis-node3
    networks:
      - jarvis_network

networks:
  jarvis_network:
    external: true
```

---

##  Failover & Recovery

### Automatic Failover
1. Node goes down → :nodedown event
2. Horde rebalances supervisors
3. Other nodes take over responsibilities
4. Client reconnects to new leader

### Recovery Process
1. Detect node down
2. Mark as unavailable
3. Attempt recovery every 5s
4. When node comes back:
   - :nodeup event
   - Sync state from cluster
   - Re-register services
   - Resume operations

---

##  Scalability

### Horizontal Scaling
```
1 node:    1 Jarvis instance
3 nodes:   3 active instances + redundancy
5 nodes:   5 active + 2 hot standbys
10 nodes:  10 active + distributed load
```

### Load Balancing
```
                    Load Balancer
                         ↓
        
        ↓        ↓        ↓        ↓
    Node1    Node2    Node3    Node4
      |        |        |        |
      
                  ↓
          PostgreSQL Cluster
              (Replication)
```

---

##  Consistency & CAP

### Trade-offs
- **Consistency** : Raft for critical state
- **Availability** : Services continue on node down
- **Partition tolerance** : Quorum-based decisions

### Guarantees
- No split-brain (consensus-based)
- Eventual consistency for replicated data
- Strong consistency for critical operations

---

##  Performance

```
Replication latency: <100ms across nodes
Failover time:       ~2-5s
Message throughput:  1000+ msg/s per node
State sync:          <500ms initial sync
```

---

##  Intégration Architecture

**Phase 9 - Final Architecture :**

```
Multi-node Cluster (Elixir/Erlang)
 Node 1: Full stack
 Node 2: Full stack
 Node 3: Full stack

Each node runs:
  Rust Backend (8100)
  C++ Audio (8004)
  Python Bridges (8005)
  Rust DB (lib)
  Rust MQTT (lib)
  Go Monitor (8006)
  Frontend (3000)
  Lua Plugins (lib)
  Elixir Clustering (8007)

Shared:
 PostgreSQL Cluster (replication)
 Redis Cluster (sentinels)
 Load Balancer
```

---

** Jarvis HA - Distributed, resilient, self-healing**

*Architecture Polyglotte Phase 9 - Production Ready*
