<script lang="ts">
	import type { HTMLInputAttributes } from 'svelte/elements';

	interface Props extends HTMLInputAttributes {
		label?: string;
		error?: string;
		hint?: string;
		class?: string;
	}

	let {
		label,
		error,
		hint,
		value = $bindable(''),
		class: className = '',
		id = `input-${Math.random().toString(36).substring(2, 8)}`,
		...rest
	}: Props = $props();
</script>

<div class="space-y-1.5 w-full">
	{#if label}
		<label for={id} class="block text-xs font-semibold text-gray-300">
			{label}
		</label>
	{/if}

	<input
		{id}
		bind:value
		class="w-full rounded-lg bg-[#111827] border {error
			? 'border-rose-500 focus:border-rose-500 focus:ring-rose-500'
			: 'border-[#2D3748] focus:border-indigo-500 focus:ring-indigo-500'} px-3.5 py-2 text-xs text-white placeholder-gray-400 focus:outline-none focus:ring-1 transition-colors {className}"
		{...rest}
	/>

	{#if error}
		<p class="text-[11px] text-rose-400">{error}</p>
	{:else if hint}
		<p class="text-[11px] text-gray-400">{hint}</p>
	{/if}
</div>
