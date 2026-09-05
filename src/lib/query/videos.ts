import { queryOptions } from '@tanstack/svelte-query';
import { videoService, type VideoWithDetails } from '$lib/services/videoService';

export const videosQueryKeys = {
	all: ['videos'] as const,
	lists: () => [...videosQueryKeys.all, 'list'] as const,
	list: (orgId: string | undefined, creatorId?: string | null) =>
		[...videosQueryKeys.lists(), { orgId, creatorId }] as const,
	detail: (id: string | undefined) => [...videosQueryKeys.all, 'detail', id] as const
};

export function videosQueryOptions(orgId: string | undefined, creatorId?: string | null, limit = 100) {
	return queryOptions({
		queryKey: [...videosQueryKeys.list(orgId, creatorId), { limit }],
		queryFn: async (): Promise<VideoWithDetails[]> => {
			if (!orgId) return [];
			return videoService.getVideos(orgId, creatorId, limit);
		},
		enabled: !!orgId
	});
}

export function videoDetailQueryOptions(id: string | undefined) {
	return queryOptions({
		queryKey: videosQueryKeys.detail(id),
		queryFn: async (): Promise<VideoWithDetails | null> => {
			if (!id) return null;
			return videoService.getVideoById(id);
		},
		enabled: !!id
	});
}
