import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { CategoryPills } from '../../src/components/CategoryPills';

describe('CategoryPills', () => {
  it('should render exactly 16 categories', () => {
    render(<CategoryPills />);

    // Since it uses next/link, they render as <a> tags
    const links = screen.getAllByRole('link');
    expect(links).toHaveLength(16);
  });
});
