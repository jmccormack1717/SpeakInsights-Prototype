/** Main application component */
import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';
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
  const { initializeFromStorage, user, logout } = useAuthStore();
  const { setUserId, reset: resetQueryStore } = useQueryStore();

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

  const handleLogout = () => {
    logout();
    resetQueryStore();
    setUserId('default_user');
    setHasStarted(false);
    window.localStorage.removeItem('si-started');
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

        <div className="flex items-center gap-2 sm:gap-3">
          {user && (
            <button
              type="button"
              onClick={handleLogout}
              className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-si-border/80 bg-si-surface/80 px-3 py-1.5 text-xs text-si-muted hover:text-si-text hover:border-red-400 hover:bg-red-500/10 transition-colors"
            >
              <span>Logout</span>
            </button>
          )}
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
      </div>
    </header>
  );

  if (!hasStarted) {
    return (
      <div className="min-h-screen bg-si-bg text-si-text transition-colors duration-300 flex flex-col">
        {header}
        {/* Clean launch page with a single wide auth card (login/signup) and demo CTA */}
        <main className="flex-1 max-w-6xl mx-auto px-6 sm:px-10 lg:px-16 py-10 sm:py-16 space-y-8 sm:space-y-10">
          {/* Intro copy */}
          <section className="space-y-4 text-center">
            <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-si-text leading-tight">
              <span className="block">Ask questions about your data,</span>
              <span className="block text-si-primary">get instant charts & insights.</span>
            </h2>
            <p className="text-sm sm:text-base text-si-muted max-w-2xl mx-auto">
              Log in to use your own datasets, or jump straight into the demo—one clean place to talk to your data.
            </p>
          </section>

          {/* Single, extra-wide auth card: login/signup + demo CTA */}
          <section className="max-w-4xl w-full mx-auto">
            <AuthPanel onAuthenticated={handleStartDemo} onStartDemo={handleStartDemo} />
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

