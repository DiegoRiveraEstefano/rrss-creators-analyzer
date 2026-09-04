<script lang="ts">
	import { onMount } from 'svelte';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import { analyticsService, type AnalyticsSummary, type StreamingSession } from '$lib/services/analyticsService';
	import { formatCurrency, formatNumber, formatDuration, formatDate } from '$lib/utils/formatters';
	import StatCard from '$lib/components/ui/StatCard.svelte';
	import DataTable from '$lib/components/ui/DataTable.svelte';
	import type { Column } from '$lib/types/ui';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import EChart from '$lib/components/charts/EChart.svelte';
	import type { EChartsOption } from 'echarts';
	import {
		DollarSign,
		Clock,
		Users,
		Zap,
		TrendingUp,
		FileSpreadsheet,
		Plus
	} from 'lucide-svelte';

	let summary = $state<AnalyticsSummary>({
		totalEarnings: 0,
		earningsChangePct: 0,
		totalHours: 0,
		hoursChangePct: 0,
		avgCcv: 0,
		ccvChangePct: 0,
		peakViewers: 0,
		totalSessions: 0,
		activeAlertsCount: 0,
		earningsPerHour: 0
	});

	let sessions = $state<StreamingSession[]>([]);
	let isLoadingData = $state(true);

	async function loadDashboardData() {
		if (!tenantStore.currentOrg) return;
		isLoadingData = true;
		try {
			const orgId = tenantStore.currentOrg.id;
			const creatorId = tenantStore.selectedCreatorId;

			const [sum, sess] = await Promise.all([
				analyticsService.getSummary(orgId, creatorId),
				analyticsService.getSessions(orgId, creatorId)
			]);

			summary = sum;
			sessions = sess;
		} catch (error) {
			console.error('Error loading dashboard data:', error);
		} finally {
			isLoadingData = false;
		}
	}

	$effect(() => {
		if (tenantStore.currentOrg) {
			// Trigger when tenant or selected creator changes
			const _ = tenantStore.selectedCreatorId;
			loadDashboardData();
		}
	});

	// Opciones del gráfico de Concurrencia (ECharts)
	let audienceChartOptions = $derived.by<EChartsOption>(() => {
		const sorted = [...sessions].sort(
			(a, b) => new Date(a.streamed_at).getTime() - new Date(b.streamed_at).getTime()
		);
		const dates = sorted.map((s) => {
			const d = new Date(s.streamed_at);
			return `${d.getDate()}/${d.getMonth() + 1}`;
		});
		const ccvValues = sorted.map((s) => s.avg_ccv);
		const peakValues = sorted.map((s) => s.peak_viewers);

		return {
			tooltip: {
				trigger: 'axis',
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB', fontSize: 12 }
			},
			legend: {
				data: ['Media CCV', 'Pico Viewers'],
				textStyle: { color: '#9CA3AF' },
				top: 0,
				right: 0
			},
			grid: { left: '3%', right: '3%', bottom: '8%', top: '15%', containLabel: true },
			xAxis: {
				type: 'category',
				data: dates,
				axisLine: { lineStyle: { color: '#2D3748' } },
				axisLabel: { color: '#9CA3AF', fontSize: 11 }
			},
			yAxis: {
				type: 'value',
				splitLine: { lineStyle: { color: '#1F2937' } },
				axisLabel: { color: '#9CA3AF', fontSize: 11 }
			},
			series: [
				{
					name: 'Media CCV',
					type: 'line',
					smooth: true,
					data: ccvValues,
					itemStyle: { color: '#06B6D4' },
					areaStyle: {
						color: {
							type: 'linear',
							x: 0,
							y: 0,
							x2: 0,
							y2: 1,
							colorStops: [
								{ offset: 0, color: 'rgba(6, 182, 212, 0.35)' },
								{ offset: 1, color: 'rgba(6, 182, 212, 0.0)' }
							]
						}
					}
				},
				{
					name: 'Pico Viewers',
					type: 'line',
					smooth: true,
					data: peakValues,
					itemStyle: { color: '#6366F1' },
					lineStyle: { type: 'dashed', width: 2 }
				}
			]
		};
	});

	// Opciones del gráfico de Ingresos por Sesión
	let revenueChartOptions = $derived.by<EChartsOption>(() => {
		const sorted = [...sessions].sort(
			(a, b) => new Date(a.streamed_at).getTime() - new Date(b.streamed_at).getTime()
		);
		const titles = sorted.map((s) => s.game_or_category || 'General');
		const earnings = sorted.map((s) => s.total_earnings);

		return {
			tooltip: {
				trigger: 'axis',
				formatter: (params: any) => {
					const item = Array.isArray(params) ? params[0] : params;
					return `<div class="text-xs"><b>${item.name}</b><br/>Ingresos: $${item.value}</div>`;
				},
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB', fontSize: 12 }
			},
			grid: { left: '3%', right: '3%', bottom: '8%', top: '15%', containLabel: true },
			xAxis: {
				type: 'category',
				data: titles,
				axisLine: { lineStyle: { color: '#2D3748' } },
				axisLabel: {
					color: '#9CA3AF',
					fontSize: 10,
					interval: 0,
					rotate: 20
				}
			},
			yAxis: {
				type: 'value',
				splitLine: { lineStyle: { color: '#1F2937' } },
				axisLabel: {
					color: '#9CA3AF',
					fontSize: 11,
					formatter: '${value}'
				}
			},
			series: [
				{
					name: 'Ingresos',
					type: 'bar',
					data: earnings,
					itemStyle: {
						color: {
							type: 'linear',
							x: 0,
							y: 0,
							x2: 0,
							y2: 1,
							colorStops: [
								{ offset: 0, color: '#10B981' },
								{ offset: 1, color: '#059669' }
							]
						},
						borderRadius: [4, 4, 0, 0]
					}
				}
			]
		};
	});

	// Definición de columnas de la tabla de sesiones
	const tableColumns: Column<StreamingSession>[] = [
		{
			key: 'session_title',
			label: 'Transmisión / Título',
			sortable: true
		},
		{
			key: 'game_or_category',
			label: 'Categoría',
			sortable: true
		},
		{
			key: 'platform',
			label: 'Plataforma',
			align: 'center',
			sortable: true
		},
		{
			key: 'hours_streamed',
			label: 'Duración',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'avg_ccv',
			label: 'Media CCV',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'peak_viewers',
			label: 'Pico Viewers',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'total_earnings',
			label: 'Ingresos Totales',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'earnings_per_hour',
			label: '$/Hora',
			align: 'right',
			isMono: true,
			sortable: true
		}
	];
