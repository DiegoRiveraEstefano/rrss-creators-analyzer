<script lang="ts">
	import './layout.css';
	import { page } from '$app/state';
	import { QueryClientProvider } from '@tanstack/svelte-query';
	import { HotkeysProvider } from '@tanstack/svelte-hotkeys';
	import { queryClient } from '$lib/query/queryClient';
	import AppShell from '$lib/components/layout/AppShell.svelte';

	let { children } = $props();

	const isAuthRoute = $derived(
		page.url.pathname.startsWith('/login') ||
		page.url.pathname.startsWith('/register') ||
		page.url.pathname.startsWith('/forgot-password') ||
		page.url.pathname.startsWith('/update-password')
	);
</script>

<svelte:head>
	<title>RRSS Creators Analyzer | Streaming BI Suite</title>
</svelte:head>

<QueryClientProvider client={queryClient}>
	<HotkeysProvider>
		{#if isAuthRoute}
			<div class="min-h-screen bg-[#090D16] text-[#F9FAFB] flex flex-col justify-center items-center p-4">
				{@render children()}
			</div>
		{:else}
			<AppShell>
				{@render children()}
			</AppShell>
		{/if}
	</HotkeysProvider>
</QueryClientProvider>
