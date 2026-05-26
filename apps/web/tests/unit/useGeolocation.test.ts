import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useGeolocation } from '../../src/hooks/useGeolocation';

describe('useGeolocation', () => {
  const mockGeolocation = {
    getCurrentPosition: vi.fn(),
    watchPosition: vi.fn(),
    clearWatch: vi.fn(),
  };

  beforeEach(() => {
    // Mock navigator.geolocation
    Object.defineProperty(global.navigator, 'geolocation', {
      value: mockGeolocation,
      configurable: true,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should return position on success', async () => {
    const mockPosition = {
      coords: {
        latitude: -23.5505,
        longitude: -46.6333,
        accuracy: 10,
        altitude: null,
        altitudeAccuracy: null,
        heading: null,
        speed: null,
      },
      timestamp: Date.now(),
    };

    mockGeolocation.getCurrentPosition.mockImplementation((success: any) => {
      success(mockPosition);
    });

    const { result } = renderHook(() => useGeolocation(true));

    expect(result.current.isLocating).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.latitude).toBe(-23.5505);
    expect(result.current.longitude).toBe(-46.6333);
  });

  it('should return error on failure (e.g. permission denied)', async () => {
    const mockError = {
      code: 1, // PERMISSION_DENIED
      message: 'User denied Geolocation',
      PERMISSION_DENIED: 1,
      POSITION_UNAVAILABLE: 2,
      TIMEOUT: 3,
    };

    mockGeolocation.getCurrentPosition.mockImplementation((success: any, error: any) => {
      error(mockError);
    });

    const { result } = renderHook(() => useGeolocation(true));

    expect(result.current.isLocating).toBe(false);
    expect(result.current.latitude).toBeNull();
    expect(result.current.longitude).toBeNull();
    expect(result.current.error).toBe('Não foi possível acessar sua localização.');
  });

  it('should handle missing geolocation in browser gracefully', () => {
    // Remove geolocation
    Object.defineProperty(global.navigator, 'geolocation', {
      value: undefined,
      configurable: true,
    });

    const { result } = renderHook(() => useGeolocation(true));

    expect(result.current.isLocating).toBe(false);
    expect(result.current.latitude).toBeNull();
    expect(result.current.longitude).toBeNull();
    expect(result.current.error).toBe('Geolocalização não suportada.');
  });
});
