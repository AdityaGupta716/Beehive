import React from 'react';
import { describe, it, vi } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AdminRoute, UserRoute } from '../ProtectedRoutes';

vi.mock('@clerk/clerk-react', () => ({
  SignedIn: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    isAdmin: () => false,
    isUser: () => true,
    user: { id: 'test-user' },
  }),
}));

describe('ProtectedRoutes', () => {
  it('renders AdminRoute without crashing', () => {
    render(
      <BrowserRouter>
        <AdminRoute />
      </BrowserRouter>
    );
  });

  it('renders UserRoute without crashing', () => {
    render(
      <BrowserRouter>
        <UserRoute />
      </BrowserRouter>
    );
  });
});
