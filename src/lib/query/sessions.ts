import { queryOptions } from '@tanstack/svelte-query';
import { analyticsService, type StreamingSession } from '$lib/services/analyticsService';

export const sessionsQueryKeys = {
	all: ['sessions'] as const,
	lists: () => [...sessionsQueryKeys.all, 'list'] as const,
	list: (orgId: string | undefined, creatorId?: string | null) =>
		[...sessionsQueryKeys.lists(), { orgId, creatorId }] as const
};

export function sessionsQueryOptions(orgId: string | undefined, creatorId?: string | null) {
	return queryOptions({
		queryKey: sessionsQueryKeys.list(orgId, creatorId),
		queryFn: async (): Promise<StreamingSession[]> => {
			if (!orgId) return [];
			return analyticsService.getSessions(orgId, creatorId);
		},
		enabled: !!orgId
	});
}
