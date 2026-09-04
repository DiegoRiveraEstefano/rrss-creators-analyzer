import { supabase } from '$lib/supabase/client';
import type { Database, PlatformType, CreatorStatus } from '$lib/supabase/database.types';

export type Creator = Database['public']['Tables']['creators']['Row'];
export type Channel = Database['public']['Tables']['channels']['Row'];

export interface CreatorWithChannels extends Creator {
	channels: Channel[];
}

export const creatorService = {
	async getCreators(organizationId: string): Promise<CreatorWithChannels[]> {
		const { data, error } = await supabase
			.from('creators')
			.select('*, channels(*)')
			.eq('organization_id', organizationId)
			.order('display_name');

		if (error) throw error;
		return (data || []) as unknown as CreatorWithChannels[];
	},

	async getCreatorById(id: string): Promise<CreatorWithChannels | null> {
		const { data, error } = await supabase
			.from('creators')
			.select('*, channels(*)')
			.eq('id', id)
			.maybeSingle();

		if (error) throw error;
		return data as unknown as CreatorWithChannels;
	},

	async createCreator(creator: Database['public']['Tables']['creators']['Insert']): Promise<Creator> {
		const { data, error } = await supabase
			.from('creators')
			.insert(creator)
			.select()
			.single();

		if (error) throw error;
		return data;
	},

	async updateCreator(
		id: string,
		updates: {
			display_name?: string;
			handle?: string;
			avatar_url?: string | null;
			bio?: string | null;
			primary_platform?: PlatformType;
			status?: CreatorStatus;
		}
	): Promise<Creator> {
		const { data, error } = await supabase
			.from('creators')
			.update({
				...updates,
				updated_at: new Date().toISOString()
			})
			.eq('id', id)
			.select()
			.single();

		if (error) throw error;
		return data;
	},

	async deleteCreator(id: string): Promise<boolean> {
		const { error } = await supabase
			.from('creators')
			.delete()
			.eq('id', id);

		if (error) throw error;
		return true;
	},

	async addChannelToCreator(payload: {
		creator_id: string;
		platform: PlatformType;
		platform_channel_id: string;
		channel_url?: string | null;
		followers_count?: number;
		subscribers_count?: number;
		is_live?: boolean;
	}): Promise<Channel> {
		const { data, error } = await supabase
			.from('channels')
			.insert({
				creator_id: payload.creator_id,
				platform: payload.platform,
				platform_channel_id: payload.platform_channel_id,
				channel_url: payload.channel_url || null,
				followers_count: payload.followers_count || 0,
				subscribers_count: payload.subscribers_count || 0,
				is_live: payload.is_live || false
			})
			.select()
			.single();

		if (error) throw error;
		return data;
	}
};
