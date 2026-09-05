<script lang="ts">
	import { createQuery } from '@tanstack/svelte-query';
	import { sessionsQueryOptions } from '$lib/query/sessions';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import type { StreamingSession } from '$lib/services/analyticsService';
	import { formatCurrency, formatNumber } from '$lib/utils/formatters';
	import StatCard from '$lib/components/ui/StatCard.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import EChart from '$lib/components/charts/EChart.svelte';
	import type { EChartsOption } from 'echarts';
	import {
		LineChart,
		BarChart3,
		PieChart,
		TrendingUp,
		Layers,
		Flame
	} from 'lucide-svelte';

	const sessionsQuery = createQuery(() =>
		sessionsQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);

	let sessions = $derived(sessionsQuery.data || []);
	let isLoading = $derived(sessionsQuery.isLoading);

	// Gráfico de Correlación: Horas vs Ingresos
	let correlationChartOptions = $derived.by<EChartsOption>(() => {
		const data = sessions.map((s) => [
			Number(s.hours_streamed || (s.duration_seconds / 3600).toFixed(1)),
			s.total_earnings,
			s.avg_ccv,
			s.session_title
		]);

		return {
			tooltip: {
				formatter: (param: any) => {
					return `<div class="text-xs">
						<b>${param.value[3]}</b><br/>
						Horas: ${param.value[0]}h<br/>
						Ingresos: $${param.value[1]}<br/>
						Media CCV: ${param.value[2]}
					</div>`;
				},
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			grid: { left: '3%', right: '3%', bottom: '8%', top: '12%', containLabel: true },
			xAxis: {
				name: 'Horas Emitidas',
				type: 'value',
				nameTextStyle: { color: '#9CA3AF', fontSize: 11 },
				axisLine: { lineStyle: { color: '#2D3748' } },
				splitLine: { lineStyle: { color: '#1F2937' } },
				axisLabel: { color: '#9CA3AF' }
			},
			yAxis: {
				name: 'Ingresos ($ USD)',
				type: 'value',
				nameTextStyle: { color: '#9CA3AF', fontSize: 11 },
				splitLine: { lineStyle: { color: '#1F2937' } },
				axisLabel: { color: '#9CA3AF', formatter: '${value}' }
			},
			series: [
				{
					type: 'scatter',
					data,
					symbolSize: (val: any) => Math.max(12, Math.min(36, (val[2] / 5000) * 8)),
					itemStyle: {
						color: '#6366F1',
						borderColor: '#818CF8',
						borderWidth: 2,
						opacity: 0.85
					}
				}
			]
		};
	});

	// Gráfico de Pastel: Distribución de Ingresos por Fuente (Ads vs Subs vs Donaciones)
	let sourceBreakdownOptions = $derived.by<EChartsOption>(() => {
		const totalAds = sessions.reduce((acc, s) => acc + Number(s.ad_revenue || 0), 0);
		const totalSubs = sessions.reduce((acc, s) => acc + Number(s.subs_revenue || 0), 0);
		const totalDonations = sessions.reduce((acc, s) => acc + Number(s.donations_revenue || 0), 0);

		return {
			tooltip: {
				trigger: 'item',
				formatter: '{b}: ${c} ({d}%)',
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			legend: {
				orient: 'horizontal',
				bottom: 0,
				textStyle: { color: '#9CA3AF', fontSize: 11 }
			},
			series: [
				{
					name: 'Fuente de Ingresos',
					type: 'pie',
					radius: ['45%', '70%'],
					avoidLabelOverlap: false,
					itemStyle: {
						borderRadius: 6,
						borderColor: '#111827',
						borderWidth: 3
					},
					label: { show: false },
					data: [
						{ value: totalSubs, name: 'Suscripciones', itemStyle: { color: '#6366F1' } },
						{ value: totalAds, name: 'Publicidad (Ads)', itemStyle: { color: '#06B6D4' } },
						{ value: totalDonations, name: 'Donaciones / Bits', itemStyle: { color: '#10B981' } }
					]
				}
			]
		};
	});
</script>

<div class="space-y-6">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<LineChart class="text-indigo-400" size={24} />
				<span>Analítica Detallada y Rendimiento</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				Correlaciones avanzadas entre duración, retención de espectadores y flujos de monetización.
			</p>
		</div>

		{#if tenantStore.selectedCreator}
			<Badge variant="cyan" size="md">
				Filtrado: @{tenantStore.selectedCreator.handle}
			</Badge>
		{/if}
	</div>

	<!-- Gráficos Analíticos -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Gráfico de Dispersión / Correlación (2 columnas) -->
		<div class="lg:col-span-2 rounded-xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Eficiencia: Horas vs. Ingresos Totales</h3>
					<p class="text-[11px] text-gray-400">El tamaño del punto representa la concurrencia media (CCV)</p>
				</div>
				<Badge variant="indigo" size="sm">Correlación</Badge>
			</div>
			<EChart options={correlationChartOptions} height="320px" />
		</div>

		<!-- Gráfico de Desglose de Fuentes de Monetización -->
		<div class="rounded-xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Desglose de Ingresos</h3>
					<p class="text-[11px] text-gray-400">Suscripciones vs. Publicidad vs. Donaciones</p>
				</div>
				<Badge variant="success" size="sm">Mix de Monetización</Badge>
			</div>
			<EChart options={sourceBreakdownOptions} height="320px" />
		</div>
	</div>
</div>
