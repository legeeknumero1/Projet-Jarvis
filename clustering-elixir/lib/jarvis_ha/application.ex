defmodule JarvisHA.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Clustering with libcluster
      {Cluster.Supervisor,
       [
         [
           {:jarvis, libcluster_topologies()}
         ],
         [name: JarvisHA.ClusterSupervisor]
       ]},

      # Distributed registry (Horde)
      {Horde.Registry, [name: JarvisHA.Registry]},

      # Distributed supervisor (Horde)
      {Horde.DynamicSupervisor,
       [name: JarvisHA.DynamicSupervisor, strategy: :one_for_one]},

      # Node monitor
      {JarvisHA.NodeMonitor, []},

      # Raft-based state management
      {JarvisHA.StateManager, []},

      # Event bus
      {JarvisHA.EventBus, []},

      # Health check server
      {Plug.Cowboy,
       [
         scheme: :http,
         plug: JarvisHA.HealthCheck,
         options: [port: 8007]
       ]},

      # Metrics exporter
      {JarvisHA.MetricsServer, []}
    ]

    opts = [strategy: :one_for_one, name: JarvisHA.Supervisor]
    Supervisor.start_link(children, opts)
  end

  defp libcluster_topologies do
    case System.get_env("CLUSTER_STRATEGY", "static") do
      "static" ->
        [
          strategy: Cluster.Strategy.Static,
          config: [
            nodes: String.split(System.get_env("CLUSTER_NODES", "jarvis@127.0.0.1"), ",")
          ]
        ]

      "kubernetes" ->
        [
          strategy: Cluster.Strategy.Kubernetes,
          config: [
            kubernetes_node_basename: "jarvis",
            kubernetes_selector_labels: %{"app" => "jarvis"},
            kubernetes_namespace: System.get_env("NAMESPACE", "default")
          ]
        ]

      "epmd" ->
        [
          strategy: Cluster.Strategy.Epmd,
          config: [
            hosts: String.split(System.get_env("EPMD_HOSTS", "localhost"), ",")
          ]
        ]

      _ ->
        []
    end
  end
end
