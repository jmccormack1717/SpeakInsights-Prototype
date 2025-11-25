/** Dataset selector component - MVP: Hardcoded single dataset */
import { useEffect } from 'react';
import { Database, CheckCircle2 } from 'lucide-react';
import { useQueryStore } from '../stores/queryStore';

// Hardcoded dataset for MVP
const HARDCODED_DATASET = {
  dataset_id: 'mvp_dataset',
  name: 'Diabetes Dataset',
};

export function DatasetSelector() {
  const {
    currentDatasetId,
    setDatasetId,
  } = useQueryStore();

  useEffect(() => {
    // Auto-select the hardcoded dataset
    if (!currentDatasetId || currentDatasetId !== HARDCODED_DATASET.dataset_id) {
      setDatasetId(HARDCODED_DATASET.dataset_id);
    }
  }, [currentDatasetId, setDatasetId]);

  return (
    <div className="w-full">
      <div className="flex items-center gap-2 mb-3">
        <Database className="w-5 h-5 text-si-primary" />
        <h2 className="text-lg font-semibold text-si-text">Active dataset</h2>
      </div>

      <div className="bg-si-surface rounded-2xl shadow-si-soft/60 border border-si-border/70 p-5 hover:shadow-si-soft transition-shadow duration-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-si-primary to-si-primary-strong rounded-2xl flex items-center justify-center shadow-md">
              <Database className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-si-text text-lg">{HARDCODED_DATASET.name}</h3>
              <p className="text-sm text-si-muted mt-0.5">Ready to analyze and visualize</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 text-emerald-400 text-sm font-medium rounded-full border border-emerald-400/40">
            <CheckCircle2 className="w-4 h-4" />
            <span>Active</span>
          </div>
        </div>
      </div>
    </div>
  );
}

