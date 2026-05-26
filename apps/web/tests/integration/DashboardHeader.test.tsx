import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DashboardHeader } from '../../src/components/dashboard/DashboardHeader';
import { useAuth } from '../../src/context/auth-context';

// Mock the Auth Context
vi.mock('../../src/context/auth-context', () => ({
  useAuth: vi.fn(),
}));

// Mock Next.js routing hooks if used in Header
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
  usePathname: () => '/dashboard',
}));

describe('DashboardHeader', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should display the user name when authenticated', () => {
    // Setup mock to return an authenticated user
    (useAuth as any).mockReturnValue({
      user: {
        id: '123',
        name: 'John Doe',
        email: 'john@example.com',
      },
      loading: false,
    });

    render(<DashboardHeader userName="John Doe" roleLabel="Cliente" />);

    // Verify the user name is rendered. It might be inside a greeting like "Olá, John Doe"
    expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
  });

  it('should not display the user name when not authenticated or loading', () => {
    // Setup mock for unauthenticated state
    (useAuth as any).mockReturnValue({
      user: null,
      loading: false,
    });

    render(<DashboardHeader userName="" roleLabel="Cliente" />);

    // Verify the user name is NOT rendered
    expect(screen.queryByText(/John Doe/i)).not.toBeInTheDocument();
  });
});
