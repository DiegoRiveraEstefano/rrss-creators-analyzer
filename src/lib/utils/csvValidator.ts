import Papa from 'papaparse';
import type { PlatformType } from '$lib/supabase/database.types';

export interface RawStreamRow {
	session_title?: string;
	game_or_category?: string;
	platform?: string;
	streamed_at?: string;
	duration_seconds?: number | string;
	hours_streamed?: number | string;
	peak_viewers?: number | string;
	avg_ccv?: number | string;
	chat_messages_count?: number | string;
	new_followers?: number | string;
	ad_revenue?: number | string;
	donations_revenue?: number | string;
	subs_revenue?: number | string;
	total_earnings?: number | string;
	[key: string]: unknown;
}

export interface ValidatedStreamRow {
	session_title: string;
	game_or_category: string;
	platform: PlatformType;
	streamed_at: string;
	duration_seconds: number;
	hours_streamed: number;
	peak_viewers: number;
	avg_ccv: number;
	chat_messages_count: number;
	new_followers: number;
	ad_revenue: number;
	donations_revenue: number;
	subs_revenue: number;
	total_earnings: number;
	earnings_per_hour: number;
	status: 'valid' | 'warning' | 'error';
	validationMessages: string[];
}

export interface ParseResult {
	filename: string;
	totalRows: number;
	validRows: ValidatedStreamRow[];
	invalidRows: ValidatedStreamRow[];
	hasErrors: boolean;
	headers: string[];
}

/**
 * Normaliza y valida una fila cruda de streaming
 */
export function validateAndNormalizeRow(raw: RawStreamRow): ValidatedStreamRow {
	const messages: string[] = [];
	let rowStatus: 'valid' | 'warning' | 'error' = 'valid';

	// 1. Título de sesión
	const session_title = (raw.session_title || raw['title'] || raw['Título'] || raw['Titulo'] || 'Live Stream').toString().trim();

	// 2. Juego / Categoría
	const game_or_category = (raw.game_or_category || raw['category'] || raw['game'] || raw['Categoría'] || raw['Juego'] || 'Just Chatting').toString().trim();

	// 3. Plataforma
	const platformRaw = (raw.platform || raw['Plataforma'] || 'twitch').toString().toLowerCase().trim();
	let platform: PlatformType = 'twitch';
	if (['twitch', 'youtube', 'kick', 'tiktok'].includes(platformRaw)) {
		platform = platformRaw as PlatformType;
	} else {
		platform = 'twitch';
		messages.push(`Plataforma desconocida "${platformRaw}", asignada por defecto a Twitch.`);
		rowStatus = 'warning';
	}

	// 4. Fecha de emisión
	let streamed_at = new Date().toISOString();
	const dateRaw = raw.streamed_at || raw['date'] || raw['Fecha'] || raw['timestamp'] || raw['created_at'];
	if (dateRaw) {
		const parsedDate = new Date(dateRaw as string);
		if (!isNaN(parsedDate.getTime())) {
			streamed_at = parsedDate.toISOString();
		} else {
			messages.push(`Fecha inválida "${dateRaw}", se usó la fecha actual.`);
			rowStatus = 'warning';
		}
	} else {
		messages.push('Fecha no especificada, se usó la fecha actual.');
		rowStatus = 'warning';
	}

	// 5. Duración (segundos u horas)
	let duration_seconds = 0;
	if (raw.duration_seconds !== undefined && raw.duration_seconds !== '') {
		duration_seconds = Math.max(0, parseInt(String(raw.duration_seconds), 10) || 0);
	} else if (raw.hours_streamed !== undefined && raw.hours_streamed !== '') {
		const hrs = parseFloat(String(raw.hours_streamed)) || 0;
		duration_seconds = Math.round(hrs * 3600);
	} else if (raw['Duración (s)'] || raw['Duracion']) {
		duration_seconds = parseInt(String(raw['Duración (s)'] || raw['Duracion']), 10) || 0;
	}

	const hours_streamed = Number((duration_seconds / 3600).toFixed(2));

	if (duration_seconds <= 0) {
		messages.push('Duración de stream es 0 o inválida.');
		rowStatus = 'warning';
	}

	// 6. Viewers y concurrencia
	const peak_viewers = Math.max(0, parseInt(String(raw.peak_viewers || raw['peak'] || raw['Pico Viewers'] || 0), 10) || 0);
	const avg_ccv = Math.max(0, parseInt(String(raw.avg_ccv || raw['ccv'] || raw['Media CCV'] || raw['Average CCV'] || 0), 10) || 0);
	const chat_messages_count = Math.max(0, parseInt(String(raw.chat_messages_count || raw['chat'] || raw['Mensajes Chat'] || 0), 10) || 0);
	const new_followers = Math.max(0, parseInt(String(raw.new_followers || raw['followers'] || raw['Nuevos Seguidores'] || 0), 10) || 0);

	// 7. Ingresos
	const ad_revenue = Math.max(0, parseFloat(String(raw.ad_revenue || raw['ads'] || raw['Ingresos Ads'] || 0)) || 0);
	const donations_revenue = Math.max(0, parseFloat(String(raw.donations_revenue || raw['donations'] || raw['Donaciones'] || 0)) || 0);
	const subs_revenue = Math.max(0, parseFloat(String(raw.subs_revenue || raw['subs'] || raw['Suscripciones'] || 0)) || 0);

	let total_earnings = parseFloat(String(raw.total_earnings || raw['earnings'] || raw['Total Ingresos'] || 0)) || 0;
	if (total_earnings === 0 && (ad_revenue > 0 || donations_revenue > 0 || subs_revenue > 0)) {
		total_earnings = ad_revenue + donations_revenue + subs_revenue;
	}

	const earnings_per_hour = hours_streamed > 0 ? Number((total_earnings / hours_streamed).toFixed(2)) : 0;

	return {
		session_title,
		game_or_category,
		platform,
		streamed_at,
		duration_seconds,
		hours_streamed,
		peak_viewers,
		avg_ccv,
		chat_messages_count,
		new_followers,
		ad_revenue: Number(ad_revenue.toFixed(2)),
		donations_revenue: Number(donations_revenue.toFixed(2)),
		subs_revenue: Number(subs_revenue.toFixed(2)),
		total_earnings: Number(total_earnings.toFixed(2)),
		earnings_per_hour,
		status: rowStatus,
		validationMessages: messages
	};
}

/**
 * Parsea un archivo CSV en el cliente usando PapaParse
 */
export async function parseCsvFile(file: File): Promise<ParseResult> {
	return new Promise((resolve, reject) => {
		Papa.parse<RawStreamRow>(file, {
			header: true,
			dynamicTyping: true,
			skipEmptyLines: 'greedy',
			complete: (results) => {
				const headers = results.meta.fields || [];
				const validRows: ValidatedStreamRow[] = [];
				const invalidRows: ValidatedStreamRow[] = [];

				for (const raw of results.data) {
					if (!raw || Object.keys(raw).length === 0) continue;
					const validated = validateAndNormalizeRow(raw);
					if (validated.status === 'error') {
						invalidRows.push(validated);
					} else {
						validRows.push(validated);
					}
				}

				resolve({
					filename: file.name,
					totalRows: validRows.length + invalidRows.length,
					validRows,
					invalidRows,
					hasErrors: invalidRows.length > 0,
					headers
				});
			},
			error: (error) => {
				reject(error);
			}
		});
	});
}
