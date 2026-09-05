<script lang="ts">
	import { onMount } from 'svelte';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import {
		analyticsService,
		type AnalyticsSummary,
		type StreamingSession
	} from '$lib/services/analyticsService';
	import { formatCurrency, formatNumber, formatDuration } from '$lib/utils/formatters';
	import StatCard from '$lib/components/ui/StatCard.svelte';
	import DataTable from '$lib/components/ui/DataTable.svelte';
	import type { Column } from '$lib/types/ui';
	import Button from '$lib/components/ui/Button.svelte';
	import EChart from '$lib/components/charts/EChart.svelte';
	import type { EChartsOption } from 'echarts';
	import {
		FilterDrawer,
		FilterTriggerButton,
		FilterSection,
		DateRangeFilter,
		PlatformFilter,
		RangeFilter,
		MultiSelectFilter,
		type DashboardFilterState
	} from '$lib/components/filters';
	import type { PlatformType } from '$lib/supabase/database.types';
	import {
		DollarSign,
		Clock,
		Users,
		Zap,
		TrendingUp,
		Plus,
		Radio,
		Layers
	} from 'lucide-svelte';

	import { createQuery } from '@tanstack/svelte-query';
	import { analyticsSummaryQueryOptions } from '$lib/query/analytics';
	import { sessionsQueryOptions } from '$lib/query/sessions';

	const summaryQuery = createQuery(() =>
		analyticsSummaryQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);
	const sessionsQuery = createQuery(() =>
		sessionsQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);

	let rawSessions = $derived(sessionsQuery.data || []);
	let rawSummary = $derived(
		summaryQuery.data || {
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
		}
	);

	let isLoadingData = $derived(summaryQuery.isLoading || sessionsQuery.isLoading);
	let isFilterDrawerOpen = $state(false);

	// Estado de filtros del Dashboard
	let filters = $state<DashboardFilterState>({
		dateRange: { preset: 'all' },
		platforms: ['twitch', 'youtube', 'kick', 'tiktok'],
		minCcv: null,
		minEarnings: null,
		categories: []
	});

	// Categorías disponibles de las sesiones
	let availableCategories = $derived.by(() => {
		const cats = new Map<string, number>();
		for (const s of rawSessions) {
			if (s.game_or_category) {
				cats.set(s.game_or_category, (cats.get(s.game_or_category) || 0) + 1);
			}
		}
		return Array.from(cats.entries()).map(([name, count]) => ({
			value: name,
			label: name,
			count
		}));
	});

	// Conteo de filtros activos
	let activeFiltersCount = $derived.by(() => {
		let count = 0;
		if (filters.dateRange.preset !== 'all') count++;
		if (filters.platforms.length < 4) count++;
		if (filters.minCcv !== null && filters.minCcv !== undefined) count++;
		if (filters.minEarnings !== null && filters.minEarnings !== undefined) count++;
		if (filters.categories.length > 0) count++;
		return count;
	});

	function resetFilters() {
		filters = {
			dateRange: { preset: 'all' },
			platforms: ['twitch', 'youtube', 'kick', 'tiktok'],
			minCcv: null,
			minEarnings: null,
			categories: []
		};
	}

	// Sesiones filtradas reactivamente
	let sessions = $derived.by(() => {
		let list = [...rawSessions];

		// 1. Filtro de Plataformas
		if (filters.platforms.length > 0) {
			list = list.filter((s) => filters.platforms.includes(s.platform));
		}

		// 2. Filtro de Fechas
		if (filters.dateRange.from) {
			const fromTime = new Date(filters.dateRange.from).getTime();
			list = list.filter((s) => new Date(s.streamed_at).getTime() >= fromTime);
		}
		if (filters.dateRange.to) {
			const toTime = new Date(filters.dateRange.to).getTime() + 86400000;
			list = list.filter((s) => new Date(s.streamed_at).getTime() <= toTime);
		}

		// 3. Filtro de CCV mínimo
		if (filters.minCcv !== null && filters.minCcv !== undefined) {
			list = list.filter((s) => s.avg_ccv >= (filters.minCcv || 0));
		}

		// 4. Filtro de Ingresos mínimos
		if (filters.minEarnings !== null && filters.minEarnings !== undefined) {
			list = list.filter((s) => s.total_earnings >= (filters.minEarnings || 0));
		}

		// 5. Filtro de Categorías
		if (filters.categories.length > 0) {
			list = list.filter((s) => s.game_or_category && filters.categories.includes(s.game_or_category));
		}

		return list;
	});

	// Resumen y KPIs recalculados
	let summary = $derived.by<AnalyticsSummary>(() => {
		const totalStreamEarnings = sessions.reduce((acc, s) => acc + Number(s.total_earnings || 0), 0);
		const totalDurationSecs = sessions.reduce((acc, s) => acc + (s.duration_seconds || 0), 0);
		const totalHours = Number((totalDurationSecs / 3600).toFixed(1));
		const avgCcv =
			sessions.length > 0
				? Math.round(sessions.reduce((acc, s) => acc + (s.avg_ccv || 0), 0) / sessions.length)
				: 0;
		const peakViewers = sessions.reduce((acc, s) => Math.max(acc, s.peak_viewers || 0), 0);
		const earningsPerHour =
			totalHours > 0 ? Number((totalStreamEarnings / totalHours).toFixed(2)) : 0;

		return {
			...rawSummary,
			totalEarnings: totalStreamEarnings + (rawSummary.totalVideoEarnings || 0),
			totalHours,
			avgCcv,
			peakViewers,
			totalSessions: sessions.length,
			earningsPerHour
		};
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
				axisLine: { lineStyle: { color: '#2D3748' } },
				splitLine: { lineStyle: { color: '#1F2937' } },
				axisLabel: { color: '#9CA3AF', fontSize: 11 }
			},
			series: [
				{
					name: 'Media CCV',
					type: 'line',
					smooth: true,
					data: ccvValues,
					itemStyle: { color: '#6366F1' },
					areaStyle: {
						color: {
							type: 'linear',
							x: 0,
							y: 0,
							x2: 0,
							y2: 1,
							colorStops: [
								{ offset: 0, color: 'rgba(99, 102, 241, 0.4)' },
								{ offset: 1, color: 'rgba(99, 102, 241, 0.0)' }
							]
						}
					}
				},
				{
					name: 'Pico Viewers',
					type: 'line',
					smooth: true,
					data: peakValues,
					itemStyle: { color: '#06B6D4' }
				}
			]
		};
	});

	// Opciones del gráfico de Ingresos por Día (ECharts)
	let revenueChartOptions = $derived.by<EChartsOption>(() => {
		const sorted = [...sessions].sort(
			(a, b) => new Date(a.streamed_at).getTime() - new Date(b.streamed_at).getTime()
		);
		const dates = sorted.map((s) => {
			const d = new Date(s.streamed_at);
			return `${d.getDate()}/${d.getMonth() + 1}`;
		});
		const earningsValues = sorted.map((s) => s.total_earnings);

		return {
			tooltip: {
				trigger: 'axis',
				formatter: '{b}: ${c}',
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			grid: { left: '3%', right: '3%', bottom: '8%', top: '10%', containLabel: true },
			xAxis: {
				type: 'category',
				data: dates,
				axisLine: { lineStyle: { color: '#2D3748' } },
				axisLabel: { color: '#9CA3AF', fontSize: 11 }
			},
			yAxis: {
				type: 'value',
				axisLine: { lineStyle: { color: '#2D3748' } },
				splitLine: { lineStyle: { color: '#1F2937' } },
				axisLabel: { color: '#9CA3AF', fontSize: 11, formatter: '${value}' }
			},
			series: [
				{
					name: 'Ingresos',
					type: 'bar',
					data: earningsValues,
					itemStyle: {
						color: '#10B981',
						borderRadius: [4, 4, 0, 0]
					}
				}
			]
		};
	});

	// Gráfico 3: Cuota de Horas por Categoría (Pie)
	let categoryShareOptions = $derived.by<EChartsOption>(() => {
		const catMap = new Map<string, number>();
		for (const s of sessions) {
			const cat = s.game_or_category || 'Sin Categoría';
			catMap.set(cat, (catMap.get(cat) || 0) + Number(s.hours_streamed || (s.duration_seconds / 3600).toFixed(1)));
		}

		const pieData = Array.from(catMap.entries())
			.map(([name, value]) => ({ name, value: Number(value.toFixed(1)) }))
			.sort((a, b) => b.value - a.value)
			.slice(0, 6);

		return {
			tooltip: {
				trigger: 'item',
				formatter: '{b}: {c} hrs ({d}%)',
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
					name: 'Horas Transmitidas',
					type: 'pie',
					radius: ['45%', '70%'],
					center: ['50%', '42%'],
					avoidLabelOverlap: false,
					itemStyle: {
						borderRadius: 6,
						borderColor: '#111827',
						borderWidth: 2
					},
					label: { show: false },
					data: pieData
				}
			]
		};
	});

	const sessionColumns: Column<StreamingSession>[] = [
		{ key: 'session_title', label: 'Título de Emisión', sortable: true },
		{ key: 'game_or_category', label: 'Categoría', sortable: true },
		{ key: 'platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'hours_streamed', label: 'Horas', align: 'right', isMono: true, sortable: true },
		{ key: 'avg_ccv', label: 'CCV', align: 'right', isMono: true, sortable: true },
		{ key: 'peak_viewers', label: 'Pico', align: 'right', isMono: true, sortable: true },
		{ key: 'total_earnings', label: 'Ingresos ($)', align: 'right', isMono: true, sortable: true }
	];
</script>

<svelte:head>
	<title>Analytics Dashboard | RRSS Creators Analyzer</title>
</svelte:head>

<div class="space-y-6">
	<!-- Page Header & Action Bar -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<TrendingUp class="text-indigo-400" size={24} />
				<span>Panel de Rendimiento Global</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				Métricas agregadas en tiempo real de directos, videos y canales para el espacio activo.
			</p>
		</div>

		<!-- Action bar con botón de filtros a la DERECHA -->
		<div class="flex items-center gap-3">
			<FilterTriggerButton
				isOpen={isFilterDrawerOpen}
				activeCount={activeFiltersCount}
				label="Filtros de Análisis"
				size="sm"
				onclick={() => (isFilterDrawerOpen = !isFilterDrawerOpen)}
			/>

			<a
				href="/import"
				class="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-600/20"
			>
				<Plus size={14} />
				<span>Ingestar Datos</span>
			</a>
		</div>
	</div>

	<!-- KPIs / Stat Cards Reactivos -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<StatCard
			title="Ingresos Totales"
			value={formatCurrency(summary.totalEarnings)}
			changePct={summary.earningsChangePct}
			icon={DollarSign}
			iconColor="emerald"
			subtitle="Streams + Videos"
		/>

		<StatCard
			title="Horas Transmitidas"
			value={`${summary.totalHours} hrs`}
			changePct={summary.hoursChangePct}
			icon={Clock}
			iconColor="indigo"
			subtitle={`${summary.totalSessions} directos`}
		/>

		<StatCard
			title="Media de Concurrencia (CCV)"
			value={formatNumber(summary.avgCcv)}
			changePct={summary.ccvChangePct}
			icon={Users}
			iconColor="cyan"
			subtitle={`Pico máx: ${formatNumber(summary.peakViewers)}`}
		/>

		<StatCard
			title="Rendimiento ($ / Hora)"
			value={formatCurrency(summary.earningsPerHour)}
			icon={Zap}
			iconColor="amber"
			subtitle="Eficiencia estimada"
		/>
	</div>

	<!-- Gráficos Interactivos ECharts -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Gráfico de Audiencia (CCV & Pico) -->
		<div class="lg:col-span-2 rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-4">
				<h3 class="text-sm font-semibold text-white">Evolución de Audiencia (CCV & Picos)</h3>
				<span class="text-xs text-gray-500 font-mono">{sessions.length} sesiones analizadas</span>
			</div>
			<div class="h-72 w-full">
				<EChart options={audienceChartOptions} />
			</div>
		</div>

		<!-- Gráfico de Cuota por Categoría (Pie) -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-4">
				<h3 class="text-sm font-semibold text-white">Horas por Categoría</h3>
			</div>
			<div class="h-72 w-full">
				<EChart options={categoryShareOptions} />
			</div>
		</div>
	</div>

	<!-- Gráfico de Ingresos por Día -->
	<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-sm font-semibold text-white">Ingresos por Sesión de Transmisión</h3>
			<span class="text-xs text-emerald-400 font-mono font-semibold">
				Total: {formatCurrency(sessions.reduce((a, b) => a + Number(b.total_earnings || 0), 0))}
			</span>
		</div>
		<div class="h-64 w-full">
			<EChart options={revenueChartOptions} />
		</div>
	</div>

	<!-- Tabla Resumen de Sesiones Recientes -->
	<div class="space-y-3">
		<div class="flex items-center justify-between">
			<h3 class="text-base font-semibold text-white flex items-center gap-2">
				<Radio size={16} class="text-indigo-400" />
				<span>Últimas Sesiones Filtradas ({sessions.length})</span>
			</h3>
		</div>

		<DataTable
			data={sessions}
			columns={sessionColumns}
			searchPlaceholder="Buscar por título o categoría..."
			searchKeys={['session_title', 'game_or_category', 'platform']}
		/>
	</div>

	<!-- Drawer de Filtros a la DERECHA -->
	<FilterDrawer
		isOpen={isFilterDrawerOpen}
		position="right"
		title="Filtros de Análisis"
		activeCount={activeFiltersCount}
		onClose={() => (isFilterDrawerOpen = false)}
		onReset={resetFilters}
	>
		<!-- 1. Rango de Fechas -->
		<FilterSection title="Periodo de Tiempo" defaultOpen={true}>
			<DateRangeFilter
				value={filters.dateRange}
				onchange={(val) => (filters.dateRange = val)}
			/>
		</FilterSection>

		<!-- 2. Plataformas -->
		<FilterSection title="Plataformas de Streaming" defaultOpen={true}>
			<PlatformFilter
				selectedPlatforms={filters.platforms}
				onchange={(p) => (filters.platforms = p)}
			/>
		</FilterSection>

		<!-- 3. Umbrales de Audiencia e Ingresos -->
		<FilterSection title="Métricas y Rendimiento" defaultOpen={false}>
			<div class="space-y-3">
				<RangeFilter
					label="Concurrencia Mínima (CCV)"
					placeholderMin="ej. 500"
					placeholderMax="Sin límite"
					min={filters.minCcv}
					onchange={(r) => (filters.minCcv = r.min)}
				/>
				<RangeFilter
					label="Ingresos Mínimos por Sesión"
					unit="$ USD"
					placeholderMin="ej. 100"
					placeholderMax="Sin límite"
					min={filters.minEarnings}
					onchange={(r) => (filters.minEarnings = r.min)}
				/>
			</div>
		</FilterSection>

		<!-- 4. Categorías de Streaming -->
		{#if availableCategories.length > 0}
			<FilterSection title="Categorías / Juegos" defaultOpen={false}>
				<MultiSelectFilter
					options={availableCategories}
					selected={filters.categories}
					searchPlaceholder="Filtrar categorías..."
					onchange={(selected) => (filters.categories = selected)}
				/>
			</FilterSection>
		{/if}
	</FilterDrawer>
</div>
