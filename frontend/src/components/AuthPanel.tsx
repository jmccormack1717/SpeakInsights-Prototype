/** Authentication card for the launch page: login / signup + optional demo CTA. */
import { useState } from 'react';
import { Lock, Mail, PlayCircle } from 'lucide-react';
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
    } catch (err: unknown) {
      let msg: string;
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { data?: { detail?: unknown } } };
        msg = typeof axiosError.response?.data?.detail === 'string' 
          ? axiosError.response.data.detail
          : (mode === 'signup' ? 'Sign up failed. Please try again.' : 'Login failed. Please check your credentials.');
      } else {
        msg = mode === 'signup' ? 'Sign up failed. Please try again.' : 'Login failed. Please check your credentials.';
      }
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full bg-si-surface rounded-3xl border border-si-border/70 shadow-lg shadow-black/20 p-6 sm:p-7 space-y-5">
      {/* Logo + title row */}
      <div className="flex flex-col items-center space-y-2 mb-1">
        <div className="w-10 h-10 rounded-2xl bg-si-primary-soft flex items-center justify-center">
          <Lock className="w-5 h-5 text-si-primary" />
        </div>
        <div className="text-center space-y-1">
          <h2 className="text-lg sm:text-xl font-semibold text-si-text">
            {mode === 'login' ? 'Sign in to SpeakInsights' : 'Create your SpeakInsights account'}
          </h2>
        </div>
      </div>

      {/* Form fields */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="space-y-1.5">
          <label className="block text-xs font-medium text-si-muted">Email</label>
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
          <div className="space-y-1.5">
            <label className="block text-xs font-medium text-si-muted">Name (optional)</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Your name"
              className="w-full px-3.5 py-2.5 rounded-xl border border-si-border/70 bg-si-bg text-sm sm:text-base text-si-text focus:outline-none focus:ring-2 focus:ring-si-primary"
            />
          </div>
        )}

        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label className="block text-xs font-medium text-si-muted">Password</label>
            {/* Placeholder for future "Forgot password?" link */}
          </div>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="w-full px-3.5 py-2.5 rounded-xl border border-si-border/70 bg-si-bg text-sm sm:text-base text-si-text focus:outline-none focus:ring-2 focus:ring-si-primary"
            required
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="mt-2 w-full inline-flex items-center justify-center px-5 py-2.5 rounded-xl bg-gradient-to-r from-si-primary to-si-primary-strong text-white text-sm font-medium shadow-md hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
        </button>
      </form>

      {/* Demo CTA */}
      <div className="pt-4 border-t border-si-border/60 space-y-3 text-center">
        <p className="text-[11px] sm:text-xs text-si-muted">
          Just want to see it in action first?
        </p>
        <button
          type="button"
          onClick={onStartDemo}
          className="inline-flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-si-primary to-si-primary-strong text-white px-6 py-2.5 text-xs sm:text-sm font-medium shadow-md hover:shadow-lg"
        >
          <PlayCircle className="w-4 h-4" />
          <span>Start instant demo</span>
        </button>
      </div>

      {/* Mode switch */}
      <div className="pt-2 text-center">
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
              Don&apos;t have an account? <span className="font-semibold">Create one</span>
            </span>
          ) : (
            <span>
              Already have an account? <span className="font-semibold">Sign in</span>
            </span>
          )}
        </button>
      </div>

      {error && <p className="mt-2 text-xs text-red-500 text-center">{error}</p>}
    </div>
  );
}


