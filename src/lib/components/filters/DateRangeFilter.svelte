<script lang="ts">
	import type { DateRangeFilterValue, DateRangePreset } from '$lib/types/filters';

	interface Props {
		value?: DateRangeFilterValue;
		onchange?: (val: DateRangeFilterValue) => void;
	}

	let {
		value = $bindable({ preset: 'all' }),
		onchange
	}: Props = $props();

	const presets: { id: DateRangePreset; label: string }[] = [
		{ id: '7d', label: '7 días' },
		{ id: '30d', label: '30 días' },
		{ id: '90d', label: '90 días' },
		{ id: 'year', label: 'Este año' },
		{ id: 'all', label: 'Todo' },
		{ id: 'custom', label: 'Personalizado' }
	];

	function selectPreset(preset: DateRangePreset) {
		const now = new Date();
		let from: string | undefined;
		let to: string | undefined = now.toISOString().split('T')[0];

		if (preset === '7d') {
			const d = new Date();
			d.setDate(d.getDate() - 7);
			from = d.toISOString().split('T')[0];
		} else if (preset === '30d') {
			const d = new Date();
			d.setDate(d.getDate() - 30);
			from = d.toISOString().split('T')[0];
		} else if (preset === '90d') {
			const d = new Date();
			d.setDate(d.getDate() - 90);
			from = d.toISOString().split('T')[0];
		} else if (preset === 'year') {
			from = `${now.getFullYear()}-01-01`;
		} else if (preset === 'all') {
			from = undefined;
			to = undefined;
		}

		value = {
			preset,
			from: preset === 'custom' ? value.from : from,
			to: preset === 'custom' ? value.to : to
		};
		onchange?.(value);
	}

	function handleCustomDateChange(field: 'from' | 'to', val: string) {
		value = {
			preset: 'custom',
			from: field === 'from' ? val : value.from,
			to: field === 'to' ? val : value.to
		};
		onchange?.(value);
	}
</script>

<div class="space-y-2.5">
	<div class="grid grid-cols-3 gap-1.5">
		{#each presets as p}
			<button
				type="button"
				onclick={() => selectPreset(p.id)}
				class="rounded-lg border px-2 py-1.5 text-center text-xs font-medium transition-colors {value.preset === p.id
					? 'border-indigo-500 bg-indigo-600/20 text-indigo-300 font-semibold'
					: 'border-[#2D3748] bg-[#111827] text-gray-400 hover:border-gray-600 hover:text-gray-200'}"
			>
				{p.label}
			</button>
		{/each}
	</div>

	{#if value.preset === 'custom'}
		<div class="grid grid-cols-2 gap-2 pt-1">
			<div>
				<label class="block text-[11px] text-gray-400 mb-1">Desde:</label>
				<input
					type="date"
					value={value.from || ''}
					onchange={(e) => handleCustomDateChange('from', (e.target as HTMLInputElement).value)}
					class="w-full rounded-lg bg-[#111827] border border-[#2D3748] px-2.5 py-1 text-xs text-white focus:border-indigo-500 focus:outline-none"
				/>
			</div>
			<div>
				<label class="block text-[11px] text-gray-400 mb-1">Hasta:</label>
				<input
					type="date"
					value={value.to || ''}
					onchange={(e) => handleCustomDateChange('to', (e.target as HTMLInputElement).value)}
					class="w-full rounded-lg bg-[#111827] border border-[#2D3748] px-2.5 py-1 text-xs text-white focus:border-indigo-500 focus:outline-none"
				/>
			</div>
		</div>
	{/if}
</div>
