import { supabase } from '$lib/supabase/client';
import type { Database, PlatformType } from '$lib/supabase/database.types';

export type PublishedVideo = Database['public']['Tables']['published_videos']['Row'];
export type PublishedVideoInsert = Database['public']['Tables']['published_videos']['Insert'];

export const videoService = {
	async getVideosByOrganization(organizationId: string, limit = 50): Promise<PublishedVideo[]> {
		const { data, error } = await supabase
			.from('published_videos')
			.select('*')
			.eq('organization_id', organizationId)
			.order('published_at', { ascending: false })
			.limit(limit);

		if (error) throw error;
		return data || [];
	},

	async getVideosByCreator(creatorId: string, limit = 50): Promise<PublishedVideo[]> {
		const { data, error } = await supabase
			.from('published_videos')
			.select('*')
			.eq('creator_id', creatorId)
			.order('published_at', { ascending: false })
			.limit(limit);

		if (error) throw error;
		return data || [];
	},

	async createVideo(video: PublishedVideoInsert): Promise<PublishedVideo> {
		const { data, error } = await supabase
			.from('published_videos')
			.insert(video)
			.select()
			.single();

		if (error) throw error;
		return data;
	},

	async updateVideo(
		id: string,
		updates: Partial<Database['public']['Tables']['published_videos']['Update']>
	): Promise<PublishedVideo> {
		const { data, error } = await supabase
			.from('published_videos')
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

	async deleteVideo(id: string): Promise<boolean> {
		const { error } = await supabase
			.from('published_videos')
			.delete()
			.eq('id', id);

		if (error) throw error;
		return true;
	}
};
