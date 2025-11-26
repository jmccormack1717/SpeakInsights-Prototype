/** Main application component */
import { useEffect, useState } from 'react';
import { Moon, Sun, PlayCircle } from 'lucide-react';
import { ResultsPanel } from './components/ResultsPanel';
import { DatasetSelector } from './components/DatasetSelector';
import { PlaybookExamples } from './components/PlaybookExamples';
import { AuthPanel } from './components/AuthPanel';
import { useAuthStore } from './stores/authStore';
import { useQueryStore } from './stores/queryStore';

type Theme = 'light' | 'dark';

function App() {
  const [theme, setTheme] = useState<Theme>('light');
  const [hasStarted, setHasStarted] = useState<boolean>(false);
  const { initializeFromStorage, user } = useAuthStore();
  const { setUserId } = useQueryStore();

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

  // Initialize auth from localStorage and sync user id into query store
  useEffect(() => {
    initializeFromStorage();
  }, [initializeFromStorage]);

  useEffect(() => {
    if (user?.userId) {
      setUserId(user.userId);
      setHasStarted(true);
      window.localStorage.setItem('si-started', 'true');
    } else {
      setUserId('default_user');
    }
  }, [user, setUserId]);

  // Initialize "started" flag from storage on first load
  useEffect(() => {
    const raw = window.localStorage.getItem('si-started');
    if (raw === 'true') {
      setHasStarted(true);
    }
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => {
      const next: Theme = prev === 'light' ? 'dark' : 'light';
      window.localStorage.setItem('si-theme', next);
      document.documentElement.classList.toggle('dark', next === 'dark');
      return next;
    });
  };

  const handleStartDemo = () => {
    setHasStarted(true);
    window.localStorage.setItem('si-started', 'true');
    setUserId('default_user');
  };

  const header = (
    <header className="bg-si-surface/70 backdrop-blur-xl border-b border-si-border/60 shadow-sm sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="relative w-11 h-11 rounded-2xl bg-si-surface shadow-si-soft flex items-center justify-center overflow-hidden border border-si-border/70">
            <img
              src="/icon.svg"
              alt="Speak Insights icon"
              className="w-9 h-9 object-contain"
            />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
              <span className="text-si-primary">Speak</span>
              <span className="text-si-primary-strong">Insights</span>
            </h1>
            <p className="text-xs sm:text-sm text-si-muted">
              Natural-language data analysis for any CSV dataset
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
  );

  if (!hasStarted) {
    return (
      <div className="min-h-screen bg-si-bg text-si-text transition-colors duration-300 flex flex-col">
        {header}
        {/* Landing hero with plenty of whitespace; wide hero copy on the left and large auth card on the right */}
        <main className="flex-1 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14 grid gap-10 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1.2fr)] items-stretch">
          <section className="space-y-6 flex flex-col justify-center">
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-si-text leading-snug max-w-3xl">
              <span className="block">Ask questions about your data,</span>
              <span className="block text-si-primary">get instant charts & insights.</span>
            </h2>
            <p className="text-sm sm:text-base text-si-muted max-w-2xl">
              Drop in a CSV or start with the built-in PIMA demo dataset. SpeakInsights turns your natural-language
              questions into visual summaries and AI-written analysis.
            </p>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={handleStartDemo}
                className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-si-primary to-si-primary-strong text-white px-5 py-2.5 text-sm font-medium shadow-md hover:shadow-lg"
              >
                <PlayCircle className="w-4 h-4" />
                <span>Try instant demo</span>
              </button>
              <span className="text-xs text-si-muted">
                No sign-in required. Or create an account on the right to save your own datasets.
              </span>
            </div>
          </section>

          <section className="space-y-4 flex flex-col justify-center">
            <div className="max-w-3xl w-full mx-auto">
              <AuthPanel onAuthenticated={handleStartDemo} />
            </div>
          </section>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-si-bg text-si-text transition-colors duration-300">
      {header}

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
        <DatasetSelector />
        <PlaybookExamples />
        <ResultsPanel />
      </main>
    </div>
  );
}

export default App;

