import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SearchBar } from '../../src/components/SearchBar';
import { useRouter, useSearchParams } from 'next/navigation';

// Mock Next.js routing hooks
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
  useSearchParams: vi.fn(),
  usePathname: () => '/',
}));

describe('SearchBar', () => {
  const mockPush = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useRouter as any).mockReturnValue({ push: mockPush });
    (useSearchParams as any).mockReturnValue({
      get: vi.fn().mockReturnValue(''),
      toString: vi.fn().mockReturnValue('')
    });
  });

  it('should trigger search query when form is submitted', async () => {
    render(<SearchBar />);

    const input = screen.getByRole('textbox');

    await userEvent.type(input, 'pintor{enter}');

    expect(mockPush).toHaveBeenCalledWith('/search?q=pintor');
  });
});
