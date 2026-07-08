import { describe, it, expect } from 'vitest'
import { formatCurrency, formatDate, daysUntil, policyTypeColor, statusColor, cn } from '../src/lib/utils'

describe('formatCurrency', () => {
  it('formats USD correctly', () => {
    expect(formatCurrency(1200)).toBe('$1,200.00')
    expect(formatCurrency(0)).toBe('$0.00')
    expect(formatCurrency(500000)).toBe('$500,000.00')
  })
})

describe('formatDate', () => {
  it('formats date string', () => {
    const result = formatDate('2025-01-15')
    expect(result).toContain('2025')
    expect(result).toContain('Jan')
  })
})

describe('daysUntil', () => {
  it('returns negative for past dates', () => {
    expect(daysUntil('2020-01-01')).toBeLessThan(0)
  })
  it('returns positive for future dates', () => {
    expect(daysUntil('2099-01-01')).toBeGreaterThan(0)
  })
})

describe('policyTypeColor', () => {
  it('returns correct color for known types', () => {
    expect(policyTypeColor('life')).toContain('purple')
    expect(policyTypeColor('health')).toContain('green')
    expect(policyTypeColor('auto')).toContain('blue')
    expect(policyTypeColor('home')).toContain('orange')
  })
  it('returns default for unknown type', () => {
    expect(policyTypeColor('unknown')).toContain('gray')
  })
})

describe('statusColor', () => {
  it('returns correct color for statuses', () => {
    expect(statusColor('active')).toContain('green')
    expect(statusColor('expired')).toContain('red')
    expect(statusColor('pending')).toContain('yellow')
    expect(statusColor('completed')).toContain('green')
  })
})

describe('cn', () => {
  it('merges class names', () => {
    expect(cn('foo', 'bar')).toBe('foo bar')
    expect(cn('px-2', 'px-4')).toBe('px-4')
  })
})
