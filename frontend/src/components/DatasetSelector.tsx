/** Dataset selector component */
import { useEffect, useState, useRef } from 'react';
import { Database, Plus, Trash2, Upload } from 'lucide-react';
import { useQueryStore } from '../stores/queryStore';
import { datasetApi } from '../services/api';

export function DatasetSelector() {
  const {
    currentUserId,
    currentDatasetId,
    datasets,
    setDatasetId,
    setDatasets,
  } = useQueryStore();

  const [isLoading, setIsLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [newDatasetName, setNewDatasetName] = useState('');
  const [uploadingDataset, setUploadingDataset] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDatasets();
  }, [currentUserId]);

  const loadDatasets = async () => {
    setIsLoading(true);
    try {
      const data = await datasetApi.listDatasets(currentUserId);
      setDatasets(data);
      if (data.length > 0 && !currentDatasetId) {
        setDatasetId(data[0].dataset_id);
      }
    } catch (error) {
      console.error('Failed to load datasets:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateDataset = async () => {
    if (!newDatasetName.trim()) return;

    try {
      await datasetApi.createDataset(
        currentUserId,
        newDatasetName.toLowerCase().replace(/\s+/g, '_'),
        newDatasetName
      );
      setNewDatasetName('');
      setShowCreate(false);
      await loadDatasets();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create dataset');
    }
  };

  const handleDeleteDataset = async (datasetId: string) => {
    if (!confirm(`Delete dataset "${datasetId}"?`)) return;

    try {
      await datasetApi.deleteDataset(currentUserId, datasetId);
      if (currentDatasetId === datasetId) {
        setDatasetId(null);
      }
      await loadDatasets();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete dataset');
    }
  };

  const handleFileSelect = (datasetId: string) => {
    setUploadingDataset(datasetId);
    fileInputRef.current?.click();
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !uploadingDataset) return;

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      alert('Please upload a CSV file');
      setUploadingDataset(null);
      return;
    }

    setUploadProgress('Uploading...');
    
    try {
      const result = await datasetApi.uploadCSV(
        currentUserId,
        uploadingDataset,
        file
      );
      
      setUploadProgress(`✅ Successfully imported ${result.rows_imported} rows into table "${result.table_name}"`);
      
      // Clear after 3 seconds
      setTimeout(() => {
        setUploadProgress('');
        setUploadingDataset(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }, 3000);
      
      // Reload datasets to show updated schema
      await loadDatasets();
    } catch (error: any) {
      setUploadProgress('');
      alert(error.response?.data?.detail || 'Failed to upload CSV file');
      setUploadingDataset(null);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5" />
          <h2 className="text-xl font-semibold">Datasets</h2>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Dataset
        </button>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        onChange={handleFileUpload}
        className="hidden"
      />

      {/* Upload progress message */}
      {uploadProgress && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-800">
          {uploadProgress}
        </div>
      )}

      {showCreate && (
        <div className="mb-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <input
            type="text"
            value={newDatasetName}
            onChange={(e) => setNewDatasetName(e.target.value)}
            placeholder="Dataset name"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-2"
            onKeyPress={(e) => e.key === 'Enter' && handleCreateDataset()}
          />
          <div className="flex gap-2">
            <button
              onClick={handleCreateDataset}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Create
            </button>
            <button
              onClick={() => {
                setShowCreate(false);
                setNewDatasetName('');
              }}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <p className="text-gray-500">Loading datasets...</p>
      ) : datasets.length === 0 ? (
        <p className="text-gray-500">
          No datasets found. Create one to get started!
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {datasets.map((dataset) => (
            <div
              key={dataset.dataset_id}
              className={`p-4 border-2 rounded-lg transition-colors ${
                currentDatasetId === dataset.dataset_id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div 
                onClick={() => setDatasetId(dataset.dataset_id)}
                className="cursor-pointer"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-semibold">{dataset.name}</h3>
                    <p className="text-sm text-gray-500">{dataset.dataset_id}</p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteDataset(dataset.dataset_id);
                    }}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <button
                onClick={() => handleFileSelect(dataset.dataset_id)}
                className="w-full mt-2 px-3 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 flex items-center justify-center gap-2"
              >
                <Upload className="w-4 h-4" />
                Upload CSV
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

