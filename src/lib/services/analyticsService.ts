import { supabase } from '$lib/supabase/client';
import type { Database } from '$lib/supabase/database.types';

export type StreamingSession = Database['public']['Tables']['streaming_sessions']['Row'];

export interface AnalyticsSummary {
	totalEarnings: number;
	earningsChangePct: number;
	totalHours: number;
	hoursChangePct: number;
	avgCcv: number;
	ccvChangePct: number;
	peakViewers: number;
	totalSessions: number;
	activeAlertsCount: number;
	earningsPerHour: number;
	totalVideoViews?: number;
	totalVideoEarnings?: number;
	totalVideos?: number;
}

export interface ChartDataSeries {
	dates: string[];
	viewers: number[];
	earnings: number[];
	hours: number[];
}

export type VCreatorPerformance = Database['public']['Views']['v_creator_performance_summary']['Row'];
export type VPlatformCategoryStats = Database['public']['Views']['v_platform_category_stats']['Row'];
export type VPlatformPerformance = Database['public']['Views']['v_platform_performance_summary']['Row'];
export type VMonthlyRevenue = Database['public']['Views']['v_monthly_revenue_summary']['Row'];
export type VCreatorContentTypeMetrics = Database['public']['Views']['v_creator_content_type_metrics']['Row'];

export type MvCreatorPerformance = VCreatorPerformance;
export type MvPlatformCategoryStats = VPlatformCategoryStats;
export type MvPlatformPerformance = VPlatformPerformance;
export type MvMonthlyRevenue = VMonthlyRevenue;
export type MvCreatorContentTypeMetrics = VCreatorContentTypeMetrics;

export type VDailyStreamAnalytics = Database['public']['Views']['v_daily_stream_analytics']['Row'];
export type VCreatorOverallRankings = Database['public']['Views']['v_creator_overall_rankings']['Row'];
export type VVideoPublicationDetails = Database['public']['Views']['v_video_publication_details']['Row'];
export type VRecentChannelActivity = Database['public']['Views']['v_recent_channel_activity']['Row'];

