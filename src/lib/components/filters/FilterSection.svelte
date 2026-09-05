<script lang="ts">
	import type { Snippet } from 'svelte';
	import { ChevronDown } from 'lucide-svelte';

	interface Props {
		title: string;
		isCollapsible?: boolean;
		defaultOpen?: boolean;
		badgeText?: string | null;
		children?: Snippet;
	}

	let {
		title,
		isCollapsible = true,
		defaultOpen = true,
		badgeText = null,
		children
	}: Props = $props();

	let isOpen = $state(defaultOpen);
</script>

<div class="border-b border-[#1F2937] py-3.5 last:border-b-0">
	<button
		type="button"
		onclick={() => isCollapsible && (isOpen = !isOpen)}
		class="flex w-full items-center justify-between text-left text-xs font-semibold text-gray-200 hover:text-white transition-colors select-none"
	>
		<div class="flex items-center gap-2">
			<span>{title}</span>
			{#if badgeText}
				<span class="rounded bg-indigo-500/20 px-1.5 py-0.2 text-[10px] font-mono font-medium text-indigo-300">
					{badgeText}
				</span>
			{/if}
		</div>

		{#if isCollapsible}
			<ChevronDown
				size={14}
				class="text-gray-400 transition-transform duration-200 {isOpen ? 'rotate-180' : ''}"
			/>
		{/if}
	</button>

	{#if isOpen}
		<div class="mt-3 space-y-2.5 animate-in fade-in duration-150">
			{#if children}
				{@render children()}
			{/if}
		</div>
	{/if}
</div>
