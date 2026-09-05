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