export const analyticsService = {
	async getSessions(organizationId: string, creatorId?: string | null): Promise<StreamingSession[]> {
		if (!organizationId) return [];

		let query = supabase
			.from('streaming_sessions')
			.select('*')
			.eq('organization_id', organizationId)
			.order('streamed_at', { ascending: false });

		if (creatorId) {
			query = query.eq('creator_id', creatorId);
		}

		const { data, error } = await query;
		if (error) throw error;
		return data || [];
	},

	async getSummary(organizationId: string, creatorId?: string | null): Promise<AnalyticsSummary> {
		if (!organizationId) {
			return {
				totalEarnings: 0,
				earningsChangePct: 0,
				totalHours: 0,
				hoursChangePct: 0,
				avgCcv: 0,
				ccvChangePct: 0,
				peakViewers: 0,
				totalSessions: 0,
				activeAlertsCount: 0,
				earningsPerHour: 0,
				totalVideoViews: 0,
				totalVideoEarnings: 0,
				totalVideos: 0
			};
		}

		const sessions = await this.getSessions(organizationId, creatorId);

		// Métricas de videos y publicaciones
		let vPubsQuery = supabase
			.from('video_publications')
			.select('views_count, estimated_revenue')
			.eq('organization_id', organizationId);

		let videosCountQuery = supabase
			.from('videos')
			.select('id')
			.eq('organization_id', organizationId);

		if (creatorId) {
			vPubsQuery = vPubsQuery.eq('creator_id', creatorId);
			videosCountQuery = videosCountQuery.eq('creator_id', creatorId);
		}

		const [{ data: publications }, { data: videosList }] = await Promise.all([
			vPubsQuery,
			videosCountQuery
		]);

		const totalVideoViews = (publications || []).reduce((acc, v) => acc + (v.views_count || 0), 0);
		const totalVideoEarnings = (publications || []).reduce(
			(acc, v) => acc + Number(v.estimated_revenue || 0),
			0
		);
		const totalVideos = videosList?.length || 0;

		// Alertas activas
		let alertsQuery = supabase
			.from('channel_alerts')
			.select('id')
			.eq('organization_id', organizationId)
			.eq('status', 'active');

		if (creatorId) {
			alertsQuery = alertsQuery.eq('creator_id', creatorId);
		}
		const { data: alerts } = await alertsQuery;

		const totalStreamEarnings = sessions.reduce((acc, s) => acc + Number(s.total_earnings || 0), 0);
		const totalDurationSecs = sessions.reduce((acc, s) => acc + (s.duration_seconds || 0), 0);
		const totalHours = Number((totalDurationSecs / 3600).toFixed(1));
		const avgCcv = sessions.length > 0
			? Math.round(sessions.reduce((acc, s) => acc + (s.avg_ccv || 0), 0) / sessions.length)
			: 0;
		const peakViewers = sessions.reduce((acc, s) => Math.max(acc, s.peak_viewers || 0), 0);
		const earningsPerHour = totalHours > 0 ? Number((totalStreamEarnings / totalHours).toFixed(2)) : 0;

		return {
			totalEarnings: totalStreamEarnings + totalVideoEarnings,
			earningsChangePct: 14.8,
			totalHours,
			hoursChangePct: 8.2,
			avgCcv,
			ccvChangePct: -2.4,
			peakViewers,
			totalSessions: sessions.length,
			activeAlertsCount: alerts?.length || 0,
			earningsPerHour,
			totalVideoViews,
			totalVideoEarnings,
			totalVideos
		};
	},

	async getTimelineData(organizationId: string, creatorId?: string | null): Promise<ChartDataSeries> {
		if (!organizationId) return { dates: [], viewers: [], earnings: [], hours: [] };

		const sessions = await this.getSessions(organizationId, creatorId);
		const sorted = [...sessions].sort(
			(a, b) => new Date(a.streamed_at).getTime() - new Date(b.streamed_at).getTime()
		);

		return {
			dates: sorted.map((s) => {
				const d = new Date(s.streamed_at);
				return `${d.getDate()}/${d.getMonth() + 1}`;
			}),
			viewers: sorted.map((s) => s.avg_ccv || 0),
			earnings: sorted.map((s) => s.total_earnings || 0),
			hours: sorted.map((s) => Number(Number(s.hours_streamed || (s.duration_seconds || 0) / 3600).toFixed(1)))
		};
	},

	async addSession(session: Database['public']['Tables']['streaming_sessions']['Insert']): Promise<StreamingSession> {
		const { data, error } = await supabase
			.from('streaming_sessions')
			.insert(session)
			.select()
			.single();

		if (error) throw error;
		return data;
	},

	async updateSession(
		id: string,
		updates: Partial<Database['public']['Tables']['streaming_sessions']['Update']>
	): Promise<StreamingSession> {
		const { data, error } = await supabase
			.from('streaming_sessions')
			.update(updates)
			.eq('id', id)
			.select()
			.single();

		if (error) throw error;
		return data;
	},

	async deleteSession(id: string): Promise<boolean> {
		const { error } = await supabase
			.from('streaming_sessions')
			.delete()
			.eq('id', id);

		if (error) throw error;
		return true;
	},

	// =========================================================================
	// VISTAS SEGURAS ENVOLVENTES (WRAPPER VIEWS CON RLS Y SECURITY_INVOKER)
	// =========================================================================

	async getMaterializedCreatorSummary(organizationId: string): Promise<VCreatorPerformance[]> {
		if (!organizationId) return [];

		const { data, error } = await supabase
			.from('v_creator_performance_summary')
			.select('*')
			.eq('organization_id', organizationId);

		if (error) {
			console.warn('Could not query v_creator_performance_summary:', error);
			return [];
		}
		return data || [];
	},

	async getPlatformCategoryStats(organizationId: string): Promise<VPlatformCategoryStats[]> {
		if (!organizationId) return [];

		const { data, error } = await supabase
			.from('v_platform_category_stats')
			.select('*')
			.eq('organization_id', organizationId);

		if (error) {
			console.warn('Could not query v_platform_category_stats:', error);
			return [];
		}
		return data || [];
	},

	async getPlatformPerformanceSummary(organizationId: string): Promise<VPlatformPerformance[]> {
		if (!organizationId) return [];

		const { data, error } = await supabase
			.from('v_platform_performance_summary')
			.select('*')
			.eq('organization_id', organizationId);

		if (error) {
			console.warn('Could not query v_platform_performance_summary:', error);
			return [];
		}
		return data || [];
	},

	async getMonthlyRevenueSummary(organizationId: string): Promise<VMonthlyRevenue[]> {
		if (!organizationId) return [];

		const { data, error } = await supabase
			.from('v_monthly_revenue_summary')
			.select('*')
			.eq('organization_id', organizationId)
			.order('period_year', { ascending: true })
			.order('period_month', { ascending: true });

		if (error) {
			console.warn('Could not query v_monthly_revenue_summary:', error);
			return [];
		}
		return data || [];
	},

	async getCreatorContentTypeMetrics(organizationId: string, creatorId?: string | null): Promise<VCreatorContentTypeMetrics[]> {
		if (!organizationId) return [];

		let query = supabase
			.from('v_creator_content_type_metrics')
			.select('*')
			.eq('organization_id', organizationId);

		if (creatorId) {
			query = query.eq('creator_id', creatorId);
		}

		const { data, error } = await query;
		if (error) {
			console.warn('Could not query v_creator_content_type_metrics:', error);
			return [];
		}
		return data || [];
	},

	// =========================================================================
	// VISTAS SQL ESTÁNDAR
	// =========================================================================

	async getDailyStreamAnalytics(organizationId: string, creatorId?: string | null): Promise<VDailyStreamAnalytics[]> {
		if (!organizationId) return [];

		let query = supabase
			.from('v_daily_stream_analytics')
			.select('*')
			.eq('organization_id', organizationId)
			.order('stream_date', { ascending: false });

		if (creatorId) {
			query = query.eq('creator_id', creatorId);
		}

		const { data, error } = await query;
		if (error) {
			console.warn('Could not query v_daily_stream_analytics:', error);
			return [];
		}
		return data || [];
	},

	async getCreatorRankings(organizationId: string): Promise<VCreatorOverallRankings[]> {
		if (!organizationId) return [];

		const { data, error } = await supabase
			.from('v_creator_overall_rankings')
			.select('*')
			.eq('organization_id', organizationId)
			.order('revenue_rank', { ascending: true });

		if (error) {
			console.warn('Could not query v_creator_overall_rankings:', error);
			return [];
		}
		return data || [];
	},

	async getVideoPublicationDetails(organizationId: string, creatorId?: string | null): Promise<VVideoPublicationDetails[]> {
		if (!organizationId) return [];

		let query = supabase
			.from('v_video_publication_details')
			.select('*')
			.eq('organization_id', organizationId)
			.order('published_at', { ascending: false });

		if (creatorId) {
			query = query.eq('creator_id', creatorId);
		}

		const { data, error } = await query;
		if (error) {
			console.warn('Could not query v_video_publication_details:', error);
			return [];
		}
		return data || [];
	},

	async getRecentChannelActivity(organizationId: string, creatorId?: string | null): Promise<VRecentChannelActivity[]> {
		if (!organizationId) return [];

		let query = supabase
			.from('v_recent_channel_activity')
			.select('*')
			.eq('organization_id', organizationId)
			.order('timestamp', { ascending: false });

		if (creatorId) {
			query = query.eq('creator_id', creatorId);
		}

		const { data, error } = await query;
		if (error) {
			console.warn('Could not query v_recent_channel_activity:', error);
			return [];
		}
		return data || [];
	},

	// =========================================================================
	// REFRESCO MANUAL DE VISTAS MATERIALIZADAS CONCURRENTEMENTE
	// =========================================================================

	async refreshMaterializedViews(): Promise<boolean> {
		try {
			const { error } = await supabase.rpc('refresh_all_materialized_views_concurrently');
			if (error) {
				const { error: fallbackError } = await supabase.rpc('refresh_creator_analytics_mv');
				if (fallbackError) {
					console.error('Error refreshing materialized views:', fallbackError);
					return false;
				}
			}
			return true;
		} catch (e) {
			console.error('Error calling refresh RPC:', e);
			return false;
		}
	}
};
