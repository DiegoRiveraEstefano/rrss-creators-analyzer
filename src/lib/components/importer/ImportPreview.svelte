<script lang="ts">
	import type { ParseResult } from '$lib/utils/csvValidator';
	import { formatCurrency, formatNumber } from '$lib/utils/formatters';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { CheckCircle2, AlertTriangle, ArrowLeft, Upload } from 'lucide-svelte';

	interface Props {
		parseResult: ParseResult;
		onCommit: () => void;
		onCancel: () => void;
		isUploading?: boolean;
	}

	let { parseResult, onCommit, onCancel, isUploading = false }: Props = $props();

	let validCount = $derived(parseResult.validRows.length);
	let invalidCount = $derived(parseResult.invalidRows.length);
	let allRows = $derived([...parseResult.validRows, ...parseResult.invalidRows]);
</script>

<div class="space-y-5">
	<!-- Resumen de Validación -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
		<div class="rounded-xl bg-[#111827] border border-[#1F2937] p-4 flex items-center justify-between">
			<div class="space-y-0.5">
				<span class="text-xs text-gray-400 font-medium">Archivo Analizado</span>
				<div class="text-sm font-semibold text-white truncate max-w-[180px]">
					{parseResult.filename}
				</div>
			</div>
			<Badge variant="indigo" size="sm">
				{parseResult.totalRows} filas
			</Badge>
		</div>

		<div class="rounded-xl bg-[#111827] border border-[#1F2937] p-4 flex items-center justify-between">
			<div class="space-y-0.5">
				<span class="text-xs text-gray-400 font-medium">Filas Válidas</span>
				<div class="text-sm font-bold text-emerald-400 font-mono">
					{validCount} / {parseResult.totalRows}
				</div>
			</div>
			<div class="h-8 w-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
				<CheckCircle2 size={18} />
			</div>
		</div>

		<div class="rounded-xl bg-[#111827] border border-[#1F2937] p-4 flex items-center justify-between">
			<div class="space-y-0.5">
				<span class="text-xs text-gray-400 font-medium">Errores / Advertencias</span>
				<div class="text-sm font-bold text-amber-400 font-mono">
					{invalidCount} detectados
				</div>
			</div>
			<div class="h-8 w-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
				<AlertTriangle size={18} />
			</div>
		</div>
	</div>

	<!-- Tabla de Vista Previa de Datos Normalizados -->
	<div class="overflow-hidden rounded-xl border border-[#1F2937] bg-[#111827] shadow-xl">
		<div class="px-5 py-3 border-b border-[#1F2937] flex items-center justify-between bg-[#161F30]">
			<h4 class="text-xs font-semibold uppercase tracking-wider text-gray-300">
				Previsualización de Métricas Normalizadas
			</h4>
			<span class="text-xs text-gray-400 font-mono">
				Mostrando {allRows.slice(0, 10).length} de {allRows.length} registros
			</span>
		</div>

		<div class="overflow-x-auto max-h-[380px]">
			<table class="w-full text-left border-collapse text-xs">
				<thead class="sticky top-0 z-10 bg-[#161F30]/95 backdrop-blur-md border-b border-[#2D3748] text-gray-300 font-semibold">
					<tr>
						<th class="px-4 py-2.5">Estado</th>
						<th class="px-4 py-2.5">Título de Sesión</th>
						<th class="px-4 py-2.5">Juego / Categoría</th>
						<th class="px-4 py-2.5">Plataforma</th>
						<th class="px-4 py-2.5 text-right">Duración</th>
						<th class="px-4 py-2.5 text-right">Media CCV</th>
						<th class="px-4 py-2.5 text-right">Pico Viewers</th>
						<th class="px-4 py-2.5 text-right">Total Ingresos</th>
						<th class="px-4 py-2.5 text-right">$/Hora</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-[#1F2937] text-gray-300">
					{#each allRows.slice(0, 10) as row}
						<tr class="hover:bg-[#1E293B]/60 transition-colors">
							<td class="px-4 py-2.5 whitespace-nowrap">
								{#if row.status === 'valid'}
									<Badge variant="success" size="sm">Válido</Badge>
								{:else if row.status === 'warning'}
									<Badge variant="warning" size="sm">Advertencia</Badge>
								{:else}
									<Badge variant="danger" size="sm">Error</Badge>
								{/if}
							</td>
							<td class="px-4 py-2.5 font-medium text-white max-w-[200px] truncate">
								{row.session_title}
							</td>
							<td class="px-4 py-2.5 text-gray-300">
								{row.game_or_category}
							</td>
							<td class="px-4 py-2.5 capitalize">
								<Badge variant={row.platform === 'twitch' ? 'purple' : row.platform === 'youtube' ? 'danger' : 'cyan'} size="sm">
									{row.platform}
								</Badge>
							</td>
							<td class="px-4 py-2.5 text-right font-mono text-gray-200">
								{row.hours_streamed}h
							</td>
							<td class="px-4 py-2.5 text-right font-mono text-cyan-400 font-semibold">
								{formatNumber(row.avg_ccv)}
							</td>
							<td class="px-4 py-2.5 text-right font-mono text-gray-200">
								{formatNumber(row.peak_viewers)}
							</td>
							<td class="px-4 py-2.5 text-right font-mono text-emerald-400 font-semibold">
								{formatCurrency(row.total_earnings)}
							</td>
							<td class="px-4 py-2.5 text-right font-mono text-gray-200">
								{formatCurrency(row.earnings_per_hour)}/h
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>

	<!-- Botones de Acción -->
	<div class="flex items-center justify-between pt-2">
		<Button variant="ghost" size="sm" onclick={onCancel} disabled={isUploading}>
			<ArrowLeft size={15} />
			Cargar otro archivo
		</Button>

		<div class="flex items-center gap-3">
			<Button
				variant="primary"
				size="md"
				isLoading={isUploading}
				disabled={validCount === 0}
				onclick={onCommit}
			>
				<Upload size={16} />
				Cargar {validCount} sesiones en Supabase
			</Button>
		</div>
	</div>
</div>
