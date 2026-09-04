import { supabase } from '$lib/supabase/client';
import type { Database } from '$lib/supabase/database.types';
import type { ValidatedStreamRow } from '$lib/utils/csvValidator';

export type ImportBatch = Database['public']['Tables']['import_batches']['Row'];

export const importService = {
	async getImportBatches(organizationId: string): Promise<ImportBatch[]> {
		const { data, error } = await supabase
			.from('import_batches')
			.select('*')
			.eq('organization_id', organizationId)
			.order('created_at', { ascending: false });

		if (error) throw error;
		return data || [];
	},

	async uploadBatch(
		organizationId: string,
		creatorId: string,
		filename: string,
		rows: ValidatedStreamRow[]
	): Promise<{ success: boolean; batchId: string; importedCount: number }> {
		const validRows = rows.filter((r) => r.status !== 'error');

		// 1. Crear el lote de importación
		const { data: batch, error: batchError } = await supabase
			.from('import_batches')
			.insert({
				organization_id: organizationId,
				filename,
				source_platform: validRows[0]?.platform || 'twitch',
				total_rows: rows.length,
				valid_rows: validRows.length,
				error_count: rows.length - validRows.length,
				status: 'completed'
			})
			.select()
			.single();

		if (batchError) throw batchError;

		// 2. Insertar las sesiones vinculadas
		const sessionInserts = validRows.map((row) => ({
			organization_id: organizationId,
			creator_id: creatorId,
			import_batch_id: batch.id,
			session_title: row.session_title,
			game_or_category: row.game_or_category,
			platform: row.platform,
			streamed_at: row.streamed_at,
			duration_seconds: row.duration_seconds,
			peak_viewers: row.peak_viewers,
			avg_ccv: row.avg_ccv,
			chat_messages_count: row.chat_messages_count,
			new_followers: row.new_followers,
			ad_revenue: row.ad_revenue,
			donations_revenue: row.donations_revenue,
			subs_revenue: row.subs_revenue,
			total_earnings: row.total_earnings,
			earnings_per_hour: row.earnings_per_hour
		}));

		const { error: insertError } = await supabase
			.from('streaming_sessions')
			.insert(sessionInserts);

		if (insertError) throw insertError;

		return {
			success: true,
			batchId: batch.id,
			importedCount: validRows.length
		};
	}
};
