import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('skillsprint_token'));
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('skillsprint_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const logout = useCallback(() => {
    localStorage.removeItem('skillsprint_token');
    localStorage.removeItem('skillsprint_user');
    setToken(null);
    setUser(null);
  }, []);

  const login = useCallback((newToken: string, newUser: User) => {
    localStorage.setItem('skillsprint_token', newToken);
    localStorage.setItem('skillsprint_user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  }, []);

  useEffect(() => {
    const verifySession = async () => {
      const storedToken = localStorage.getItem('skillsprint_token');
      if (!storedToken) {
        setUser(null);
        setIsLoading(false);
        return;
      }
      try {
        const res = await fetch('/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${storedToken}`
          }
        });
        if (res.ok) {
          const fetchedUser: User = await res.json();
          if (!fetchedUser.full_name && fetchedUser.username) {
            fetchedUser.full_name = fetchedUser.username;
          }
          setUser(fetchedUser);
          localStorage.setItem('skillsprint_user', JSON.stringify(fetchedUser));
        } else {
          logout();
        }
      } catch (err) {
        // Network or server error
      } finally {
        setIsLoading(false);
      }
    };

    verifySession();
  }, [logout]);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
