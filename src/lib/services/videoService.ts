import { supabase } from '$lib/supabase/client';
import type { Database, PlatformType } from '$lib/supabase/database.types';

export type Video = Database['public']['Tables']['videos']['Row'];
export type VideoInsert = Database['public']['Tables']['videos']['Insert'];
export type VideoPublication = Database['public']['Tables']['video_publications']['Row'];
export type VideoPublicationInsert = Database['public']['Tables']['video_publications']['Insert'];
export type PublishedVideo = VideoPublication;
export type VideoRelation = Database['public']['Tables']['video_relations']['Row'];
export type VideoRelationInsert = Database['public']['Tables']['video_relations']['Insert'];

export interface VideoWithDetails extends Video {
	publications: VideoPublication[];
	relations: VideoRelation[];
	total_views: number;
	total_revenue: number;
	total_likes: number;
	total_comments: number;
	total_shares: number;
	platforms: PlatformType[];
	has_live_relation: boolean;
	live_session_id?: string | null;
}

export const videoService = {
	async getVideos(
		organizationId: string,
		creatorId?: string | null,
		limit = 100
	): Promise<VideoWithDetails[]> {
		let query = supabase
			.from('videos')
			.select('*, video_publications(*), video_relations!video_relations_source_video_id_fkey(*)')
			.eq('organization_id', organizationId)
			.order('created_at', { ascending: false })
			.limit(limit);

		if (creatorId) {
			query = query.eq('creator_id', creatorId);
		}

		const { data, error } = await query;
		if (error) {
			// Fallback si la clave foránea no tiene el nombre explícito
			const fallback = await supabase
				.from('videos')
				.select('*, video_publications(*)')
				.eq('organization_id', organizationId)
				.order('created_at', { ascending: false })
				.limit(limit);

			if (fallback.error) throw fallback.error;
			return this.enrichVideos(fallback.data || []);
		}

		return this.enrichVideos(data || []);
	},

	enrichVideos(rawVideos: any[]): VideoWithDetails[] {
		return rawVideos.map((v) => {
			const pubs: VideoPublication[] = v.video_publications || [];
			const rels: VideoRelation[] = v.video_relations || [];

			const total_views = pubs.reduce((sum, p) => sum + (p.views_count || 0), 0);
			const total_revenue = pubs.reduce((sum, p) => sum + Number(p.estimated_revenue || 0), 0);
			const total_likes = pubs.reduce((sum, p) => sum + (p.likes_count || 0), 0);
			const total_comments = pubs.reduce((sum, p) => sum + (p.comments_count || 0), 0);
			const total_shares = pubs.reduce((sum, p) => sum + (p.shares_count || 0), 0);
			const platforms = Array.from(new Set(pubs.map((p) => p.platform)));

			const liveRel = rels.find((r) => r.target_session_id);

			return {
				...v,
				publications: pubs,
				relations: rels,
				total_views,
				total_revenue,
				total_likes,
				total_comments,
				total_shares,
				platforms,
				has_live_relation: !!liveRel,
				live_session_id: liveRel?.target_session_id || null
			};
		});
	},

	async getVideoById(id: string): Promise<VideoWithDetails | null> {
		const { data, error } = await supabase
			.from('videos')
			.select('*, video_publications(*), video_relations!video_relations_source_video_id_fkey(*)')
			.eq('id', id)
			.maybeSingle();

		if (error) {
			const fallback = await supabase
				.from('videos')
				.select('*, video_publications(*)')
				.eq('id', id)
				.maybeSingle();

			if (fallback.error) throw fallback.error;
			if (!fallback.data) return null;
			return this.enrichVideos([fallback.data])[0] || null;
		}

		if (!data) return null;
		return this.enrichVideos([data])[0] || null;
	},

	async createVideoWithDetails(payload: {
		video: VideoInsert;
		publication?: {
			platform: PlatformType;
			post_url?: string | null;
			thumbnail_url?: string | null;
			publication_type?: string;
			published_at?: string;
			views_count?: number;
			likes_count?: number;
			comments_count?: number;
			shares_count?: number;
			estimated_revenue?: number;
		};
		relation?: {
			target_session_id?: string | null;
			target_video_id?: string | null;
			relation_type: string;
			description?: string | null;
		};
	}): Promise<Video> {
		// 1. Crear video master
		const { data: videoData, error: videoError } = await supabase
			.from('videos')
			.insert(payload.video)
			.select()
			.single();

		if (videoError) throw videoError;

		// 2. Crear publicación inicial si se especificó
		if (payload.publication) {
			const pubInsert: VideoPublicationInsert = {
				video_id: videoData.id,
				organization_id: payload.video.organization_id,
				creator_id: payload.video.creator_id,
				platform: payload.publication.platform,
				post_url: payload.publication.post_url || null,
				thumbnail_url: payload.publication.thumbnail_url || null,
				publication_type: payload.publication.publication_type || 'standard',
				published_at: payload.publication.published_at || new Date().toISOString(),
				views_count: payload.publication.views_count || 0,
				likes_count: payload.publication.likes_count || 0,
				comments_count: payload.publication.comments_count || 0,
				shares_count: payload.publication.shares_count || 0,
				estimated_revenue: payload.publication.estimated_revenue || 0
			};

			const { error: pubError } = await supabase.from('video_publications').insert(pubInsert);
			if (pubError) {
				console.error('Error inserting initial video publication:', pubError);
				throw pubError;
			}
		}

		// 3. Crear relación si se especificó
		if (payload.relation && (payload.relation.target_session_id || payload.relation.target_video_id)) {
			const relInsert: VideoRelationInsert = {
				organization_id: payload.video.organization_id,
				source_video_id: videoData.id,
				target_session_id: payload.relation.target_session_id || null,
				target_video_id: payload.relation.target_video_id || null,
				relation_type: payload.relation.relation_type || 'derived_from_live',
				description: payload.relation.description || null
			};

			const { error: relError } = await supabase.from('video_relations').insert(relInsert);
			if (relError) {
				console.error('Error inserting video relation:', relError);
				throw relError;
			}
		}

		return videoData;
	},

	async addPublication(pub: VideoPublicationInsert): Promise<VideoPublication> {
		const { data, error } = await supabase
			.from('video_publications')
			.insert(pub)
			.select()
			.single();

		if (error) throw error;
		return data;
	},

	async addRelation(rel: VideoRelationInsert): Promise<VideoRelation> {
		const { data, error } = await supabase
			.from('video_relations')
			.insert(rel)
			.select()
			.single();

		if (error) throw error;
		return data;
	},

	async updateVideo(
		id: string,
		updates: Partial<Database['public']['Tables']['videos']['Update']>
	): Promise<Video> {
		const { data, error } = await supabase
			.from('videos')
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
		const { error } = await supabase.from('videos').delete().eq('id', id);
		if (error) throw error;
		return true;
	},

	// Métodos para consultar tablas crudas en el visor
	async getRawPublications(organizationId: string, limit = 100): Promise<VideoPublication[]> {
		const { data, error } = await supabase
			.from('video_publications')
			.select('*')
			.eq('organization_id', organizationId)
			.order('published_at', { ascending: false })
			.limit(limit);

		if (error) throw error;
		return data || [];
	},

	async getRawRelations(organizationId: string, limit = 100): Promise<VideoRelation[]> {
		const { data, error } = await supabase
			.from('video_relations')
			.select('*')
			.eq('organization_id', organizationId)
			.order('created_at', { ascending: false })
			.limit(limit);

		if (error) throw error;
		return data || [];
	}
};
