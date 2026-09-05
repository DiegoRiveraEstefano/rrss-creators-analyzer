import { queryOptions } from '@tanstack/svelte-query';
import {
	analyticsService,
	type AnalyticsSummary,
	type ChartDataSeries,
	type MvCreatorPerformance,
	type MvPlatformCategoryStats,
	type MvPlatformPerformance,
	type MvMonthlyRevenue,
	type MvCreatorContentTypeMetrics,
	type VDailyStreamAnalytics,
	type VCreatorOverallRankings,
	type VVideoPublicationDetails,
	type VRecentChannelActivity
} from '$lib/services/analyticsService';

export const analyticsQueryKeys = {
	all: ['analytics'] as const,
	summary: (orgId: string | undefined, creatorId?: string | null) =>
		[...analyticsQueryKeys.all, 'summary', { orgId, creatorId }] as const,
	chartData: (orgId: string | undefined, creatorId?: string | null) =>
		[...analyticsQueryKeys.all, 'chart', { orgId, creatorId }] as const,
	materializedSummary: (orgId: string | undefined) =>
		[...analyticsQueryKeys.all, 'materializedSummary', orgId] as const,
	platformPerformance: (orgId: string | undefined) =>
		[...analyticsQueryKeys.all, 'platformPerformance', orgId] as const,
	categoryStats: (orgId: string | undefined) =>
		[...analyticsQueryKeys.all, 'categoryStats', orgId] as const,
	monthlyRevenue: (orgId: string | undefined) =>
		[...analyticsQueryKeys.all, 'monthlyRevenue', orgId] as const,
	contentTypeMetrics: (orgId: string | undefined, creatorId?: string | null) =>
		[...analyticsQueryKeys.all, 'contentTypeMetrics', { orgId, creatorId }] as const,
	dailyStreamAnalytics: (orgId: string | undefined, creatorId?: string | null) =>
		[...analyticsQueryKeys.all, 'dailyStreamAnalytics', { orgId, creatorId }] as const,
	creatorRankings: (orgId: string | undefined) =>
		[...analyticsQueryKeys.all, 'creatorRankings', orgId] as const,
	videoPublicationDetails: (orgId: string | undefined, creatorId?: string | null) =>
		[...analyticsQueryKeys.all, 'videoPublicationDetails', { orgId, creatorId }] as const,
	recentActivity: (orgId: string | undefined, creatorId?: string | null) =>
		[...analyticsQueryKeys.all, 'recentActivity', { orgId, creatorId }] as const
};

export function analyticsSummaryQueryOptions(orgId: string | undefined, creatorId?: string | null) {
	return queryOptions({
		queryKey: analyticsQueryKeys.summary(orgId, creatorId),
		queryFn: async (): Promise<AnalyticsSummary> => {
			if (!orgId) {
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
					earningsPerHour: 0
				};
			}
			return analyticsService.getSummary(orgId, creatorId);
		},
		enabled: !!orgId
	});
}

export function analyticsChartQueryOptions(orgId: string | undefined, creatorId?: string | null) {
	return queryOptions({
		queryKey: analyticsQueryKeys.chartData(orgId, creatorId),
		queryFn: async (): Promise<ChartDataSeries> => {
			if (!orgId) return { dates: [], viewers: [], earnings: [], hours: [] };
			return analyticsService.getTimelineData(orgId, creatorId);
		},
		enabled: !!orgId
	});
}

export function materializedCreatorSummaryQueryOptions(orgId: string | undefined) {
	return queryOptions({
		queryKey: analyticsQueryKeys.materializedSummary(orgId),
		queryFn: async (): Promise<MvCreatorPerformance[]> => {
			if (!orgId) return [];
			return analyticsService.getMaterializedCreatorSummary(orgId);
		},
		enabled: !!orgId
	});
}

export function platformPerformanceQueryOptions(orgId: string | undefined) {
	return queryOptions({
		queryKey: analyticsQueryKeys.platformPerformance(orgId),
		queryFn: async (): Promise<MvPlatformPerformance[]> => {
			if (!orgId) return [];
			return analyticsService.getPlatformPerformanceSummary(orgId);
		},
		enabled: !!orgId
	});
}

export function platformCategoryStatsQueryOptions(orgId: string | undefined) {
	return queryOptions({
		queryKey: analyticsQueryKeys.categoryStats(orgId),
		queryFn: async (): Promise<MvPlatformCategoryStats[]> => {
			if (!orgId) return [];
			return analyticsService.getPlatformCategoryStats(orgId);
		},
		enabled: !!orgId
	});
}

export function monthlyRevenueQueryOptions(orgId: string | undefined) {
	return queryOptions({
		queryKey: analyticsQueryKeys.monthlyRevenue(orgId),
		queryFn: async (): Promise<MvMonthlyRevenue[]> => {
			if (!orgId) return [];
			return analyticsService.getMonthlyRevenueSummary(orgId);
		},
		enabled: !!orgId
	});
}

export function creatorContentTypeMetricsQueryOptions(orgId: string | undefined, creatorId?: string | null) {
	return queryOptions({
		queryKey: analyticsQueryKeys.contentTypeMetrics(orgId, creatorId),
		queryFn: async (): Promise<MvCreatorContentTypeMetrics[]> => {
			if (!orgId) return [];
			return analyticsService.getCreatorContentTypeMetrics(orgId, creatorId);
		},
		enabled: !!orgId
	});
}

export function dailyStreamAnalyticsQueryOptions(orgId: string | undefined, creatorId?: string | null) {
	return queryOptions({
		queryKey: analyticsQueryKeys.dailyStreamAnalytics(orgId, creatorId),
		queryFn: async (): Promise<VDailyStreamAnalytics[]> => {
			if (!orgId) return [];
			return analyticsService.getDailyStreamAnalytics(orgId, creatorId);
		},
		enabled: !!orgId
	});
}

export function creatorRankingsQueryOptions(orgId: string | undefined) {
	return queryOptions({
		queryKey: analyticsQueryKeys.creatorRankings(orgId),
		queryFn: async (): Promise<VCreatorOverallRankings[]> => {
			if (!orgId) return [];
			return analyticsService.getCreatorRankings(orgId);
		},
		enabled: !!orgId
	});
}

export function videoPublicationDetailsQueryOptions(orgId: string | undefined, creatorId?: string | null) {
	return queryOptions({
		queryKey: analyticsQueryKeys.videoPublicationDetails(orgId, creatorId),
		queryFn: async (): Promise<VVideoPublicationDetails[]> => {
			if (!orgId) return [];
			return analyticsService.getVideoPublicationDetails(orgId, creatorId);
		},
		enabled: !!orgId
	});
}

export function recentActivityQueryOptions(orgId: string | undefined, creatorId?: string | null) {
	return queryOptions({
		queryKey: analyticsQueryKeys.recentActivity(orgId, creatorId),
		queryFn: async (): Promise<VRecentChannelActivity[]> => {
			if (!orgId) return [];
			return analyticsService.getRecentChannelActivity(orgId, creatorId);
		},
		enabled: !!orgId
	});
}
