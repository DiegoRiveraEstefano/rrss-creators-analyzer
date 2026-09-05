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

export const analyticsService = {
	async getSessions(organizationId: string, creatorId?: string | null): Promise<StreamingSession[]> {
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
		const sessions = await this.getSessions(organizationId, creatorId);
		const sorted = [...sessions].sort(
			(a, b) => new Date(a.streamed_at).getTime() - new Date(b.streamed_at).getTime()
		);

		return {
			dates: sorted.map((s) => {
				const d = new Date(s.streamed_at);
				return `${d.getDate()}/${d.getMonth() + 1}`;
			}),
			viewers: sorted.map((s) => s.avg_ccv),
			earnings: sorted.map((s) => s.total_earnings),
			hours: sorted.map((s) => Number(s.hours_streamed || (s.duration_seconds / 3600).toFixed(1)))
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

	async getMaterializedCreatorSummary(organizationId: string) {
		const { data, error } = await supabase
			.from('mv_creator_performance_summary')
			.select('*')
			.eq('organization_id', organizationId);

		if (error) {
			// Si la vista aún no está materializada, retornamos vacío
			return [];
		}
		return data || [];
	}
};
