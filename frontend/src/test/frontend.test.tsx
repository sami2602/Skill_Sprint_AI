import { describe, it, expect, beforeEach, vi } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { App } from '../App';

describe('SkillSprint AI — Authentication & Production Routing Test Suite', () => {
  beforeEach(() => {
    localStorage.clear();
    window.history.pushState({}, '', '/');
    vi.restoreAllMocks();
  });

  it('redirects unauthenticated visitor to Sign In page', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/Sign In to Your Account/i)).toBeDefined();
      expect(screen.getByText(/Username or Work Email/i)).toBeDefined();
    });
  });

  it('navigates from Login page to Employee Registration page', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/Register with Enterprise Email/i)).toBeDefined();
    });
    const signupLink = screen.getByText(/Register with Enterprise Email/i);
    fireEvent.click(signupLink);

    await waitFor(() => {
      expect(screen.getByText(/Employee Registration/i)).toBeDefined();
      expect(screen.getByText(/Strict Employee Verification Policy/i)).toBeDefined();
    });
  });

  it('renders application workspace when authenticated user is present in session', async () => {
    const mockUser = {
      id: 'usr-admin-01',
      username: 'admin',
      email: 'admin@skillsprint.ai',
      full_name: 'Elena Rostova',
      role: 'ADMIN',
      department: 'Executive',
      is_active: true
    };
    localStorage.setItem('skillsprint_token', 'mock-valid-jwt-token');
    localStorage.setItem('skillsprint_user', JSON.stringify(mockUser));

    global.fetch = vi.fn().mockImplementation((url: string) => {
      if (url.includes('/api/v1/auth/me')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockUser)
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      });
    }) as any;

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/Executive Overview Dashboard/i)).toBeDefined();
    });
  });
});
