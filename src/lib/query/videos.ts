import { queryOptions } from '@tanstack/svelte-query';
import { videoService, type PublishedVideo } from '$lib/services/videoService';

export const videosQueryKeys = {
	all: ['videos'] as const,
	lists: () => [...videosQueryKeys.all, 'list'] as const,
	byOrg: (orgId: string | undefined) => [...videosQueryKeys.lists(), 'org', orgId] as const,
	byCreator: (creatorId: string | undefined) => [...videosQueryKeys.lists(), 'creator', creatorId] as const
};

export function videosByOrgQueryOptions(orgId: string | undefined, limit = 100) {
	return queryOptions({
		queryKey: [...videosQueryKeys.byOrg(orgId), { limit }],
		queryFn: async (): Promise<PublishedVideo[]> => {
			if (!orgId) return [];
			return videoService.getVideosByOrganization(orgId, limit);
		},
		enabled: !!orgId
	});
}

export function videosByCreatorQueryOptions(creatorId: string | undefined, limit = 100) {
	return queryOptions({
		queryKey: [...videosQueryKeys.byCreator(creatorId), { limit }],
		queryFn: async (): Promise<PublishedVideo[]> => {
			if (!creatorId) return [];
			return videoService.getVideosByCreator(creatorId, limit);
		},
		enabled: !!creatorId
	});
}
