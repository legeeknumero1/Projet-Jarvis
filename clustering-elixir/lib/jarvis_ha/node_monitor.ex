defmodule JarvisHA.NodeMonitor do
  use GenServer
  require Logger

  def start_link(_opts) do
    GenServer.start_link(__MODULE__, :ok, name: __MODULE__)
  end

  @impl true
  def init(:ok) do
    # Subscribe to node events
    :net_kernel.monitor_nodes(true)

    Logger.info(" Node Monitor started")

    {:ok,
     %{
       healthy_nodes: MapSet.new(),
       dead_nodes: MapSet.new(),
       started_at: DateTime.utc_now()
     }}
  end

  @impl true
  def handle_info({:nodeup, node}, state) do
    Logger.info(" Node joined cluster: #{node}")

    new_state = %{
      state
      | healthy_nodes: MapSet.put(state.healthy_nodes, node),
        dead_nodes: MapSet.delete(state.dead_nodes, node)
    }

    broadcast_node_event({:node_joined, node})
    {:noreply, new_state}
  end

  def handle_info({:nodedown, node}, state) do
    Logger.warn(" Node left cluster: #{node}")

    new_state = %{
      state
      | healthy_nodes: MapSet.delete(state.healthy_nodes, node),
        dead_nodes: MapSet.put(state.dead_nodes, node)
    }

    broadcast_node_event({:node_left, node})

    # Attempt recovery if possible
    schedule_recovery_check(node)

    {:noreply, new_state}
  end

  def handle_info({:recovery_check, node}, state) do
    case Node.ping(node) do
      :pong ->
        Logger.info(" Node recovered: #{node}")

        new_state = %{
          state
          | healthy_nodes: MapSet.put(state.healthy_nodes, node),
            dead_nodes: MapSet.delete(state.dead_nodes, node)
        }

        broadcast_node_event({:node_recovered, node})
        {:noreply, new_state}

      :pang ->
        # Try again later
        schedule_recovery_check(node)
        {:noreply, state}
    end
  end

  # Public API

  def get_status do
    GenServer.call(__MODULE__, :get_status)
  end

  def healthy_nodes do
    GenServer.call(__MODULE__, :healthy_nodes)
  end

  def dead_nodes do
    GenServer.call(__MODULE__, :dead_nodes)
  end

  @impl true
  def handle_call(:get_status, _from, state) do
    status = %{
      node: node(),
      healthy_nodes: MapSet.to_list(state.healthy_nodes),
      dead_nodes: MapSet.to_list(state.dead_nodes),
      healthy_count: MapSet.size(state.healthy_nodes),
      dead_count: MapSet.size(state.dead_nodes),
      started_at: state.started_at
    }

    {:reply, status, state}
  end

  def handle_call(:healthy_nodes, _from, state) do
    {:reply, MapSet.to_list(state.healthy_nodes), state}
  end

  def handle_call(:dead_nodes, _from, state) do
    {:reply, MapSet.to_list(state.dead_nodes), state}
  end

  # Private helpers

  defp broadcast_node_event(event) do
    JarvisHA.EventBus.broadcast("cluster:events", event)
  end

  defp schedule_recovery_check(node) do
    Process.send_after(self(), {:recovery_check, node}, 5000)
  end
end
