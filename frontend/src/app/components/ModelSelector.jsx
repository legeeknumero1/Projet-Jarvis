import { useState, useEffect, useCallback } from 'react';
// Types removed for JSX compatibility

export default function ModelSelector({ selectedModel, onModelSelect, baseUrl }) {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchModels = useCallback(async () => {
    try {
      setError(null);
      setLoading(true);
      const response = await fetch(`${baseUrl}/chat/models`);
      if (!response.ok) {
        throw new Error('Failed to fetch models');
      }
      const data = await response.json();
      const modelList = data.models || [];
      setModels(modelList);

      // If currently selected model is not in the list, select the first available
      if (modelList.length > 0) {
        const modelNames = modelList.map((m: Model) => m.name);
        if (!modelNames.includes(selectedModel)) {
          onModelSelect(modelList[0]?.name || '');
        }
      }
    } catch (error) {
      console.error('Error fetching models:', error);
      setError('Failed to connect to Ollama server');
    } finally {
      setLoading(false);
    }
  }, [baseUrl, selectedModel, onModelSelect]);

  // Fetch models when component mounts and baseUrl changes
  useEffect(() => {
    fetchModels();
  }, [baseUrl, fetchModels]); // Removed selectedModel to fix dependency warning

  if (loading) {
    return <div className="loading loading-spinner loading-sm"></div>;
  }

  if (error) {
    return (
      <div className="text-error text-sm">
        {error}
      </div>
    );
  }

  return (
    <select
      className="select select-bordered w-full max-w-xs"
      value={selectedModel}
      onChange={(e) => onModelSelect(e.target.value)}
    >
      {models.length === 0 ? (
        <option value="">No models available</option>
      ) : (
        models.map((model) => (
          <option key={model.name} value={model.name}>
            {model.name}
          </option>
        ))
      )}
    </select>
  );
} 