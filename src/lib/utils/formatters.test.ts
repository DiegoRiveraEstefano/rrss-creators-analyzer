import { describe, it, expect } from 'vitest';
import { formatCurrency, formatNumber, formatDuration, formatPercentage } from './formatters';

describe('formatters', () => {
	it('formats currency correctly', () => {
		expect(formatCurrency(1250.5)).toBe('$1,250.50');
		expect(formatCurrency(0)).toBe('$0.00');
		expect(formatCurrency(1500, true)).toBe('$1.5K');
	});

	it('formats numbers with compact notation', () => {
		expect(formatNumber(15400000, true)).toBe('15.4M');
		expect(formatNumber(42000, true)).toBe('42K');
	});

	it('formats duration in seconds to hours/minutes', () => {
		expect(formatDuration(3600)).toBe('1h 0m');
		expect(formatDuration(5400)).toBe('1h 30m');
		expect(formatDuration(1800)).toBe('30m');
	});

	it('formats percentage with sign and flags', () => {
		const positive = formatPercentage(14.8);
		expect(positive.text).toBe('+14.8%');
		expect(positive.isPositive).toBe(true);

		const negative = formatPercentage(-3.2);
		expect(negative.text).toBe('-3.2%');
		expect(negative.isPositive).toBe(false);
	});
});
