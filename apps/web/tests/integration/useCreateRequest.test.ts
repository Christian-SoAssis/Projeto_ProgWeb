import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useCreateRequest } from '../../src/hooks/useCreateRequest';
import { requestRepository } from '../../src/repositories';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

// Mock dependencies
vi.mock('../../src/repositories', () => ({
  requestRepository: {
    create: vi.fn(),
  },
}));

vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}));

vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('useCreateRequest', () => {
  const mockPush = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useRouter as any).mockReturnValue({ push: mockPush });
  });

  it('should handle the full mock flow for creating a request successfully', async () => {
    const mockCreatedRequest = { id: 'req-123', title: 'Test Request' };
    (requestRepository.create as any).mockResolvedValueOnce(mockCreatedRequest);

    const { result } = renderHook(() => useCreateRequest());

    expect(result.current.isSubmitting).toBe(false);

    const formData = {
      title: 'Fix my AC',
      categoryId: 'cat-1',
      urgency: 'medium',
      latitude: 0,
      longitude: 0,
    };

    await act(async () => {
      await result.current.createRequest(formData as any);
    });

    expect(requestRepository.create).toHaveBeenCalledTimes(1);
    expect(requestRepository.create).toHaveBeenCalledWith(formData);
    expect(toast.success).toHaveBeenCalledWith('Pedido criado!', expect.any(Object));
    expect(mockPush).toHaveBeenCalledWith(`/requests/req-123/matches`);
    expect(result.current.isSubmitting).toBe(false);
  });

  it('should handle the error flow correctly', async () => {
    const mockError = new Error('Failed to create request');
    (requestRepository.create as any).mockRejectedValueOnce(mockError);

    const { result } = renderHook(() => useCreateRequest());

    const formData = {
      title: 'Fix my AC',
      categoryId: 'cat-1',
      urgency: 'medium',
      latitude: 0,
      longitude: 0,
    };

    await act(async () => {
      await result.current.createRequest(formData as any);
    });

    expect(requestRepository.create).toHaveBeenCalledTimes(1);
    expect(toast.error).toHaveBeenCalledWith('Erro ao criar pedido', expect.any(Object));
    expect(mockPush).not.toHaveBeenCalled();
    expect(result.current.isSubmitting).toBe(false);
  });
});
