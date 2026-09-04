<script lang="ts">
	import type { HTMLSelectAttributes } from 'svelte/elements';

	export interface OptionItem {
		value: string;
		label: string;
	}

	interface Props extends HTMLSelectAttributes {
		label?: string;
		options: OptionItem[];
		error?: string;
		class?: string;
	}

	let {
		label,
		options,
		error,
		value = $bindable(''),
		class: className = '',
		id = `select-${Math.random().toString(36).substring(2, 8)}`,
		...rest
	}: Props = $props();
</script>

<div class="space-y-1.5 w-full">
	{#if label}
		<label for={id} class="block text-xs font-semibold text-gray-300">
			{label}
		</label>
	{/if}

	<div class="relative">
		<select
			{id}
			bind:value
			class="w-full appearance-none rounded-lg bg-[#111827] border {error
				? 'border-rose-500 focus:border-rose-500 focus:ring-rose-500'
				: 'border-[#2D3748] focus:border-indigo-500 focus:ring-indigo-500'} px-3.5 py-2 pr-9 text-xs text-white focus:outline-none focus:ring-1 transition-colors cursor-pointer {className}"
			{...rest}
		>
			{#each options as opt}
				<option value={opt.value} class="bg-[#111827] text-white">
					{opt.label}
				</option>
			{/each}
		</select>
		<div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-gray-400">
			<svg class="h-4 w-4 fill-current" viewBox="0 0 20 20">
				<path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
			</svg>
		</div>
	</div>

	{#if error}
		<p class="text-[11px] text-rose-400">{error}</p>
	{/if}
</div>
