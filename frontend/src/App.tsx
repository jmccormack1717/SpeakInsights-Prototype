/** Main application component */
import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';
import { QueryChat } from './components/QueryChat';
import { ResultsPanel } from './components/ResultsPanel';
import { DatasetSelector } from './components/DatasetSelector';

type Theme = 'light' | 'dark';

function App() {
  const [theme, setTheme] = useState<Theme>('light');

  // Initialize theme from localStorage / OS preference
  useEffect(() => {
    const stored = window.localStorage.getItem('si-theme') as Theme | null;
    if (stored === 'light' || stored === 'dark') {
      setTheme(stored);
      document.documentElement.classList.toggle('dark', stored === 'dark');
      return;
    }

    const prefersDark = window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initial: Theme = prefersDark ? 'dark' : 'light';
    setTheme(initial);
    document.documentElement.classList.toggle('dark', initial === 'dark');
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => {
      const next: Theme = prev === 'light' ? 'dark' : 'light';
      window.localStorage.setItem('si-theme', next);
      document.documentElement.classList.toggle('dark', next === 'dark');
      return next;
    });
  };

  return (
    <div className="min-h-screen bg-si-bg text-si-text transition-colors duration-300">
      <header className="bg-si-surface/70 backdrop-blur-xl border-b border-si-border/60 shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="relative w-11 h-11 rounded-2xl bg-gradient-to-br from-si-primary to-si-primary-strong shadow-si-soft flex items-center justify-center overflow-hidden">
              <div className="absolute inset-[18%] rounded-lg bg-white/10" />
              <span className="relative text-white font-bold text-xl tracking-tight">
                SI
              </span>
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
                <span className="text-si-primary">Speak</span>
                <span className="text-si-primary-strong">Insights</span>
              </h1>
              <p className="text-xs sm:text-sm text-si-muted">
                Prompt-driven data stories from your own dataset
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={toggleTheme}
            className="inline-flex items-center gap-2 rounded-full border border-si-border/80 bg-si-surface/80 px-3 py-1.5 text-xs sm:text-sm text-si-muted hover:text-si-text hover:border-si-primary/70 hover:bg-si-primary-soft/40 shadow-sm transition-colors duration-200"
          >
            {theme === 'dark' ? (
              <>
                <Sun className="w-4 h-4 text-yellow-300" />
                <span className="hidden sm:inline">Light mode</span>
              </>
            ) : (
              <>
                <Moon className="w-4 h-4 text-si-primary-strong" />
                <span className="hidden sm:inline">Dark mode</span>
              </>
            )}
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
        <DatasetSelector />
        <QueryChat />
        <ResultsPanel />
      </main>
    </div>
  );
}

export default App;

