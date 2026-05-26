import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiFetch } from '../../src/lib/api';

describe('apiFetch', () => {
  const mockFetch = vi.fn();
  
  beforeEach(() => {
    global.fetch = mockFetch;
    // Clear storage before each test
    localStorage.clear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should inject Bearer Token if token exists in localStorage', async () => {
    // Setup
    localStorage.setItem('access_token', 'my-secret-token');
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true })
    });

    // Execute
    await apiFetch('/test-endpoint');

    // Assert
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/test-endpoint'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': 'Bearer my-secret-token',
        })
      })
    );
  });

  it('should remove Content-Type header if body is FormData', async () => {
    // Setup
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true })
    });
    
    const formData = new FormData();
    formData.append('file', new Blob(['test']), 'test.txt');

    // Execute
    await apiFetch('/upload', {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data', // user explicitly passed it
      }
    });

    // Assert
    // When sending FormData, we should let the browser set the Content-Type with boundary.
    // So the 'Content-Type' header should be undefined/deleted from the final headers.
    const callArgs = mockFetch.mock.calls[0];
    const fetchOptions = callArgs[1];
    
    expect(fetchOptions.body).toBeInstanceOf(FormData);
    
    // We expect the headers object not to have Content-Type
    const headers = fetchOptions.headers;
    // headers could be a Headers object or a plain object
    if (headers instanceof Headers) {
      expect(headers.has('Content-Type')).toBe(false);
    } else {
      expect(headers['Content-Type']).toBeUndefined();
    }
  });

  it('should set Content-Type to application/json by default if no body', async () => {
    // Setup
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true })
    });

    // Execute
    await apiFetch('/test-endpoint');

    // Assert
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/test-endpoint'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        })
      })
    );
  });
});
