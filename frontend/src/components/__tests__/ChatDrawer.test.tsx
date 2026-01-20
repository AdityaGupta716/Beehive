import React from 'react';
import { describe, it, vi } from 'vitest';
import { render } from '@testing-library/react';
import ChatDrawer from '../ChatDrawer';

vi.mock('@clerk/clerk-react', () => ({
  useClerk: () => ({
    session: {
      getToken: vi.fn().mockResolvedValue('mock-token'),
    },
  }),
}));

global.fetch = vi.fn() as any;

describe('ChatDrawer', () => {
  it('renders without crashing for user role', () => {
    render(
      <ChatDrawer 
        userId="test-user" 
        userRole="user" 
        onClose={() => {}} 
      />
    );
  });

  it('renders without crashing for admin role', () => {
    render(
      <ChatDrawer 
        userId="test-admin" 
        userRole="admin" 
        onClose={() => {}} 
      />
    );
  });
});
