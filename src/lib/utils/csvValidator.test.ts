import { describe, it, expect } from 'vitest';
import { validateAndNormalizeRow } from './csvValidator';

describe('csvValidator', () => {
	it('normalizes valid raw streaming rows', () => {
		const result = validateAndNormalizeRow({
			session_title: 'Gran Final de Torneo',
			game_or_category: 'VALORANT',
			platform: 'twitch',
			streamed_at: '2026-09-04T18:00:00Z',
			duration_seconds: 7200,
			peak_viewers: 50000,
			avg_ccv: 35000,
			total_earnings: 2000
		});

		expect(result.status).toBe('valid');
		expect(result.session_title).toBe('Gran Final de Torneo');
		expect(result.platform).toBe('twitch');
		expect(result.hours_streamed).toBe(2);
		expect(result.earnings_per_hour).toBe(1000);
	});

	it('handles missing or alternate headers gracefully', () => {
		const result = validateAndNormalizeRow({
			title: 'Directo improvisado',
			category: 'Just Chatting',
			Plataforma: 'kick',
			hours_streamed: 3,
			earnings: 600
		});

		expect(result.session_title).toBe('Directo improvisado');
		expect(result.game_or_category).toBe('Just Chatting');
		expect(result.platform).toBe('kick');
		expect(result.duration_seconds).toBe(10800);
		expect(result.earnings_per_hour).toBe(200);
	});
});