</script>

<!-- Header & Quick Actions -->
<div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
	<div>
		<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
			<span>Resumen Ejecutivo</span>
			{#if tenantStore.selectedCreator}
				<Badge variant="cyan" size="md">
					@{tenantStore.selectedCreator.handle}
				</Badge>
			{:else}
				<Badge variant="indigo" size="md">
					Roster Completo
				</Badge>
			{/if}
		</h1>
		<p class="text-xs text-gray-400 mt-1">
			Métricas de monetización, concurrencia de streaming y rendimiento de contenido en tiempo real.
		</p>
	</div>

	<div class="flex items-center gap-3">
		<a href="/import">
			<Button variant="primary" size="sm">
				<FileSpreadsheet size={15} />
				Importar CSV / Excel
			</Button>
		</a>
		<a href="/roster">
			<Button variant="secondary" size="sm">
				<Plus size={15} />
				Ver Roster
			</Button>
		</a>
	</div>
</div>

<!-- Row de KPI Stat Cards -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
	<StatCard
		title="Ingresos Totales"
		value={formatCurrency(summary.totalEarnings)}
		changePct={summary.earningsChangePct}
		icon={DollarSign}
		iconColor="emerald"
	/>

	<StatCard
		title="Horas Transmitidas"
		value={`${summary.totalHours}h`}
		changePct={summary.hoursChangePct}
		icon={Clock}
		iconColor="indigo"
	/>

	<StatCard
		title="Media CCV"
		value={formatNumber(summary.avgCcv)}
		changePct={summary.ccvChangePct}
		icon={Users}
		iconColor="cyan"
	/>

	<StatCard
		title="Pico Máximo Viewers"
		value={formatNumber(summary.peakViewers)}
		icon={Zap}
		iconColor="purple"
		subtitle="Máximo alcanzado en el periodo"
	/>

	<StatCard
		title="Rendimiento $/Hora"
		value={`${formatCurrency(summary.earningsPerHour)}/h`}
		changePct={11.2}
		icon={TrendingUp}
		iconColor="amber"
	/>
</div>

<!-- Gráficos de Visualización de BI -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
	<!-- Gráfico 1: Concurrencia de Audiencia -->
	<div class="rounded-xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
		<div class="flex items-center justify-between mb-4">
			<div>
				<h3 class="text-sm font-semibold text-white">Evolución de Concurrencia (CCV)</h3>
				<p class="text-[11px] text-gray-400">Media de espectadores en vivo vs. Picos por sesión</p>
			</div>
			<Badge variant="cyan" size="sm">En Vivo</Badge>
		</div>
		<EChart options={audienceChartOptions} height="280px" />
	</div>

	<!-- Gráfico 2: Monetización por Contenido -->
	<div class="rounded-xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
		<div class="flex items-center justify-between mb-4">
			<div>
				<h3 class="text-sm font-semibold text-white">Ingresos por Categoría / Transmisión</h3>
				<p class="text-[11px] text-gray-400">Distribución de monetización total generada ($ USD)</p>
			</div>
			<Badge variant="success" size="sm">Monetización</Badge>
		</div>
		<EChart options={revenueChartOptions} height="280px" />
	</div>
</div>

<!-- Tabla Dinámica de Sesiones Recientes -->
<div class="space-y-3">
	<div class="flex items-center justify-between">
		<div>
			<h3 class="text-base font-semibold text-white">Sesiones de Streaming Recientes</h3>
			<p class="text-xs text-gray-400">Historial normalizado de emisiones, retención e ingresos</p>
		</div>
	</div>

	<DataTable
		data={sessions}
		columns={tableColumns}
		searchPlaceholder="Buscar por título, categoría o plataforma..."
		searchKeys={['session_title', 'game_or_category', 'platform']}
	/>
</div>
