<script lang="ts">
	import { SlidersHorizontal } from 'lucide-svelte';

	interface Props {
		isOpen?: boolean;
		activeCount?: number;
		label?: string;
		size?: 'sm' | 'md';
		onclick: () => void;
		class?: string;
	}

	let {
		isOpen = false,
		activeCount = 0,
		label = 'Filtros',
		size = 'sm',
		onclick,
		class: className = ''
	}: Props = $props();
</script>

<button
	type="button"
	{onclick}
	class="inline-flex items-center gap-2 rounded-xl border font-semibold transition-all {size === 'sm'
		? 'px-3 py-1.5 text-xs'
		: 'px-4 py-2 text-sm'} {activeCount > 0 || isOpen
		? 'border-indigo-500/50 bg-indigo-600/15 text-indigo-300 shadow-sm shadow-indigo-500/10'
		: 'border-[#2D3748] bg-[#111827] text-gray-300 hover:border-gray-600 hover:bg-gray-800 hover:text-white'} {className}"
	title="Abrir panel de filtros"
>
	<SlidersHorizontal size={size === 'sm' ? 14 : 16} class={activeCount > 0 ? 'text-indigo-400' : 'text-gray-400'} />
	<span>{label}</span>

	{#if activeCount > 0}
		<span class="flex h-4 min-w-[16px] items-center justify-center rounded-full bg-indigo-500 px-1 text-[10px] font-bold text-white font-mono">
			{activeCount}
		</span>
	{/if}
</button>
