import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { formatRelative } from '../../src/utils/formatters';

describe('formatRelative', () => {
  beforeEach(() => {
    // Mock the current date to a fixed point in time
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2023-10-01T12:00:00Z'));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should return "agora" for times less than 1 minute ago', () => {
    const time = new Date('2023-10-01T11:59:30Z').toISOString();
    expect(formatRelative(time)).toBe('agora');
  });

  it('should return "Xmin atrás" for times less than 60 minutes ago', () => {
    const time = new Date('2023-10-01T11:45:00Z').toISOString();
    expect(formatRelative(time)).toBe('15min atrás');
  });

  it('should return "Xh atrás" for times less than 24 hours ago', () => {
    const time = new Date('2023-10-01T09:00:00Z').toISOString();
    expect(formatRelative(time)).toBe('3h atrás');
  });

  it('should return "Xd atrás" for times more than 24 hours ago', () => {
    const time = new Date('2023-09-29T12:00:00Z').toISOString();
    expect(formatRelative(time)).toBe('2d atrás');
  });
});
