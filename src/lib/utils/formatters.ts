/**
 * Formatea valores numéricos a moneda USD ($1,250.00 o $1.2K)
 */
export function formatCurrency(value: number, compact = false): string {
	if (isNaN(value)) return '$0.00';

	if (compact && Math.abs(value) >= 1000) {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			notation: 'compact',
			maximumFractionDigits: 1
		}).format(value);
	}

	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
		minimumFractionDigits: 2,
		maximumFractionDigits: 2
	}).format(value);
}

/**
 * Formatea cifras grandes con sufijos K, M (ej. 142.5K viewers)
 */
export function formatNumber(value: number, compact = false): string {
	if (isNaN(value)) return '0';

	if (compact) {
		return new Intl.NumberFormat('en-US', {
			notation: 'compact',
			maximumFractionDigits: 1
		}).format(value);
	}

	return new Intl.NumberFormat('en-US').format(value);
}

/**
 * Formatea segundos a formato legible 'Xh Ym'
 */
export function formatDuration(seconds: number): string {
	if (!seconds || seconds <= 0) return '0h 0m';
	const hours = Math.floor(seconds / 3600);
	const minutes = Math.floor((seconds % 3600) / 60);
	if (hours === 0) return `${minutes}m`;
	return `${hours}h ${minutes}m`;
}

/**
 * Formateo de porcentaje de cambio con signo (+12.4% o -3.1%)
 */
export function formatPercentage(value: number): { text: string; isPositive: boolean; isNeutral: boolean } {
	if (isNaN(value)) return { text: '0.0%', isPositive: true, isNeutral: true };
	const isNeutral = value === 0;
	const isPositive = value > 0;
	const prefix = isPositive ? '+' : '';
	return {
		text: `${prefix}${value.toFixed(1)}%`,
		isPositive,
		isNeutral
	};
}

/**
 * Formatea fecha ISO a formato local legible
 */
export function formatDate(dateString: string): string {
	try {
		const date = new Date(dateString);
		return new Intl.DateTimeFormat('es-ES', {
			day: '2-digit',
			month: 'short',
			year: 'numeric'
		}).format(date);
	} catch {
		return dateString;
	}
}

/**
 * Formatea fecha y hora completa
 */
export function formatDateTime(dateString: string): string {
	try {
		const date = new Date(dateString);
		return new Intl.DateTimeFormat('es-ES', {
			day: '2-digit',
			month: 'short',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		}).format(date);
	} catch {
		return dateString;
	}
}
