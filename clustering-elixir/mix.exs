defmodule JarvisHA.MixProject do
  use Mix.Project

  def project do
    [
      app: :jarvis_ha,
      version: "1.9.0",
      elixir: "~> 1.14",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      releases: releases()
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {JarvisHA.Application, []}
    ]
  end

  defp deps do
    [
      # Clustering
      {:libcluster, "~> 3.3"},
      {:horde, "~> 0.8"},

      # Supervision & resilience
      {:supervisor_tree, "~> 0.1"},

      # Consensus algorithm
      {:ra, "~> 2.6"},

      # State management
      {:ecto, "~> 3.10"},
      {:ecto_sql, "~> 3.10"},
      {:postgrex, "~> 0.17"},

      # HTTP & messaging
      {:tesla, "~> 1.7"},
      {:plug_cowboy, "~> 2.6"},
      {:jason, "~> 1.4"},
      {:cowboy, "~> 2.9"},

      # Event bus
      {:gen_stage, "~> 1.0"},
      {:broadway, "~> 1.0"},

      # Metrics
      {:prometheus_ex, "~> 3.0"},
      {:prometheus_plugs, "~> 1.1"},

      # Logging
      {:logger_json, "~> 5.1"},

      # Testing
      {:ex_unit_fixtures, "~> 0.1", only: :test},
      {:mock, "~> 0.3", only: :test}
    ]
  end

  defp releases do
    [
      jarvis_ha: [
        include_executables_for: [:unix],
        applications: [runtime_tools: :permanent]
      ]
    ]
  end
end
