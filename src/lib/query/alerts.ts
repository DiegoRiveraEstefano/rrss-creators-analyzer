import { queryOptions } from '@tanstack/svelte-query';
import { alertsService, type ChannelAlert } from '$lib/services/alertsService';

export const alertsQueryKeys = {
	all: ['alerts'] as const,
	lists: () => [...alertsQueryKeys.all, 'list'] as const,
	list: (orgId: string | undefined, creatorId?: string | null) =>
		[...alertsQueryKeys.lists(), { orgId, creatorId }] as const
};

export function alertsQueryOptions(orgId: string | undefined, creatorId?: string | null) {
	return queryOptions({
		queryKey: alertsQueryKeys.list(orgId, creatorId),
		queryFn: async (): Promise<ChannelAlert[]> => {
			if (!orgId) return [];
			return alertsService.getAlerts(orgId, creatorId);
		},
		enabled: !!orgId
	});
}
