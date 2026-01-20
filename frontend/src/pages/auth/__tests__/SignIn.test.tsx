import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import SignInPage from '../SignIn';

vi.mock('@clerk/clerk-react', () => ({
  SignIn: ({ appearance }: any) => (
    <div data-testid="clerk-signin">Sign In Component</div>
  ),
}));

describe('SignInPage', () => {
  it('renders Clerk SignIn component', () => {
    const { getByTestId } = render(
      <BrowserRouter>
        <SignInPage />
      </BrowserRouter>
    );
    
    expect(getByTestId('clerk-signin')).toBeInTheDocument();
  });
});
