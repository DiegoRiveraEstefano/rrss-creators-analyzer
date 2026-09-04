<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLButtonAttributes } from 'svelte/elements';

	interface Props extends HTMLButtonAttributes {
		variant?: 'primary' | 'secondary' | 'ghost' | 'outline' | 'danger' | 'cyan';
		size?: 'sm' | 'md' | 'lg';
		isLoading?: boolean;
		children?: Snippet;
	}

	let {
		variant = 'primary',
		size = 'md',
		isLoading = false,
		disabled = false,
		class: className = '',
		children,
		type = 'button',
		...rest
	}: Props = $props();

	const variantStyles = {
		primary: 'bg-[#6366F1] hover:bg-[#4F46E5] active:bg-[#4338CA] text-white shadow-lg shadow-indigo-500/20 border border-indigo-500/30',
		secondary: 'bg-[#1F2937] hover:bg-[#374151] active:bg-[#111827] text-[#F9FAFB] border border-[#374151]',
		outline: 'bg-transparent hover:bg-white/5 active:bg-white/10 text-[#F9FAFB] border border-[#2D3748]',
		ghost: 'bg-transparent hover:bg-white/5 active:bg-white/10 text-[#9CA3AF] hover:text-white border-transparent',
		danger: 'bg-[#EF4444] hover:bg-[#DC2626] active:bg-[#B91C1C] text-white shadow-lg shadow-rose-500/20 border border-rose-500/30',
		cyan: 'bg-[#06B6D4] hover:bg-[#0891B2] active:bg-[#0E7490] text-white shadow-lg shadow-cyan-500/20 border border-cyan-500/30'
	};

	const sizeStyles = {
		sm: 'text-xs px-2.5 py-1.5 rounded-md gap-1.5 font-medium',
		md: 'text-sm px-3.5 py-2 rounded-lg gap-2 font-medium',
		lg: 'text-base px-5 py-2.5 rounded-lg gap-2.5 font-semibold'
	};
</script>

<button
	{type}
	disabled={disabled || isLoading}
	class="inline-flex items-center justify-center transition-all duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed select-none {variantStyles[variant]} {sizeStyles[size]} {className}"
	{...rest}
>
	{#if isLoading}
		<svg
			class="animate-spin -ml-0.5 mr-2 h-4 w-4 text-current"
			xmlns="http://www.w3.org/2000/svg"
			fill="none"
			viewBox="0 0 24 24"
		>
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
			<path
				class="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
			></path>
		</svg>
	{/if}
	{#if children}
		{@render children()}
	{/if}
</button>
