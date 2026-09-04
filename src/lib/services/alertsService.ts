import { supabase } from '$lib/supabase/client';
import type { Database } from '$lib/supabase/database.types';

export type ChannelAlert = Database['public']['Tables']['channel_alerts']['Row'];

export const alertsService = {
	async getAlerts(organizationId: string, creatorId?: string | null): Promise<ChannelAlert[]> {
		let query = supabase
			.from('channel_alerts')
			.select('*')
			.eq('organization_id', organizationId)
			.order('occurred_at', { ascending: false });

		if (creatorId) {
			query = query.eq('creator_id', creatorId);
		}

		const { data, error } = await query;
		if (error) throw error;
		return data || [];
	},

	async resolveAlert(id: string, notes?: string): Promise<boolean> {
		const { error } = await supabase
			.from('channel_alerts')
			.update({
				status: 'resolved',
				resolved_at: new Date().toISOString(),
				resolution_notes: notes || null
			})
			.eq('id', id);

		if (error) throw error;
		return true;
	}
};
