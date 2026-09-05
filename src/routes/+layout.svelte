<script lang="ts">
	import './layout.css';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { QueryClientProvider } from '@tanstack/svelte-query';
	import { HotkeysProvider } from '@tanstack/svelte-hotkeys';
	import { queryClient } from '$lib/query/queryClient';
	import { authStore } from '$lib/stores/authStore.svelte';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import { Radio, Loader2 } from 'lucide-svelte';

	let { children } = $props();

	const isAuthRoute = $derived(
		page.url.pathname.startsWith('/login') ||
		page.url.pathname.startsWith('/register') ||
		page.url.pathname.startsWith('/forgot-password') ||
		page.url.pathname.startsWith('/update-password')
	);

	onMount(async () => {
		await Promise.all([authStore.init(), tenantStore.init()]);
	});

	// Middleware reactivo de protección y redirección de rutas
	$effect(() => {
		if (!authStore.isInitialized) return;

		const pathname = page.url.pathname;
		const isAuth = isAuthRoute;

		// 1. Ruta protegida sin autenticación -> Redirigir a login
		if (!authStore.isAuthenticated && !isAuth) {
			const redirectParam = pathname !== '/' ? `?redirectTo=${encodeURIComponent(pathname + page.url.search)}` : '';
			goto(`/login${redirectParam}`, { replaceState: true });
			return;
		}

		// 2. Ruta de auth con sesión activa -> Redirigir al dashboard
		if (authStore.isAuthenticated && isAuth && !pathname.startsWith('/update-password')) {
			const redirectTo = page.url.searchParams.get('redirectTo') || '/';
			goto(redirectTo, { replaceState: true });
		}
	});
</script>

<svelte:head>
	<title>RRSS Creators Analyzer | Streaming BI Suite</title>
</svelte:head>

<QueryClientProvider client={queryClient}>
	<HotkeysProvider>
		{#if !authStore.isInitialized}
			<div class="min-h-screen bg-[#090D16] text-[#F9FAFB] flex flex-col justify-center items-center gap-3">
				<div class="h-12 w-12 rounded-2xl bg-gradient-to-tr from-[#6366F1] to-[#06B6D4] flex items-center justify-center text-white shadow-xl shadow-indigo-500/20 animate-pulse">
					<Radio size={24} />
				</div>
				<div class="flex items-center gap-2 text-xs text-gray-400 font-medium">
					<Loader2 size={14} class="animate-spin text-indigo-400" />
					<span>Verificando sesión...</span>
				</div>
			</div>
		{:else if isAuthRoute}
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
