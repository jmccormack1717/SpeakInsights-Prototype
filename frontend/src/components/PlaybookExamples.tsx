/** Playbook examples / gallery for quick testing and demos */
import { useQueryStore } from '../stores/queryStore';
import { Lightbulb } from 'lucide-react';

const EXAMPLES: { title: string; prompt: string; hint: string }[] = [
  {
    title: 'Overview',
    prompt: 'Describe this dataset to me like I am new to it.',
    hint: 'High-level summary of columns and numeric ranges.',
  },
  {
    title: 'Drivers of outcome',
    prompt: 'Which features are most strongly related to the main outcome or target in this dataset?',
    hint: 'Top drivers bar chart plus a focused risk curve for the strongest feature (if an outcome column exists).',
  },
  {
    title: 'Single feature distribution',
    prompt: 'Show me the distribution of an important numeric feature in this dataset.',
    hint: 'Histogram and summary stats for one numeric column (you can replace this with a specific feature name).',
  },
  {
    title: 'Relationship between two features',
    prompt: 'How are two key numeric features in this dataset related?',
    hint: 'Scatter plot and correlation (e.g., Feature A vs Feature B).',
  },
  {
    title: 'Compare groups',
    prompt: 'Compare two important groups in this dataset across key metrics.',
    hint: 'Group comparison with effect size (e.g., Group A vs Group B).',
  },
  {
    title: 'Outcome breakdown',
    prompt: 'How is the main outcome or target column distributed across the dataset?',
    hint: 'Outcome / class balance chart.',
  },
];

export function PlaybookExamples() {
  const { setPresetQuestion, currentDatasetId } = useQueryStore();

  const handleClick = (prompt: string) => {
    if (!currentDatasetId) return;
    setPresetQuestion(prompt);
    // Optionally scroll to the query input
    const el = document.getElementById('query-input');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  return (
    <div className="w-full bg-si-surface rounded-2xl border border-si-border/70 shadow-sm p-4 sm:p-5">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-8 h-8 rounded-lg bg-si-primary-soft flex items-center justify-center">
          <Lightbulb className="w-4 h-4 text-si-primary" />
        </div>
        <div>
          <h2 className="text-sm font-semibold text-si-text">Example questions</h2>
          <p className="text-xs text-si-muted">
            Try one of these to see different analysis playbooks in action.
          </p>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {EXAMPLES.map((ex) => (
          <button
            key={ex.title}
            type="button"
            onClick={() => handleClick(ex.prompt)}
            disabled={!currentDatasetId}
            className="text-left rounded-xl border border-si-border/60 bg-si-bg/80 px-3 py-2.5 text-xs hover:border-si-primary/80 hover:bg-si-primary-soft/40 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <div className="font-semibold text-si-text mb-1">{ex.title}</div>
            <div className="text-si-muted mb-1 line-clamp-2">{ex.prompt}</div>
            <div className="text-[10px] text-si-muted/80">{ex.hint}</div>
          </button>
        ))}
      </div>
    </div>
  );
}


