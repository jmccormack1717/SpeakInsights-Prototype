/** Simple authentication card for signup / login */
import { useState } from 'react';
import { Lock, LogIn, UserPlus, Mail } from 'lucide-react';
import { authApi } from '../services/api';
import { useAuthStore } from '../stores/authStore';
import { useQueryStore } from '../stores/queryStore';

type Mode = 'login' | 'signup';

export function AuthPanel() {
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
    <div className="w-full bg-si-surface rounded-2xl border border-si-border/70 shadow-sm p-4 sm:p-5">
      <div className="flex items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-si-primary-soft flex items-center justify-center">
            <Lock className="w-4 h-4 text-si-primary" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-si-text">
              {mode === 'login' ? 'Sign in to personalize datasets' : 'Create an account'}
            </h2>
            <p className="text-xs text-si-muted">
              Use your own user space while keeping the demo-friendly PIMA dataset.
            </p>
          </div>
        </div>
        <div className="inline-flex rounded-full bg-si-bg border border-si-border/80 p-0.5 text-[11px]">
          <button
            type="button"
            onClick={() => setMode('login')}
            className={`px-2 py-1 rounded-full flex items-center gap-1 ${
              mode === 'login' ? 'bg-si-primary text-white' : 'text-si-muted'
            }`}
          >
            <LogIn className="w-3 h-3" />
            <span>Sign in</span>
          </button>
          <button
            type="button"
            onClick={() => setMode('signup')}
            className={`px-2 py-1 rounded-full flex items-center gap-1 ${
              mode === 'signup' ? 'bg-si-primary text-white' : 'text-si-muted'
            }`}
          >
            <UserPlus className="w-3 h-3" />
            <span>Sign up</span>
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
        <div className="sm:col-span-1">
          <label className="block text-xs font-medium text-si-muted mb-1">Email</label>
          <div className="relative">
            <Mail className="w-3.5 h-3.5 text-si-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full pl-8 pr-3 py-2 rounded-xl border border-si-border/70 bg-si-bg text-sm text-si-text focus:outline-none focus:ring-2 focus:ring-si-primary"
              required
            />
          </div>
        </div>
        {mode === 'signup' && (
          <div className="sm:col-span-1">
            <label className="block text-xs font-medium text-si-muted mb-1">Name (optional)</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Your name"
              className="w-full px-3 py-2 rounded-xl border border-si-border/70 bg-si-bg text-sm text-si-text focus:outline-none focus:ring-2 focus:ring-si-primary"
            />
          </div>
        )}
        <div className={mode === 'signup' ? 'sm:col-span-1' : 'sm:col-span-1'}>
          <label className="block text-xs font-medium text-si-muted mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="w-full px-3 py-2 rounded-xl border border-si-border/70 bg-si-bg text-sm text-si-text focus:outline-none focus:ring-2 focus:ring-si-primary"
            required
          />
        </div>
        <div className="sm:col-span-1 flex justify-end">
          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex items-center justify-center px-4 py-2 rounded-xl bg-gradient-to-r from-si-primary to-si-primary-strong text-white text-xs font-medium shadow-sm hover:shadow-md disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </div>
      </form>

      {error && <p className="mt-2 text-xs text-red-500">{error}</p>}
    </div>
  );
}


