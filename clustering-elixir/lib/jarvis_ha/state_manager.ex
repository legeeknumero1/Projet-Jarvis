defmodule JarvisHA.StateManager do
  @moduledoc """
  Distributed state management using Raft consensus algorithm.

  This module provides a replicated, strongly-consistent key-value store
  across the Jarvis cluster using the Ra library (Raft implementation).

  ## Features
  - Strong consistency via Raft consensus
  - Automatic leader election
  - Log replication across nodes
  - Crash recovery
  - Snapshot support

  ## Usage
      # Start the Raft cluster
      StateManager.start_cluster([:node1@host, :node2@host, :node3@host])

      # Write state (replicated to all nodes)
      StateManager.put("user:123:session", %{token: "abc", expires: ~U[2025-01-01 00:00:00Z]})

      # Read state (from leader)
      StateManager.get("user:123:session")

      # Delete state
      StateManager.delete("user:123:session")
  """

  use GenServer
  require Logger

  @ra_system :jarvis_raft
  @cluster_name :jarvis_state_cluster

  # Client API

  @doc """
  Start the StateManager GenServer.
  """
  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  @doc """
  Initialize the Raft cluster with a list of nodes.

  ## Parameters
  - nodes: List of node names (e.g., [:node1@host, :node2@host])

  ## Returns
  - :ok | {:error, reason}
  """
  def start_cluster(nodes) when is_list(nodes) do
    GenServer.call(__MODULE__, {:start_cluster, nodes})
  end

  @doc """
  Store a key-value pair in the distributed state.

  This operation is replicated to all nodes via Raft consensus.

  ## Parameters
  - key: String key
  - value: Any Elixir term (will be serialized)

  ## Returns
  - :ok | {:error, reason}
  """
  def put(key, value) do
    GenServer.call(__MODULE__, {:put, key, value})
  end

  @doc """
  Retrieve a value from the distributed state.

  ## Parameters
  - key: String key

  ## Returns
  - {:ok, value} | {:error, :not_found}
  """
  def get(key) do
    GenServer.call(__MODULE__, {:get, key})
  end

  @doc """
  Delete a key from the distributed state.

  ## Parameters
  - key: String key

  ## Returns
  - :ok | {:error, reason}
  """
  def delete(key) do
    GenServer.call(__MODULE__, {:delete, key})
  end

  @doc """
  List all keys in the distributed state.

  ## Returns
  - {:ok, [key]} | {:error, reason}
  """
  def list_keys do
    GenServer.call(__MODULE__, :list_keys)
  end

  @doc """
  Get cluster status and leader information.

  ## Returns
  - %{leader: node, members: [node], state: :running | :initializing}
  """
  def cluster_status do
    GenServer.call(__MODULE__, :cluster_status)
  end

  # Server Callbacks

  @impl true
  def init(_opts) do
    Logger.info("StateManager initializing...")

    # Start Ra system
    case :ra.start_in(Node.self()) do
      {:ok, _} -> Logger.info("Ra system started")
      {:error, {:already_started, _}} -> Logger.info("Ra system already running")
      error -> Logger.error("Failed to start Ra system: #{inspect(error)}")
    end

    state = %{
      cluster_started: false,
      server_id: nil,
      members: []
    }

    {:ok, state}
  end

  @impl true
  def handle_call({:start_cluster, nodes}, _from, state) do
    Logger.info("Starting Raft cluster with nodes: #{inspect(nodes)}")

    server_id = {__MODULE__, Node.self()}

    # Build cluster configuration
    machine = %{
      module: __MODULE__.Machine,
      init: fn -> %{} end
    }

    members = Enum.map(nodes, fn node -> {__MODULE__, node} end)

    cluster_config = %{
      id: @cluster_name,
      uid: "jarvis_state_#{:erlang.system_time()}",
      initial_members: members,
      log_init_args: %{uid: "jarvis_state_log"},
      machine: machine
    }

    case :ra.start_cluster(@ra_system, cluster_config) do
      {:ok, started_servers, _} ->
        Logger.info("Raft cluster started: #{inspect(started_servers)}")

        new_state = %{
          state
          | cluster_started: true,
            server_id: server_id,
            members: members
        }

        {:reply, :ok, new_state}

      {:error, reason} ->
        Logger.error("Failed to start Raft cluster: #{inspect(reason)}")
        {:reply, {:error, reason}, state}
    end
  end

  @impl true
  def handle_call({:put, key, value}, _from, %{cluster_started: true, server_id: server_id} = state) do
    command = {:put, key, value}

    case :ra.process_command(server_id, command) do
      {:ok, _result, _leader} ->
        {:reply, :ok, state}

      {:error, reason} ->
        {:reply, {:error, reason}, state}

      {:timeout, _} ->
        {:reply, {:error, :timeout}, state}
    end
  end

  @impl true
  def handle_call({:get, key}, _from, %{cluster_started: true, server_id: server_id} = state) do
    case :ra.consistent_query(server_id, fn state_map -> Map.get(state_map, key) end) do
      {:ok, {:ok, value}, _leader} ->
        {:reply, {:ok, value}, state}

      {:ok, {nil, _}, _leader} ->
        {:reply, {:error, :not_found}, state}

      {:error, reason} ->
        {:reply, {:error, reason}, state}

      {:timeout, _} ->
        {:reply, {:error, :timeout}, state}
    end
  end

  @impl true
  def handle_call({:delete, key}, _from, %{cluster_started: true, server_id: server_id} = state) do
    command = {:delete, key}

    case :ra.process_command(server_id, command) do
      {:ok, _result, _leader} ->
        {:reply, :ok, state}

      {:error, reason} ->
        {:reply, {:error, reason}, state}

      {:timeout, _} ->
        {:reply, {:error, :timeout}, state}
    end
  end

  @impl true
  def handle_call(:list_keys, _from, %{cluster_started: true, server_id: server_id} = state) do
    case :ra.consistent_query(server_id, fn state_map -> Map.keys(state_map) end) do
      {:ok, {:ok, keys}, _leader} ->
        {:reply, {:ok, keys}, state}

      {:error, reason} ->
        {:reply, {:error, reason}, state}

      {:timeout, _} ->
        {:reply, {:error, :timeout}, state}
    end
  end

  @impl true
  def handle_call(:cluster_status, _from, %{cluster_started: true, server_id: server_id, members: members} = state) do
    case :ra.members(server_id) do
      {:ok, leader, member_list} ->
        status = %{
          leader: leader,
          members: member_list,
          configured_members: members,
          state: :running
        }
        {:reply, status, state}

      {:error, _reason} ->
        status = %{
          leader: nil,
          members: members,
          configured_members: members,
          state: :initializing
        }
        {:reply, status, state}
    end
  end

  @impl true
  def handle_call(_request, _from, %{cluster_started: false} = state) do
    {:reply, {:error, :cluster_not_started}, state}
  end
end

defmodule JarvisHA.StateManager.Machine do
  @moduledoc """
  Ra state machine implementation for Jarvis distributed state.

  This module defines the commands and queries that can be applied to the Raft log.
  """

  @behaviour :ra_machine

  @impl :ra_machine
  def init(_config) do
    %{}
  end

  @impl :ra_machine
  def apply(_meta, {:put, key, value}, state) do
    new_state = Map.put(state, key, value)
    {new_state, :ok, []}
  end

  @impl :ra_machine
  def apply(_meta, {:delete, key}, state) do
    new_state = Map.delete(state, key)
    {new_state, :ok, []}
  end

  @impl :ra_machine
  def apply(_meta, _command, state) do
    {state, {:error, :unknown_command}, []}
  end

  @impl :ra_machine
  def state_enter(:leader, state) do
    [:leader_elected | state]
  end

  @impl :ra_machine
  def state_enter(_status, state) do
    state
  end

  @impl :ra_machine
  def snapshot_installed(meta, state) do
    {state, meta}
  end

  @impl :ra_machine
  def overview(_state) do
    %{}
  end
end
