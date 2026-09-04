import { queryOptions } from '@tanstack/svelte-query';
import { analyticsService, type AnalyticsSummary, type ChartDataSeries } from '$lib/services/analyticsService';

export const analyticsQueryKeys = {
	all: ['analytics'] as const,
	summary: (orgId: string | undefined, creatorId?: string | null) =>
		[...analyticsQueryKeys.all, 'summary', { orgId, creatorId }] as const,
	chartData: (orgId: string | undefined, creatorId?: string | null) =>
		[...analyticsQueryKeys.all, 'chart', { orgId, creatorId }] as const,
	materializedSummary: (orgId: string | undefined) =>
		[...analyticsQueryKeys.all, 'materializedSummary', orgId] as const
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
		queryFn: async () => {
			if (!orgId) return [];
			return analyticsService.getMaterializedCreatorSummary(orgId);
		},
		enabled: !!orgId
	});
}
