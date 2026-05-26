import { describe, it, expect } from 'vitest';
import { BidStatus } from '../../src/domain/models/bid';

describe('BidStatus (union types)', () => {
  it('should accept only valid statuses at runtime (simulate validation)', () => {
    // Array with the exact allowed types from the union type
    const validStatuses: BidStatus[] = ['pending', 'accepted', 'rejected', 'cancelled'];
    
    // Test a simple validation function that a component or mapper might use
    const isValidStatus = (status: any): status is BidStatus => {
      return validStatuses.includes(status);
    };

    expect(isValidStatus('pending')).toBe(true);
    expect(isValidStatus('accepted')).toBe(true);
    expect(isValidStatus('rejected')).toBe(true);
    expect(isValidStatus('cancelled')).toBe(true);
    
    expect(isValidStatus('completed')).toBe(false);
    expect(isValidStatus('OPEN')).toBe(false);
    expect(isValidStatus(null)).toBe(false);
    expect(isValidStatus(123)).toBe(false);
  });
});
