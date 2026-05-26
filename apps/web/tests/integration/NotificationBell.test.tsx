import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NotificationBell } from '../../src/components/dashboard/NotificationBell';

// Mock the custom hook to provide specific states for the test
vi.mock('../../src/hooks/useNotifications', () => ({
  useNotifications: vi.fn()
}));

import { useNotifications } from '../../src/hooks/useNotifications';

describe('NotificationBell', () => {
  const mockMarkRead = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the badge with the correct unread count', () => {
    (useNotifications as any).mockReturnValue({
      notifications: [
        { id: '1', type: 'new_bid', readAt: null, createdAt: new Date().toISOString(), payload: {} },
        { id: '2', type: 'new_review', readAt: null, createdAt: new Date().toISOString(), payload: {} }
      ],
      unreadCount: 2,
      loading: false,
      markRead: mockMarkRead,
    });

    render(<NotificationBell />);

    // Check if the badge showing "2" is rendered
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('should call markRead when opened with unread notifications', async () => {
    (useNotifications as any).mockReturnValue({
      notifications: [
        { id: '1', type: 'new_bid', readAt: null, createdAt: new Date().toISOString(), payload: {} },
      ],
      unreadCount: 1,
      loading: false,
      markRead: mockMarkRead,
    });

    render(<NotificationBell />);

    // Get the bell button. We can find it by its role or structure.
    const bellButton = screen.getByRole('button');
    
    // Open the dropdown
    await userEvent.click(bellButton);

    // Expect markRead to be called with the ID of the unread notification
    expect(mockMarkRead).toHaveBeenCalledTimes(1);
    expect(mockMarkRead).toHaveBeenCalledWith(['1']);
    
    // Expect the dropdown list to appear
    expect(screen.getByText('Notificações')).toBeInTheDocument();
  });

  it('should show 9+ badge for more than 9 unread notifications', () => {
    (useNotifications as any).mockReturnValue({
      notifications: [],
      unreadCount: 10,
      loading: false,
      markRead: mockMarkRead,
    });

    render(<NotificationBell />);

    // Check if the badge showing "9+" is rendered
    expect(screen.getByText('9+')).toBeInTheDocument();
  });
});
