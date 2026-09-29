import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { ShieldCheck, Lock, Mail, User, AlertCircle, ArrowRight, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const from = (location.state as any)?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError('Please enter both username/email and password.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const res = await api.login(username.trim(), password);
      login(res.access_token, res.user);
      const requestedPath = (location.state as any)?.from?.pathname;
      const defaultPath = res.user.role === 'EMPLOYEE' ? '/employee-portal' : '/';
      const destination = requestedPath && requestedPath !== '/' ? requestedPath : defaultPath;
      navigate(destination, { replace: true });
    } catch (err: any) {
      console.error('Login failure:', err);
      setError(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cloud flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center h-14 w-14 rounded-2xl bg-electric-600 text-white font-heading font-extrabold text-2xl shadow-lg mb-4">
          S
        </div>
        <h2 className="text-2xl font-bold font-heading text-obsidian tracking-tight">
          SkillSprint <span className="text-electric-600">AI</span>
        </h2>
        <p className="mt-1 text-xs font-mono text-obsidian-400 uppercase tracking-wider">
          Enterprise Onboarding Intelligence Platform
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-modal rounded-2xl border border-cloud-200 sm:px-10">
          <div className="mb-6 pb-4 border-b border-cloud-200">
            <h3 className="text-base font-bold text-obsidian font-heading">Sign In to Your Account</h3>
            <p className="text-xs text-obsidian-400">Enter your credentials to access protected onboarding workflows.</p>
          </div>

          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2.5 animate-in fade-in">
              <AlertCircle className="h-4 w-4 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Authentication Error</span>
                <p className="text-[11px] text-rose-700 mt-0.5">{error}</p>
              </div>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-obsidian mb-1">
                Username or Work Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-obsidian-400">
                  <User className="h-4 w-4" />
                </div>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin@skillsprint.ai"
                  className="w-full pl-9 pr-3 py-2 text-xs bg-cloud-50 border border-cloud-300 rounded-xl text-obsidian focus:outline-none focus:ring-2 focus:ring-electric-600 focus:bg-white transition-all placeholder:text-obsidian-300"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-obsidian mb-1">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-obsidian-400">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-9 pr-3 py-2 text-xs bg-cloud-50 border border-cloud-300 rounded-xl text-obsidian focus:outline-none focus:ring-2 focus:ring-electric-600 focus:bg-white transition-all placeholder:text-obsidian-300"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 py-2.5 px-4 bg-electric-600 hover:bg-electric-700 text-white font-semibold text-xs rounded-xl shadow-subtle flex items-center justify-center gap-2 transition-all disabled:opacity-60"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-cloud-200 text-center">
            <p className="text-xs text-obsidian-400">
              New employee?{' '}
              <Link to="/signup" className="font-semibold text-electric-600 hover:underline">
                Register with Enterprise Email
              </Link>
            </p>
          </div>
        </div>

        {/* Footnote */}
        <div className="mt-6 text-center text-[11px] text-obsidian-400 font-mono">
          <div className="flex items-center justify-center gap-1">
            <ShieldCheck className="h-3.5 w-3.5 text-teal-600" />
            <span>Deterministic Ground-Truth Python Verification Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};
