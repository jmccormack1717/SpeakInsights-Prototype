/** Dataset selector component - built-in PIMA dataset + custom CSV upload */
import { useEffect, useState, type ChangeEvent } from 'react';
import { Database, CheckCircle2, Upload } from 'lucide-react';
import { useQueryStore } from '../stores/queryStore';
import { datasetApi } from '../services/api';
import type { Dataset } from '../types';

// Built-in PIMA diabetes dataset
const PIMA_DATASET: Dataset = {
  dataset_id: 'mvp_dataset',
  name: 'PIMA Diabetes Dataset',
};

export function DatasetSelector() {
  const {
    currentDatasetId,
    currentUserId,
    setDatasetId,
    datasets,
    setDatasets,
    setError,
  } = useQueryStore();

  const [isUploading, setIsUploading] = useState(false);

  // Ensure the built-in PIMA dataset is always present as an option
  useEffect(() => {
    const loadDatasets = async () => {
      try {
        const list = await datasetApi.listDatasets(currentUserId);
        const withPima = [
          PIMA_DATASET,
          ...list.filter((d) => d.dataset_id !== PIMA_DATASET.dataset_id),
        ];
        setDatasets(withPima);

        // Default to PIMA if nothing selected yet
        if (!currentDatasetId) {
          setDatasetId(PIMA_DATASET.dataset_id);
        }
      } catch (err) {
        console.error('Failed to load datasets', err);
      }
    };

    void loadDatasets();
  }, [currentUserId, currentDatasetId, setDatasetId, setDatasets]);

  const handleUsePima = () => {
    setDatasetId(PIMA_DATASET.dataset_id);
  };

  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      const baseName = file.name.replace(/\.[^/.]+$/, '');
      const safeId = baseName.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 40) || 'custom_dataset';

      // Create dataset (if it doesn't already exist)
      await datasetApi.createDataset(currentUserId, safeId, baseName);

      // Upload CSV into that dataset
      const uploadResult = await datasetApi.uploadCSV(currentUserId, safeId, file);

      // If we dropped any mostly-empty columns, surface a friendly info message
      if (uploadResult.dropped_column_count && uploadResult.dropped_column_count > 0) {
        const count = uploadResult.dropped_column_count;
        const colList =
          uploadResult.dropped_columns && uploadResult.dropped_columns.length > 0
            ? ` (${uploadResult.dropped_columns.join(', ')})`
            : '';
        setError(
          `Imported your dataset and removed ${count} mostly-empty column${
            count > 1 ? 's' : ''
          } due to missing data${colList}.`,
        );
      }

      // Refresh list and select the new dataset
      const list = await datasetApi.listDatasets(currentUserId);
      const withPima = [
        PIMA_DATASET,
        ...list.filter((d) => d.dataset_id !== PIMA_DATASET.dataset_id),
      ];
      setDatasets(withPima);
      setDatasetId(safeId);
    } catch (err) {
      console.error('Upload failed', err);
      setError('We could not import that CSV. Please check the file and try again.');
    } finally {
      setIsUploading(false);
      // Reset file input so the same file can be re-selected if needed
      e.target.value = '';
    }
  };

  const activeDataset = datasets.find((d) => d.dataset_id === currentDatasetId) || PIMA_DATASET;

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center gap-2 mb-1">
        <Database className="w-5 h-5 text-si-primary" />
        <h2 className="text-lg font-semibold text-si-text">Dataset</h2>
      </div>
      <p className="text-xs text-si-muted mb-2">
        Choose the built-in PIMA diabetes dataset or import your own CSV to analyze.
        For this demo (running on free hosting), CSVs up to about 50MB / ~100k rows tend to work best.
      </p>

      {/* Built-in PIMA card */}
      <div className="bg-si-surface rounded-2xl shadow-si-soft/60 border border-si-border/70 p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-br from-si-primary to-si-primary-strong rounded-2xl flex items-center justify-center shadow-md">
            <Database className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-si-text text-lg">{PIMA_DATASET.name}</h3>
            <p className="text-sm text-si-muted mt-0.5">
              Cleaned medical dataset, great for testing correlations and risk patterns.
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={handleUsePima}
          className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
            activeDataset.dataset_id === PIMA_DATASET.dataset_id
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-400/40 flex items-center gap-1'
              : 'bg-transparent text-si-text border-si-border/70 hover:border-si-primary hover:text-si-primary'
          }`}
        >
          {activeDataset.dataset_id === PIMA_DATASET.dataset_id && <CheckCircle2 className="w-4 h-4" />}
          {activeDataset.dataset_id === PIMA_DATASET.dataset_id ? 'Active' : 'Use this dataset'}
        </button>
      </div>

      {/* Custom CSV upload card */}
      <div className="bg-si-surface rounded-2xl border border-dashed border-si-border/70 p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Upload className="w-5 h-5 text-si-primary" />
            <h3 className="font-semibold text-si-text text-lg">Import your own CSV</h3>
          </div>
          <p className="text-sm text-si-muted">
            Upload any tabular CSV file. We&apos;ll infer the schema and run the same analyses.
          </p>
          {datasets.length > 1 && (
            <p className="text-xs text-si-muted mt-2">
              Recently used:{' '}
              {datasets
                .filter((d: Dataset) => d.dataset_id !== PIMA_DATASET.dataset_id)
                .slice(0, 3)
                .map((d: Dataset) => d.name)
                .join(', ')}
            </p>
          )}
        </div>
        <label className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-si-primary text-white text-xs font-medium cursor-pointer hover:bg-si-primary-strong transition-colors">
          <Upload className="w-4 h-4" />
          <span>{isUploading ? 'Uploading...' : 'Upload CSV'}</span>
          <input
            type="file"
            accept=".csv,text/csv"
            className="hidden"
            onChange={handleFileChange}
            disabled={isUploading}
          />
        </label>
      </div>

      {isUploading && (
        <p className="text-xs text-si-muted">
          Importing and indexing your CSV. This may take a few moments for larger files.
        </p>
      )}

      {/* Active dataset summary */}
      <div className="text-xs text-si-muted">
        <span className="font-medium text-si-text">Active:</span>{' '}
        <span>{activeDataset.name}</span>
      </div>
    </div>
  );
}

