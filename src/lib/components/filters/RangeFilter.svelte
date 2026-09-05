<script lang="ts">
	interface Props {
		label: string;
		min?: number | null;
		max?: number | null;
		unit?: string;
		step?: number;
		placeholderMin?: string;
		placeholderMax?: string;
		onchange?: (range: { min?: number | null; max?: number | null }) => void;
	}

	let {
		label,
		min = $bindable(null),
		max = $bindable(null),
		unit = '',
		step = 1,
		placeholderMin = 'Mín',
		placeholderMax = 'Máx',
		onchange
	}: Props = $props();

	function handleMinChange(val: string) {
		const num = val === '' ? null : Number(val);
		min = num;
		onchange?.({ min: num, max });
	}

	function handleMaxChange(val: string) {
		const num = val === '' ? null : Number(val);
		max = num;
		onchange?.({ min, max: num });
	}
</script>

<div class="space-y-1.5">
	<div class="flex items-center justify-between text-xs text-gray-300 font-medium">
		<span>{label}</span>
		{#if unit}
			<span class="text-[10px] text-gray-500 font-mono">({unit})</span>
		{/if}
	</div>

	<div class="grid grid-cols-2 gap-2">
		<input
			type="number"
			{step}
			value={min ?? ''}
			placeholder={placeholderMin}
			oninput={(e) => handleMinChange((e.target as HTMLInputElement).value)}
			class="w-full rounded-lg bg-[#111827] border border-[#2D3748] px-2.5 py-1.5 text-xs text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none"
		/>
		<input
			type="number"
			{step}
			value={max ?? ''}
			placeholder={placeholderMax}
			oninput={(e) => handleMaxChange((e.target as HTMLInputElement).value)}
			class="w-full rounded-lg bg-[#111827] border border-[#2D3748] px-2.5 py-1.5 text-xs text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none"
		/>
	</div>
</div>
