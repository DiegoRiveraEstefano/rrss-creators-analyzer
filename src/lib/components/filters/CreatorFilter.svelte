<script lang="ts">
	import { Search, Check, Users } from 'lucide-svelte';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import type { CreatorWithChannels } from '$lib/services/creatorService';
	import Badge from '$lib/components/ui/Badge.svelte';

	interface Props {
		label?: string;
		selected?: string[];
		creators?: CreatorWithChannels[];
		onchange?: (selected: string[]) => void;
	}

	let {
		label,
		selected = $bindable([]),
		creators,
		onchange
	}: Props = $props();

	let searchQuery = $state('');

	let availableCreators = $derived(
		creators && creators.length > 0 ? creators : tenantStore.creators
	);

	let filteredCreators = $derived(
		availableCreators.filter(
			(c) =>
				c.display_name.toLowerCase().includes(searchQuery.toLowerCase().trim()) ||
				c.handle.toLowerCase().includes(searchQuery.toLowerCase().trim())
		)
	);

	function toggleCreator(id: string) {
		const next = selected.includes(id)
			? selected.filter((item) => item !== id)
			: [...selected, id];
		selected = next;
		onchange?.(next);
	}

	function selectAll() {
		const next = availableCreators.map((c) => c.id);
		selected = next;
		onchange?.(next);
	}

	function clearAll() {
		const next: string[] = [];
		selected = next;
		onchange?.(next);
	}
</script>

<div class="space-y-2">
	<div class="flex items-center justify-between text-[11px] text-gray-400">
		<span>{label || 'Creadores seleccionados:'}</span>
		<div class="flex gap-2">
			<button type="button" onclick={selectAll} class="hover:text-indigo-400 transition-colors">
				Todos
			</button>
			<span>•</span>
			<button type="button" onclick={clearAll} class="hover:text-indigo-400 transition-colors">
				Ninguno
			</button>
		</div>
	</div>

	{#if availableCreators.length > 3}
		<div class="relative">
			<Search class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" size={13} />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Buscar creador..."
				class="w-full rounded-lg bg-[#111827] border border-[#2D3748] py-1 pl-7 pr-3 text-xs text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none"
			/>
		</div>
	{/if}

	<div class="max-h-48 overflow-y-auto space-y-1.5 pr-1">
		{#if availableCreators.length === 0}
			<div class="py-3 text-center text-xs text-gray-500">No hay creadores disponibles</div>
		{:else if filteredCreators.length === 0}
			<div class="py-3 text-center text-xs text-gray-500">Ningún creador coincide con la búsqueda</div>
		{:else}
			{#each filteredCreators as creator}
				{@const isChecked = selected.includes(creator.id)}
				<button
					type="button"
					onclick={() => toggleCreator(creator.id)}
					class="flex w-full items-center justify-between rounded-xl p-2 text-left transition-all border {isChecked
						? 'border-indigo-500/50 bg-indigo-600/15 text-white'
						: 'border-[#1F2937] bg-[#111827] text-gray-300 hover:border-gray-700 hover:bg-gray-800/60'}"
				>
					<div class="flex items-center gap-2.5 min-w-0">
						<div
							class="flex h-4 w-4 shrink-0 items-center justify-center rounded border {isChecked
								? 'border-indigo-500 bg-indigo-600 text-white'
								: 'border-gray-600 bg-gray-900'}"
						>
							{#if isChecked}
								<Check size={11} strokeWidth={3} />
							{/if}
						</div>

						<img
							src={creator.avatar_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop&q=80'}
							alt={creator.display_name}
							class="h-6 w-6 rounded-lg object-cover ring-1 ring-gray-700 shrink-0"
						/>

						<div class="truncate">
							<div class="text-xs font-semibold leading-tight text-white truncate">
								{creator.display_name}
							</div>
							<div class="text-[10px] text-gray-400 font-mono truncate">
								@{creator.handle}
							</div>
						</div>
					</div>

					<Badge
						variant={creator.primary_platform === 'twitch' ? 'purple' : creator.primary_platform === 'youtube' ? 'danger' : 'cyan'}
						size="sm"
					>
						{creator.primary_platform}
					</Badge>
				</button>
			{/each}
		{/if}
	</div>
</div>
