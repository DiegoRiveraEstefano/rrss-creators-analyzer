import { queryOptions } from '@tanstack/svelte-query';
import { creatorService, type Creator, type CreatorWithChannels } from '$lib/services/creatorService';
import type { Database, PlatformType, CreatorStatus } from '$lib/supabase/database.types';

export const creatorsQueryKeys = {
	all: ['creators'] as const,
	lists: () => [...creatorsQueryKeys.all, 'list'] as const,
	list: (orgId: string | undefined) => [...creatorsQueryKeys.lists(), orgId] as const,
	details: () => [...creatorsQueryKeys.all, 'detail'] as const,
	detail: (id: string | undefined) => [...creatorsQueryKeys.details(), id] as const
};

export function creatorsQueryOptions(orgId: string | undefined) {
	return queryOptions({
		queryKey: creatorsQueryKeys.list(orgId),
		queryFn: async (): Promise<CreatorWithChannels[]> => {
			if (!orgId) return [];
			return creatorService.getCreators(orgId);
		},
		enabled: !!orgId
	});
}

export function creatorDetailQueryOptions(id: string | undefined) {
	return queryOptions({
		queryKey: creatorsQueryKeys.detail(id),
		queryFn: async (): Promise<CreatorWithChannels | null> => {
			if (!id) return null;
			return creatorService.getCreatorById(id);
		},
		enabled: !!id
	});
}
