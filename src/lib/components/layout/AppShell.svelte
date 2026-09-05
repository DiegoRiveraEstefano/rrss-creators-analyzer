<script lang="ts">
	import { onMount, type Snippet } from 'svelte';
	import { goto } from '$app/navigation';
	import { createHotkeys, createHotkeySequences } from '@tanstack/svelte-hotkeys';
	import { useQueryClient } from '@tanstack/svelte-query';
	import Sidebar from './Sidebar.svelte';
	import Topbar from './Topbar.svelte';
	import CommandPalette from './CommandPalette.svelte';
	import HotkeysModal from './HotkeysModal.svelte';
	import { authStore } from '$lib/stores/authStore.svelte';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';

	interface Props {
		children?: Snippet;
	}

	let { children }: Props = $props();

	let isCommandPaletteOpen = $state(false);
	let isHotkeysModalOpen = $state(false);

	const queryClient = useQueryClient();

	// Atajos simples con TanStack Hotkeys
	createHotkeys([
		{
			hotkey: 'Mod+K',
			callback: (e) => {
				e?.preventDefault();
				isCommandPaletteOpen = !isCommandPaletteOpen;
			}
		},
		{
			hotkey: { key: '?', shift: true },
			callback: () => {
				isHotkeysModalOpen = !isHotkeysModalOpen;
			}
		},
		{
			hotkey: 'Shift+R',
			callback: () => {
				queryClient.invalidateQueries();
			}
		},
		{
			hotkey: 'Escape',
			callback: () => {
				isCommandPaletteOpen = false;
				isHotkeysModalOpen = false;
			}
		}
	]);

	// Atajos de secuencias de navegación rápida ('g' luego tecla)
	createHotkeySequences([
		{
			sequence: ['G', 'D'],
			callback: () => {
				tenantStore.selectCreator(null);
				goto('/');
			}
		},
		{
			sequence: ['G', 'R'],
			callback: () => goto('/roster')
		},
		{
			sequence: ['G', 'V'],
			callback: () => goto('/videos')
		},
		{
			sequence: ['G', 'I'],
			callback: () => goto('/import')
		},
		{
			sequence: ['G', 'A'],
			callback: () => goto('/alerts')
		},
		{
			sequence: ['G', 'T'],
			callback: () => goto('/tenants')
		}
	]);
</script>

<div class="flex min-h-screen bg-[#090D16] text-[#F9FAFB]">
	<!-- Sidebar fija a la izquierda -->
	<Sidebar />

	<!-- Contenedor principal con Topbar y contenido dinámico -->
	<div class="flex flex-1 flex-col overflow-x-hidden">
		<Topbar
			onOpenCommandPalette={() => (isCommandPaletteOpen = true)}
			onOpenHotkeys={() => (isHotkeysModalOpen = true)}
		/>

		<main class="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto space-y-6">
			{#if tenantStore.isLoading}
				<div class="flex h-64 items-center justify-center">
					<div class="flex flex-col items-center gap-3 text-gray-400">
						<div
							class="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent"
						></div>
						<span class="text-xs font-mono">Cargando espacio de trabajo...</span>
					</div>
				</div>
			{:else}
				{#if children}
					{@render children()}
				{/if}
			{/if}
		</main>
	</div>

	<!-- Paleta de Comandos y Modal de Atajos de Teclado -->
	<CommandPalette
		isOpen={isCommandPaletteOpen}
		onClose={() => (isCommandPaletteOpen = false)}
		onOpenHotkeys={() => {
			isCommandPaletteOpen = false;
			isHotkeysModalOpen = true;
		}}
	/>

	<HotkeysModal
		isOpen={isHotkeysModalOpen}
		onClose={() => (isHotkeysModalOpen = false)}
	/>
</div>
