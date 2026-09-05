<script lang="ts">
	import { Search, Check } from 'lucide-svelte';

	interface OptionItem {
		value: string;
		label: string;
		count?: number;
	}

	interface Props {
		label?: string;
		options: OptionItem[];
		selected?: string[];
		placeholder?: string;
		searchPlaceholder?: string;
		maxHeight?: string;
		onchange?: (selected: string[]) => void;
	}

	let {
		label,
		options,
		selected = $bindable([]),
		placeholder,
		searchPlaceholder = 'Buscar...',
		maxHeight = 'max-h-40',
		onchange
	}: Props = $props();

	let effectivePlaceholder = $derived(placeholder || searchPlaceholder);
	let searchQuery = $state('');

	let filteredOptions = $derived(
		options.filter(
			(o) =>
				o.label.toLowerCase().includes(searchQuery.toLowerCase().trim()) ||
				o.value.toLowerCase().includes(searchQuery.toLowerCase().trim())
		)
	);

	function toggleOption(val: string) {
		const next = selected.includes(val)
			? selected.filter((item) => item !== val)
			: [...selected, val];
		selected = next;
		onchange?.(next);
	}
</script>

<div class="space-y-2">
	{#if label}
		<div class="text-xs text-gray-300 font-medium">{label}</div>
	{/if}

	{#if options.length > 5}
		<div class="relative">
			<Search class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" size={13} />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder={effectivePlaceholder}
				class="w-full rounded-lg bg-[#111827] border border-[#2D3748] py-1 pl-7 pr-3 text-xs text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none"
			/>
		</div>
	{/if}

	<div class="{maxHeight} overflow-y-auto space-y-1 pr-1">
		{#if filteredOptions.length === 0}
			<div class="py-3 text-center text-xs text-gray-500">Sin opciones disponibles</div>
		{:else}
			{#each filteredOptions as opt}
				{@const isChecked = selected.includes(opt.value)}
				<button
					type="button"
					onclick={() => toggleOption(opt.value)}
					class="flex w-full items-center justify-between rounded-lg px-2.5 py-1.5 text-left text-xs transition-colors {isChecked
						? 'bg-indigo-600/20 text-indigo-300 font-medium'
						: 'text-gray-300 hover:bg-gray-800 hover:text-white'}"
				>
					<div class="flex items-center gap-2 truncate">
						<div
							class="flex h-3.5 w-3.5 items-center justify-center rounded border {isChecked
								? 'border-indigo-500 bg-indigo-600 text-white'
								: 'border-gray-600 bg-gray-900'}"
						>
							{#if isChecked}
								<Check size={10} strokeWidth={3} />
							{/if}
						</div>
						<span class="truncate">{opt.label}</span>
					</div>

					{#if opt.count !== undefined}
						<span class="text-[10px] text-gray-500 font-mono">({opt.count})</span>
					{/if}
				</button>
			{/each}
		{/if}
	</div>
</div>
