/** Panel displaying textual analysis and insights */
import type { TextualAnalysis } from '../types';
import { Lightbulb, TrendingUp, AlertCircle, Sparkles, MessageCircle } from 'lucide-react';
import { useQueryStore } from '../stores/queryStore';

export function AnalysisPanel({ analysis }: { analysis: TextualAnalysis }) {
  const { setPresetQuestion, currentDatasetId } = useQueryStore();

  const handleFollowUpClick = (question: string) => {
    if (!currentDatasetId) return;
    setPresetQuestion(question);

    const el = document.getElementById('query-input');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      // Try to focus the input for quicker editing/submission
      (el as HTMLInputElement).focus?.();
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200/60 p-6 sm:p-8 space-y-6">
      <div className="flex items-center gap-3 pb-4 border-b border-gray-100">
        <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg flex items-center justify-center shadow-sm">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <h2 className="text-xl font-bold text-gray-900">AI Analysis & Insights</h2>
      </div>

      {/* Executive Summary */}
      {analysis.summary && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-5 border-l-4 border-indigo-500">
          <h3 className="text-sm font-semibold text-indigo-900 mb-2 uppercase tracking-wide">Executive Summary</h3>
          <p className="text-gray-800 leading-relaxed">{analysis.summary}</p>
        </div>
      )}

      {/* Key Findings */}
      {analysis.key_findings && analysis.key_findings.length > 0 && (
        <div>
          <h3 className="text-base font-semibold mb-3 flex items-center gap-2 text-gray-800">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            Key Findings
          </h3>
          <ul className="space-y-2.5">
            {analysis.key_findings.map((finding, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                  <span className="text-blue-600 text-xs font-semibold">{idx + 1}</span>
                </div>
                <span className="text-gray-700 leading-relaxed">{finding}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Patterns */}
      {analysis.patterns && analysis.patterns.length > 0 && (
        <div>
          <h3 className="text-base font-semibold mb-3 flex items-center gap-2 text-gray-800">
            <Lightbulb className="w-5 h-5 text-amber-500" />
            Notable Patterns
          </h3>
          <ul className="space-y-2.5">
            {analysis.patterns.map((pattern, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className="flex-shrink-0 w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
                <span className="text-gray-700 leading-relaxed">{pattern}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations && analysis.recommendations.length > 0 && (
        <div className="bg-green-50 rounded-lg p-5 border border-green-200">
          <h3 className="text-base font-semibold mb-3 flex items-center gap-2 text-green-900">
            <AlertCircle className="w-5 h-5 text-green-600" />
            Recommendations
          </h3>
          <ul className="space-y-2.5">
            {analysis.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className="flex-shrink-0 w-2 h-2 bg-green-600 rounded-full mt-2"></div>
                <span className="text-green-900 leading-relaxed">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Follow-up questions */}
      {analysis.follow_ups && analysis.follow_ups.length > 0 && (
        <div className="pt-4 border-t border-gray-100">
          <h3 className="text-sm font-semibold mb-2 flex items-center gap-2 text-gray-800">
            <MessageCircle className="w-4 h-4 text-si-primary" />
            Helpful follow-up questions
          </h3>
          <ul className="flex flex-wrap gap-2">
            {analysis.follow_ups.map((q, idx) => (
              <li
                key={idx}
                className="px-3 py-1.5 text-xs rounded-full bg-si-primary-soft text-si-primary-strong border border-si-primary/20 cursor-pointer hover:bg-si-primary-soft/70 hover:border-si-primary/40 transition-colors"
                onClick={() => handleFollowUpClick(q)}
                role="button"
                aria-label={`Ask follow-up: ${q}`}
              >
                {q}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

