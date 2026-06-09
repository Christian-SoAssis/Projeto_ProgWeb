import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import LoginPage from '../../src/app/login/page';
import { useAuth } from '../../src/presentation/hooks/use-auth';

// Mock the Auth Context
vi.mock('../../src/presentation/hooks/use-auth', () => ({
  useAuth: vi.fn(),
}));

// Mock Next.js router
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
  useSearchParams: () => new URLSearchParams(),
}));

describe('LoginPage', () => {
  const mockLogin = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useAuth as any).mockReturnValue({
      login: mockLogin,
      loading: false,
    });
  });

  it('should submit credentials successfully', async () => {
    mockLogin.mockResolvedValueOnce(undefined);

    render(<LoginPage />);

    // Find inputs
    const emailInput = screen.getByPlaceholderText('exemplo@email.com');
    const passwordInput = screen.getByPlaceholderText('••••••••');
    const submitButton = screen.getByRole('button', { name: /entrar/i });

    // Fill the form
    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');

    // Submit
    await userEvent.click(submitButton);

    // Verify login function was called with correct credentials
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({ email: 'test@example.com', password: 'password123' });
      // Depending on implementation, you might expect a redirect here.
      // E.g., expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });
});
