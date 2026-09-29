import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, Mail, User, Lock, IdCard, AlertCircle, CheckCircle2, Loader2, ArrowRight } from 'lucide-react';
import { api } from '../services/api';

export const SignupPage: React.FC = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [employeeId, setEmployeeId] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);

    if (!email.trim() || !username.trim() || !password) {
      setError('Please fill out all required fields.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setIsLoading(true);

    try {
      const res = await api.signup({
        email: email.trim(),
        username: username.trim(),
        password,
        employee_id: employeeId.trim() || undefined
      });

      setSuccessMsg(
        `Employee registration successful for ${res.username} (${res.email})! Your assigned role is ${res.role}. Redirecting to login...`
      );

      setTimeout(() => {
        navigate('/login');
      }, 2500);
    } catch (err: any) {
      console.error('Signup error:', err);
      setError(err.message || 'Registration rejected. Please verify your company email address.');
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
          Employee Registration
        </h2>
        <p className="mt-1 text-xs font-mono text-obsidian-400 uppercase tracking-wider">
          Verified Apex Global Solutions Staff Only
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        {/* Employee Verification Guarantee Banner */}
        <div className="mb-4 p-3.5 rounded-xl bg-teal-50 border border-teal-200 text-teal-900 text-xs flex items-start gap-2.5">
          <Shield className="h-4 w-4 text-teal-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Strict Employee Verification Policy</span>
            <p className="text-[11px] text-teal-800 mt-0.5">
              Registration requires an active company employee record matching your work email. Account roles are automatically provisioned from enterprise records.
            </p>
          </div>
        </div>

        <div className="bg-white py-8 px-6 shadow-modal rounded-2xl border border-cloud-200 sm:px-10">
          {successMsg ? (
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs space-y-2 text-center animate-in fade-in">
              <CheckCircle2 className="h-8 w-8 text-emerald-600 mx-auto" />
              <h4 className="font-bold text-sm text-emerald-950">Registration Complete</h4>
              <p className="text-xs text-emerald-800">{successMsg}</p>
            </div>
          ) : (
            <>
              {error && (
                <div className="mb-5 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2.5 animate-in fade-in">
                  <AlertCircle className="h-4 w-4 text-rose-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold">Registration Rejected</span>
                    <p className="text-[11px] text-rose-700 mt-0.5">{error}</p>
                  </div>
                </div>
              )}

              <form className="space-y-4" onSubmit={handleSubmit}>
                <div>
                  <label className="block text-xs font-semibold text-obsidian mb-1">
                    Company Work Email <span className="text-rose-500">*</span>
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-obsidian-400">
                      <Mail className="h-4 w-4" />
                    </div>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="sarah.connor@skillsprint.ai"
                      className="w-full pl-9 pr-3 py-2 text-xs bg-cloud-50 border border-cloud-300 rounded-xl text-obsidian focus:outline-none focus:ring-2 focus:ring-electric-600 focus:bg-white transition-all placeholder:text-obsidian-300"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-obsidian mb-1">
                    Desired Username <span className="text-rose-500">*</span>
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
                      placeholder="sarah_connor"
                      className="w-full pl-9 pr-3 py-2 text-xs bg-cloud-50 border border-cloud-300 rounded-xl text-obsidian focus:outline-none focus:ring-2 focus:ring-electric-600 focus:bg-white transition-all placeholder:text-obsidian-300"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-obsidian mb-1">
                    Employee ID <span className="text-obsidian-400 font-normal">(Optional)</span>
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-obsidian-400">
                      <IdCard className="h-4 w-4" />
                    </div>
                    <input
                      type="text"
                      value={employeeId}
                      onChange={(e) => setEmployeeId(e.target.value)}
                      placeholder="EMP-005"
                      className="w-full pl-9 pr-3 py-2 text-xs bg-cloud-50 border border-cloud-300 rounded-xl text-obsidian focus:outline-none focus:ring-2 focus:ring-electric-600 focus:bg-white transition-all placeholder:text-obsidian-300"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-obsidian mb-1">
                      Password <span className="text-rose-500">*</span>
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
                        placeholder="••••••••"
                        className="w-full pl-9 pr-3 py-2 text-xs bg-cloud-50 border border-cloud-300 rounded-xl text-obsidian focus:outline-none focus:ring-2 focus:ring-electric-600 focus:bg-white transition-all placeholder:text-obsidian-300"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-obsidian mb-1">
                      Confirm Password <span className="text-rose-500">*</span>
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-obsidian-400">
                        <Lock className="h-4 w-4" />
                      </div>
                      <input
                        type="password"
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full pl-9 pr-3 py-2 text-xs bg-cloud-50 border border-cloud-300 rounded-xl text-obsidian focus:outline-none focus:ring-2 focus:ring-electric-600 focus:bg-white transition-all placeholder:text-obsidian-300"
                      />
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full mt-3 py-2.5 px-4 bg-electric-600 hover:bg-electric-700 text-white font-semibold text-xs rounded-xl shadow-subtle flex items-center justify-center gap-2 transition-all disabled:opacity-60"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Verifying Employee Record...</span>
                    </>
                  ) : (
                    <>
                      <span>Register Account</span>
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </button>
              </form>
            </>
          )}

          <div className="mt-6 pt-4 border-t border-cloud-200 text-center">
            <p className="text-xs text-obsidian-400">
              Already have an account?{' '}
              <Link to="/login" className="font-semibold text-electric-600 hover:underline">
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
