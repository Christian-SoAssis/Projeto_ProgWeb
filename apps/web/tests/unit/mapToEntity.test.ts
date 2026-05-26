import { describe, it, expect } from 'vitest';
import { RequestRepositoryImpl } from '../../src/infrastructure/repositories/request.repository.impl';

describe('mapToEntity (snake_case -> camelCase)', () => {
  it('should correctly map snake_case API payload to camelCase entity', () => {
    const repository = new RequestRepositoryImpl();
    
    const apiPayload = {
      id: 'req-123',
      client_id: 'client-456',
      category_id: 'cat-789',
      title: 'Fix my sink',
      description: 'It is leaking',
      latitude: -23.5505,
      longitude: -46.6333,
      urgency: 'high',
      budget_cents: 5000,
      status: 'open',
      created_at: '2023-01-01T10:00:00Z',
      updated_at: '2023-01-01T12:00:00Z',
      images: [
        {
          id: 'img-1',
          request_id: 'req-123',
          url: 'https://example.com/img1.jpg',
          content_type: 'image/jpeg',
          size_bytes: 1024,
          analyzed: true,
          created_at: '2023-01-01T10:05:00Z'
        }
      ]
    };

    // Access private method for testing
    const entity = (repository as any).mapToEntity(apiPayload);

    expect(entity).toEqual({
      id: 'req-123',
      clientId: 'client-456',
      categoryId: 'cat-789',
      title: 'Fix my sink',
      description: 'It is leaking',
      latitude: -23.5505,
      longitude: -46.6333,
      urgency: 'high',
      budgetCents: 5000,
      status: 'open',
      createdAt: '2023-01-01T10:00:00Z',
      updatedAt: '2023-01-01T12:00:00Z',
      images: [
        {
          id: 'img-1',
          requestId: 'req-123',
          url: 'https://example.com/img1.jpg',
          contentType: 'image/jpeg',
          sizeBytes: 1024,
          analyzed: true,
          createdAt: '2023-01-01T10:05:00Z'
        }
      ]
    });
  });

  it('should handle missing images gracefully', () => {
    const repository = new RequestRepositoryImpl();
    
    const apiPayload = {
      id: 'req-123',
      client_id: 'client-456',
      category_id: 'cat-789',
      title: 'Fix my sink',
      latitude: -23.5505,
      longitude: -46.6333,
      urgency: 'high',
      status: 'open',
      // images array is missing
    };

    const entity = (repository as any).mapToEntity(apiPayload);

    expect(entity.images).toEqual([]);
    expect(entity.clientId).toBe('client-456');
  });
});
