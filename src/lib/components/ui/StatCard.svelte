<script lang="ts">
	import { TrendingUp, TrendingDown, Minus } from 'lucide-svelte';

	interface Props {
		title: string;
		value: string | number;
		changePct?: number;
		changeLabel?: string;
		icon?: any;
		iconColor?: 'indigo' | 'cyan' | 'emerald' | 'amber' | 'rose' | 'purple';
		subtitle?: string;
		class?: string;
	}

	let {
		title,
		value,
		changePct,
		changeLabel = 'vs. periodo anterior',
		icon: IconComponent,
		iconColor = 'indigo',
		subtitle,
		class: className = ''
	}: Props = $props();

	const iconColorMap = {
		indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
		cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
		emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
		amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
		rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
		purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20'
	};
</script>

<div
	class="relative overflow-hidden rounded-xl bg-[#111827] border border-[#1F2937] p-5 shadow-lg transition-all duration-200 hover:border-indigo-500/40 hover:shadow-indigo-500/5 {className}"
>
	<!-- Glow accent sutil en el fondo -->
	<div class="absolute -right-6 -top-6 h-24 w-24 rounded-full bg-indigo-500/5 blur-xl pointer-events-none"></div>

	<div class="flex items-start justify-between">
		<div class="space-y-1">
			<span class="text-xs font-semibold uppercase tracking-wider text-gray-400">{title}</span>
			<div class="text-2xl font-bold tracking-tight text-white font-mono">
				{value}
			</div>
		</div>

		{#if IconComponent}
			<div class="flex h-10 w-10 items-center justify-center rounded-lg border {iconColorMap[iconColor]}">
				<IconComponent size={20} />
			</div>
		{/if}
	</div>

	{#if changePct !== undefined || subtitle}
		<div class="mt-4 flex items-center gap-2 pt-2 border-t border-[#1F2937]/60 text-xs">
			{#if changePct !== undefined}
				{@const isPositive = changePct > 0}
				{@const isNeutral = changePct === 0}
				<span
					class="inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 font-mono font-medium {isPositive
						? 'bg-emerald-500/10 text-emerald-400'
						: isNeutral
							? 'bg-gray-800 text-gray-400'
							: 'bg-rose-500/10 text-rose-400'}"
				>
					{#if isPositive}
						<TrendingUp size={12} class="stroke-[2.5]" />
						+{changePct.toFixed(1)}%
					{:else if isNeutral}
						<Minus size={12} class="stroke-[2.5]" />
						0.0%
					{:else}
						<TrendingDown size={12} class="stroke-[2.5]" />
						{changePct.toFixed(1)}%
					{/if}
				</span>
				<span class="text-gray-400 text-[11px] truncate">{changeLabel}</span>
			{:else if subtitle}
				<span class="text-gray-400 text-xs">{subtitle}</span>
			{/if}
		</div>
	{/if}
</div>
