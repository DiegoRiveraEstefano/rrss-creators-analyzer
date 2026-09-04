import { QueryClient } from '@tanstack/svelte-query';

export const queryClient = new QueryClient({
	defaultOptions: {
		queries: {
			staleTime: 1000 * 60 * 2, // 2 minutos
			gcTime: 1000 * 60 * 10, // 10 minutos
			refetchOnWindowFocus: false,
			retry: 1
		},
		mutations: {
			retry: 0
		}
	}
});
