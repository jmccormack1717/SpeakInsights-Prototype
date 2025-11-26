/** Authentication card for the launch page: login / signup + optional demo CTA. */
import { useState } from 'react';
import { Lock, LogIn, UserPlus, Mail, PlayCircle } from 'lucide-react';
import { authApi } from '../services/api';
import { useAuthStore } from '../stores/authStore';
import { useQueryStore } from '../stores/queryStore';

type Mode = 'login' | 'signup';

interface AuthPanelProps {
  onAuthenticated?: () => void;
  onStartDemo?: () => void;
}

export function AuthPanel({ onAuthenticated, onStartDemo }: AuthPanelProps) {
  const [mode, setMode] = useState<Mode>('login');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { setAuth } = useAuthStore();
  const { setUserId } = useQueryStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setIsSubmitting(true);
    setError(null);

    try {
      if (mode === 'signup') {
        const res = await authApi.signup(email, password, fullName || undefined);
        setAuth(
          {
            userId: res.user_id,
            email: res.email,
            fullName: res.full_name,
          },
          res.access_token,
        );
        setUserId(res.user_id);
        onAuthenticated?.();
      } else {
        const res = await authApi.login(email, password);
        setAuth(
          {
            userId: res.user_id,
            email: res.email,
            fullName: res.full_name,
          },
          res.access_token,
        );
        setUserId(res.user_id);
        onAuthenticated?.();
      }
    } catch (err: any) {
      const msg =
        err?.response?.data?.detail ||
        (mode === 'signup' ? 'Sign up failed. Please try again.' : 'Login failed. Please check your credentials.');
      setError(typeof msg === 'string' ? msg : 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full bg-si-surface rounded-2xl border border-si-border/70 shadow-md p-6 sm:p-7 space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-si-primary-soft flex items-center justify-center">
            <Lock className="w-4 h-4 text-si-primary" />
          </div>
          <div>
            <h2 className="text-lg sm:text-xl font-semibold text-si-text">
              {mode === 'login' ? 'Sign in to SpeakInsights' : 'Create an account'}
            </h2>
            <p className="text-sm text-si-muted">
              Use your own user space while keeping the demo-friendly PIMA dataset.
            </p>
          </div>
        </div>
        <button
          type="button"
          className="text-[11px] sm:text-xs text-si-muted hover:text-si-primary transition-colors"
          onClick={() => {
            setMode((prev) => (prev === 'login' ? 'signup' : 'login'));
            setError(null);
          }}
        >
          {mode === 'login' ? (
            <span>
              New here? <span className="font-semibold">Create account</span>
            </span>
          ) : (
            <span>
              Already have an account? <span className="font-semibold">Log in</span>
            </span>
          )}
        </button>
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
        <div className="sm:col-span-1">
          <label className="block text-sm font-medium text-si-muted mb-1.5">Email</label>
          <div className="relative">
            <Mail className="w-4 h-4 text-si-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-si-border/70 bg-si-bg text-sm sm:text-base text-si-text focus:outline-none focus:ring-2 focus:ring-si-primary"
              required
            />
          </div>
        </div>
        {mode === 'signup' && (
          <div className="sm:col-span-1">
            <label className="block text-sm font-medium text-si-muted mb-1.5">Name (optional)</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Your name"
              className="w-full px-3.5 py-2.5 rounded-xl border border-si-border/70 bg-si-bg text-sm sm:text-base text-si-text focus:outline-none focus:ring-2 focus:ring-si-primary"
            />
          </div>
        )}
        <div className={mode === 'signup' ? 'sm:col-span-1' : 'sm:col-span-1'}>
          <label className="block text-sm font-medium text-si-muted mb-1.5">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="w-full px-3.5 py-2.5 rounded-xl border border-si-border/70 bg-si-bg text-sm sm:text-base text-si-text focus:outline-none focus:ring-2 focus:ring-si-primary"
            required
          />
        </div>
        <div className="sm:col-span-1 flex justify-end">
          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex items-center justify-center px-5 py-2.5 rounded-xl bg-gradient-to-r from-si-primary to-si-primary-strong text-white text-sm font-medium shadow-sm hover:shadow-md disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </div>
      </form>

      <div className="pt-3 border-t border-si-border/60 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <p className="text-[11px] sm:text-xs text-si-muted">
          Or, explore instantly with the built-in demo dataset.
        </p>
        <button
          type="button"
          onClick={onStartDemo}
          className="inline-flex items-center gap-1.5 rounded-full border border-si-primary/70 text-si-primary px-3.5 py-1.5 text-[11px] sm:text-xs font-medium hover:bg-si-primary-soft/40"
        >
          <PlayCircle className="w-3.5 h-3.5" />
          <span>Start instant demo</span>
        </button>
      </div>

      {error && <p className="mt-2 text-xs text-red-500">{error}</p>}
    </div>
  );
}


