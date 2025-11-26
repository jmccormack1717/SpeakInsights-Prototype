/** Results panel showing visualization and analysis */
import { useQueryStore } from '../stores/queryStore';
import { ChartRenderer } from './ChartRenderer';
import { AnalysisPanel } from './AnalysisPanel';
import { Loader2 } from 'lucide-react';

export function ResultsPanel() {
  const { history, error, isLoading } = useQueryStore();
  const hasTurns = history.length > 0;

  if (!hasTurns && isLoading) {
    return (
      <div className="w-full mt-8 py-12 flex flex-col items-center justify-center gap-4 bg-si-surface rounded-2xl border border-si-border/70 shadow-si-soft">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-si-primary-soft">
          <Loader2 className="w-6 h-6 text-si-primary animate-spin" />
        </div>
        <div className="text-center px-4 max-w-xl">
          <p className="text-sm font-medium text-si-text">
            Analyzing your dataset and preparing visual insights...
          </p>
          <p className="text-xs text-si-muted mt-1">
            We&apos;re running analysis playbooks on your data and choosing charts that best match your question.
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full mt-6 p-5 bg-red-500/10 border-l-4 border-red-500 rounded-xl shadow-sm">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <svg className="w-5 h-5 text-red-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-red-800 mb-1">Something went wrong</h3>
            <p className="text-sm text-red-700">
              {error || 'We had trouble analyzing your data. Please try asking your question a little differently.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!hasTurns) {
    return (
      <div className="w-full mt-8 text-center py-12">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-si-primary-soft mb-4">
          <svg className="w-8 h-8 text-si-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <p className="text-si-muted text-lg">Ask a question to see insights</p>
        <p className="text-si-muted text-sm mt-2">We\'ll analyze your data and show a visual story</p>
      </div>
    );
  }

  return (
    <div className="w-full mt-6 space-y-4">
      {history.map((turn, idx) => {
        const isLast = idx === history.length - 1;
        const response = turn.response;
        const secondaryCharts = response?.extra_visualizations || [];

        return (
          <div
            key={turn.id}
            className="space-y-3 border border-si-border/60 rounded-2xl bg-si-surface/60 shadow-sm p-4 sm:p-5"
          >
            {/* User question */}
            <div className="flex justify-end">
              <div className="max-w-[80%] rounded-2xl bg-si-primary text-white px-4 py-2 text-sm shadow-sm">
                {turn.question}
              </div>
            </div>

            {/* Loading state for this turn */}
            {!response && isLast && isLoading && (
              <div className="flex items-center gap-2 text-xs text-si-muted mt-1">
                <Loader2 className="w-4 h-4 animate-spin text-si-primary" />
                <span>Analyzing your data for this question…</span>
              </div>
            )}

            {/* Response content when ready */}
            {response && (
              <div className="space-y-4">
                <div className="bg-si-elevated rounded-2xl shadow-si-soft border border-si-border/70 p-4 sm:p-6">
                  <ChartRenderer config={response.visualization} />
                </div>

                {secondaryCharts.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {secondaryCharts.map((viz, vIdx) => (
                      <div
                        key={vIdx}
                        className="bg-si-surface rounded-2xl shadow-sm border border-si-border/60 p-4"
                      >
                        <ChartRenderer config={viz} />
                      </div>
                    ))}
                  </div>
                )}

                <AnalysisPanel analysis={response.analysis} />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

