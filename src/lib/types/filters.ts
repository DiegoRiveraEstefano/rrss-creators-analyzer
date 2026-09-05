import type { PlatformType } from '$lib/supabase/database.types';

export type DateRangePreset = '7d' | '30d' | '90d' | 'year' | 'all' | 'custom';

export interface DateRangeFilterValue {
	preset: DateRangePreset;
	from?: string; // YYYY-MM-DD
	to?: string;   // YYYY-MM-DD
}

export interface NumericRangeFilterValue {
	min?: number | null;
	max?: number | null;
}

export interface DashboardFilterState {
	dateRange: DateRangeFilterValue;
	platforms: PlatformType[];
	creatorIds?: string[];
	minCcv?: number | null;
	minEarnings?: number | null;
	categories: string[];
}

export interface VideoTableFilterState {
	creatorIds: string[];
	platforms: PlatformType[];
	categories: string[];
	minViews?: number | null;
	minRevenue?: number | null;
	onlyLiveDerived: boolean;
	status?: string;
}

export interface LiveTableFilterState {
	creatorIds: string[];
	dateRange: DateRangeFilterValue;
	platforms: PlatformType[];
	categories: string[];
	minCcv?: number | null;
	minPeak?: number | null;
	minEarnings?: number | null;
	minDurationHours?: number | null;
}

export interface RawDataTableFilterState {
	dateRange: DateRangeFilterValue;
	platforms: PlatformType[];
	minDurationMinutes?: number | null;
	minEarnings?: number | null;
	minCcv?: number | null;
}

export interface AlertTableFilterState {
	severities: ('critical' | 'warning' | 'info')[];
	statuses: ('active' | 'resolved' | 'dismissed')[];
	platforms: PlatformType[];
}

export interface RosterFilterState {
	platforms: PlatformType[];
	statuses: ('active' | 'inactive' | 'paused')[];
	minFollowers?: number | null;
}

export interface ViewsFilterState {
	creatorPerf: {
		platforms: PlatformType[];
		minStreams?: number | null;
		minCombinedRevenue?: number | null;
		minAvgCcv?: number | null;
	};
	platformPerf: {
		platforms: PlatformType[];
		minTotalHours?: number | null;
		minCombinedRevenue?: number | null;
	};
	platformCategory: {
		platforms: PlatformType[];
		minSessions?: number | null;
		minCcv?: number | null;
		minRevenue?: number | null;
		categories: string[];
	};
	monthlyRevenue: {
		dateRange: DateRangeFilterValue;
		minMonthlyRevenue?: number | null;
		minStreamHours?: number | null;
	};
	contentType: {
		platforms: PlatformType[];
		publicationTypes: string[];
		minViews?: number | null;
		minEngagementRate?: number | null;
		minRevenue?: number | null;
	};
	creatorRankings: {
		platforms: PlatformType[];
		topN?: number | null;
		minAvgCcv?: number | null;
	};
	dailyStream: {
		dateRange: DateRangeFilterValue;
		platforms: PlatformType[];
		minEarningsPerHour?: number | null;
		minAvgCcv?: number | null;
	};
	videoDetails: {
		platforms: PlatformType[];
		publicationTypes: string[];
		categories: string[];
		minRoiPercentage?: number | null;
		minViews?: number | null;
		minRevenue?: number | null;
	};
	recentActivity: {
		dateRange: DateRangeFilterValue;
		activityTypes: ('stream' | 'video' | 'alert')[];
		platforms: PlatformType[];
	};
}
