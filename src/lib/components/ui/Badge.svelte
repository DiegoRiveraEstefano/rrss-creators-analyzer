<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		variant?: 'success' | 'warning' | 'danger' | 'info' | 'indigo' | 'cyan' | 'purple' | 'neutral';
		size?: 'sm' | 'md';
		dot?: boolean;
		pulse?: boolean;
		class?: string;
		children?: Snippet;
	}

	let {
		variant = 'neutral',
		size = 'md',
		dot = false,
		pulse = false,
		class: className = '',
		children
	}: Props = $props();

	const variantStyles = {
		success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
		warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
		danger: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
		info: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
		indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
		cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
		purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
		neutral: 'bg-gray-800 text-gray-300 border-gray-700'
	};

	const dotColors = {
		success: 'bg-emerald-400',
		warning: 'bg-amber-400',
		danger: 'bg-rose-400',
		info: 'bg-sky-400',
		indigo: 'bg-indigo-400',
		cyan: 'bg-cyan-400',
		purple: 'bg-purple-400',
		neutral: 'bg-gray-400'
	};

	const sizeStyles = {
		sm: 'text-[11px] px-2 py-0.5 rounded gap-1 font-medium',
		md: 'text-xs px-2.5 py-1 rounded-md gap-1.5 font-medium'
	};
</script>

<span
	class="inline-flex items-center border font-sans tracking-wide select-none {variantStyles[variant]} {sizeStyles[size]} {className}"
>
	{#if dot}
		<span class="relative flex h-1.5 w-1.5">
			{#if pulse}
				<span
					class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 {dotColors[variant]}"
				></span>
			{/if}
			<span class="relative inline-flex rounded-full h-1.5 w-1.5 {dotColors[variant]}"></span>
		</span>
	{/if}
	{#if children}
		{@render children()}
	{/if}
</span>
