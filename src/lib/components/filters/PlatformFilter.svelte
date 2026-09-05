<script lang="ts">
	import type { PlatformType } from '$lib/supabase/database.types';
	import { Tv, Video, Radio, Sparkles } from 'lucide-svelte';

	interface Props {
		selected?: PlatformType[];
		selectedPlatforms?: PlatformType[];
		availablePlatforms?: PlatformType[];
		onchange?: (platforms: PlatformType[]) => void;
	}

	let {
		selected = $bindable([]),
		selectedPlatforms,
		availablePlatforms = ['twitch', 'youtube', 'kick', 'tiktok'],
		onchange
	}: Props = $props();

	let currentSelected = $derived(selectedPlatforms !== undefined ? selectedPlatforms : selected);

	function togglePlatform(p: PlatformType) {
		const next = currentSelected.includes(p)
			? currentSelected.filter((item) => item !== p)
			: [...currentSelected, p];
		selected = next;
		onchange?.(next);
	}

	function selectAll() {
		const next = [...availablePlatforms];
		selected = next;
		onchange?.(next);
	}

	function clearAll() {
		const next: PlatformType[] = [];
		selected = next;
		onchange?.(next);
	}

	const platformMeta: Record<string, { label: string; color: string }> = {
		twitch: { label: 'Twitch', color: 'hover:border-purple-500' },
		youtube: { label: 'YouTube', color: 'hover:border-red-500' },
		kick: { label: 'Kick', color: 'hover:border-emerald-500' },
		tiktok: { label: 'TikTok', color: 'hover:border-cyan-500' },
		other: { label: 'Otras', color: 'hover:border-gray-500' }
	};
</script>

<div class="space-y-2">
	<div class="flex items-center justify-between text-[11px] text-gray-400">
		<span>Selecciona plataformas:</span>
		<div class="flex gap-2">
			<button type="button" onclick={selectAll} class="hover:text-indigo-400 transition-colors">
				Todas
			</button>
			<span>•</span>
			<button type="button" onclick={clearAll} class="hover:text-indigo-400 transition-colors">
				Ninguna
			</button>
		</div>
	</div>

	<div class="grid grid-cols-2 gap-2">
		{#each availablePlatforms as p}
			{@const isSelected = currentSelected.includes(p)}
			{@const meta = platformMeta[p] || { label: p, color: '' }}
			<button
				type="button"
				onclick={() => togglePlatform(p)}
				class="flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-medium transition-all {isSelected
					? 'border-indigo-500 bg-indigo-600/20 text-white font-semibold'
					: `border-[#2D3748] bg-[#111827] text-gray-400 ${meta.color}`}"
			>
				<span class="h-2 w-2 rounded-full {isSelected ? 'bg-indigo-400' : 'bg-gray-600'}"></span>
				<span class="capitalize">{meta.label}</span>
			</button>
		{/each}
	</div>
</div>
