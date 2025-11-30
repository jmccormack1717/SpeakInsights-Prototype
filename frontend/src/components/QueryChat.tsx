/** Main query chat interface */
import { useEffect, useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { useQueryStore } from '../stores/queryStore';
import { queryApi } from '../services/api';
import type { QueryRequest } from '../types';

export function QueryChat() {
  const [question, setQuestion] = useState('');
  const { 
    isLoading, 
    setLoading, 
    setError, 
    addTurn,
    attachResponseToTurn,
    currentUserId,
    currentDatasetId,
    presetQuestion,
    setPresetQuestion,
  } = useQueryStore();

  // If another component sets a preset question (e.g. from examples),
  // populate the input with it.
  useEffect(() => {
    if (presetQuestion) {
      setQuestion(presetQuestion);
      setPresetQuestion(null);
    }
  }, [presetQuestion, setPresetQuestion]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim() || !currentDatasetId) {
      setError('Please enter a question and select a dataset');
      return;
    }

    const trimmed = question.trim();
    // Append a new turn so it shows up immediately in the conversation
    const turnId = addTurn(trimmed);

    setLoading(true);
    setError(null);

    try {
      const request: QueryRequest = {
        user_id: currentUserId,
        dataset_id: currentDatasetId,
        query: trimmed,
      };

      const response = await queryApi.executeQuery(request);
      attachResponseToTurn(turnId, response);
      setQuestion(''); // Clear input after successful analysis
    } catch (error: unknown) {
      // Log full error to console for debugging, but show a friendly message to the user
      console.error('Analysis error:', error);
      setError('We couldn\'t analyze your data just now. Please try a slightly different question.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      <div className="mb-3">
        <label className="text-sm font-medium text-si-muted">Ask about your data</label>
      </div>
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1 relative">
          <input
            id="query-input"
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder={
              currentDatasetId
                ? 'Ask a question about your data...'
                : 'Please select a dataset first'
            }
            disabled={isLoading || !currentDatasetId}
            className="w-full px-5 py-4 pr-12 bg-si-surface border border-si-border rounded-2xl focus:outline-none focus:ring-2 focus:ring-si-primary focus:border-transparent disabled:bg-si-surface/60 disabled:cursor-not-allowed text-si-text placeholder:text-si-muted shadow-sm transition-all duration-200"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading || !question.trim() || !currentDatasetId}
          className="px-6 py-4 bg-gradient-to-r from-si-primary to-si-primary-strong text-white rounded-2xl hover:from-si-primary-strong hover:to-si-primary disabled:from-slate-500 disabled:to-slate-600 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium shadow-md hover:shadow-lg transition-all min-w-[120px]"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="hidden sm:inline">Processing</span>
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span>Analyze</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}

