<script lang="ts">
	import { page } from '$app/state';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import { creatorService, type CreatorWithChannels } from '$lib/services/creatorService';
	import {
		analyticsService,
		type StreamingSession,
		type AnalyticsSummary
	} from '$lib/services/analyticsService';
	import { videoService, type VideoWithDetails } from '$lib/services/videoService';
	import { formatCurrency, formatNumber } from '$lib/utils/formatters';
	import StatCard from '$lib/components/ui/StatCard.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
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
		type DashboardFilterState
	} from '$lib/components/filters';
	import {
		BarChart3,
		LineChart,
		DollarSign,
		Clock,
		Users,
		Zap,
		ArrowLeft,
		Video,
		Sparkles
	} from 'lucide-svelte';

	import { createQuery } from '@tanstack/svelte-query';
	import { creatorDetailQueryOptions } from '$lib/query/creators';
	import { sessionsQueryOptions } from '$lib/query/sessions';
	import { videosQueryOptions } from '$lib/query/videos';
	import { analyticsSummaryQueryOptions } from '$lib/query/analytics';

	let creatorId = $derived(page.params.id);

	const creatorQuery = createQuery(() => creatorDetailQueryOptions(creatorId));
	const sessionsQuery = createQuery(() =>
		sessionsQueryOptions(tenantStore.currentOrg?.id, creatorId)
	);
	const videosQuery = createQuery(() =>
		videosQueryOptions(tenantStore.currentOrg?.id, creatorId)
	);
	const summaryQuery = createQuery(() =>
		analyticsSummaryQueryOptions(tenantStore.currentOrg?.id, creatorId)
	);

	let creator = $derived(creatorQuery.data || null);
	let rawSessions = $derived(sessionsQuery.data || []);
	let rawVideos = $derived(videosQuery.data || []);
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

	let isLoading = $derived(
		creatorQuery.isLoading || sessionsQuery.isLoading || videosQuery.isLoading || summaryQuery.isLoading
	);
	let isFilterDrawerOpen = $state(false);

	let filters = $state<DashboardFilterState>({
		dateRange: { preset: 'all' },
		platforms: ['twitch', 'youtube', 'kick', 'tiktok'],
		minCcv: null,
		minEarnings: null,
		categories: []
	});

	// Conteo de filtros activos
	let activeFiltersCount = $derived.by(() => {
		let count = 0;
		if (filters.dateRange.preset !== 'all') count++;
		if (filters.platforms.length < 4) count++;
		if (filters.minCcv !== null && filters.minCcv !== undefined) count++;
		if (filters.minEarnings !== null && filters.minEarnings !== undefined) count++;
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

	// Sesiones filtradas
	let sessions = $derived.by(() => {
		let list = [...rawSessions];

		if (filters.platforms.length > 0) {
			list = list.filter((s) => filters.platforms.includes(s.platform));
		}

		if (filters.dateRange.from) {
			const fromTime = new Date(filters.dateRange.from).getTime();
			list = list.filter((s) => new Date(s.streamed_at).getTime() >= fromTime);
		}
		if (filters.dateRange.to) {
			const toTime = new Date(filters.dateRange.to).getTime() + 86400000;
			list = list.filter((s) => new Date(s.streamed_at).getTime() <= toTime);
		}

		if (filters.minCcv !== null && filters.minCcv !== undefined) {
			list = list.filter((s) => s.avg_ccv >= (filters.minCcv || 0));
		}

		if (filters.minEarnings !== null && filters.minEarnings !== undefined) {
			list = list.filter((s) => s.total_earnings >= (filters.minEarnings || 0));
		}

		return list;
	});

	// Videos filtrados
	let videos = $derived.by(() => {
		let list = [...rawVideos];
		if (filters.platforms.length > 0) {
			list = list.filter((v) => v.platforms.some((p) => filters.platforms.includes(p)));
		}
		return list;
	});

	// Resumen recalculado
	let summary = $derived.by<AnalyticsSummary>(() => {
		const totalStreamEarnings = sessions.reduce((acc, s) => acc + Number(s.total_earnings || 0), 0);
		const totalVideoEarnings = videos.reduce((acc, v) => acc + Number(v.total_revenue || 0), 0);
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
			totalEarnings: totalStreamEarnings + totalVideoEarnings,
			totalHours,
			avgCcv,
			peakViewers,
			totalSessions: sessions.length,
			earningsPerHour
		};
	});

	// Gráfico 1: Concurrencia de Audiencia en Vivo
	let concurrencyChartOptions = $derived.by<EChartsOption>(() => {
		const sorted = [...sessions].sort(
			(a, b) => new Date(a.streamed_at).getTime() - new Date(b.streamed_at).getTime()
		);
		const dates = sorted.map((s) => {
			const d = new Date(s.streamed_at);
			return `${d.getDate()}/${d.getMonth() + 1}`;
		});
		const ccv = sorted.map((s) => s.avg_ccv);
		const peak = sorted.map((s) => s.peak_viewers);

		return {
			tooltip: {
				trigger: 'axis',
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
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
					data: ccv,
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
					data: peak,
					itemStyle: { color: '#06B6D4' }
				}
			]
		};
	});

	// Gráfico 2: Ingresos por Stream
	let earningsChartOptions = $derived.by<EChartsOption>(() => {
		const sorted = [...sessions].sort(
			(a, b) => new Date(a.streamed_at).getTime() - new Date(b.streamed_at).getTime()
		);
		const dates = sorted.map((s) => {
			const d = new Date(s.streamed_at);
			return `${d.getDate()}/${d.getMonth() + 1}`;
		});
		const ad = sorted.map((s) => s.ad_revenue);
		const subs = sorted.map((s) => s.subs_revenue);

		return {
			tooltip: {
				trigger: 'axis',
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			legend: {
				data: ['Publicidad', 'Suscripciones'],
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
				axisLabel: { color: '#9CA3AF', fontSize: 11, formatter: '${value}' }
			},
			series: [
				{
					name: 'Publicidad',
					type: 'bar',
					stack: 'total',
					data: ad,
					itemStyle: { color: '#3B82F6' }
				},
				{
					name: 'Suscripciones',
					type: 'bar',
					stack: 'total',
					data: subs,
					itemStyle: {
						color: '#10B981',
						borderRadius: [4, 4, 0, 0]
					}
				}
			]
		};
	});

	// Gráfico 3: Desglose Streams vs Videos
	let revenueMixOptions = $derived.by<EChartsOption>(() => {
		const streamEarnings = sessions.reduce((acc, s) => acc + Number(s.total_earnings || 0), 0);
		const videoEarnings = videos.reduce((acc, v) => acc + Number(v.total_revenue || 0), 0);

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
					name: 'Mix de Ingresos',
					type: 'pie',
					radius: ['50%', '75%'],
					center: ['50%', '42%'],
					avoidLabelOverlap: false,
					itemStyle: {
						borderRadius: 6,
						borderColor: '#111827',
						borderWidth: 2
					},
					label: { show: false },
					data: [
						{ value: streamEarnings, name: 'Streaming en Vivo', itemStyle: { color: '#6366F1' } },
						{ value: videoEarnings, name: 'Videos Subidos / VODs', itemStyle: { color: '#06B6D4' } }
					]
				}
			]
		};
	});
</script>

<svelte:head>
	<title>{creator?.display_name || 'Creador'} | BI Dashboard</title>
</svelte:head>

<div class="space-y-6">
	<!-- Top Breadcrumb & Action Bar -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div class="flex items-center gap-3">
			<a
				href="/roster/{creatorId}"
				class="flex h-9 w-9 items-center justify-center rounded-xl border border-[#2D3748] bg-[#111827] text-gray-400 hover:border-gray-600 hover:text-white transition-colors"
			>
				<ArrowLeft size={16} />
			</a>

			<div>
				<div class="flex items-center gap-2">
					<h1 class="text-xl font-bold tracking-tight text-white flex items-center gap-2">
						<BarChart3 class="text-indigo-400" size={22} />
						<span>Dashboard Analítico: {creator?.display_name || '...'}</span>
					</h1>
					{#if creator?.primary_platform}
						<Badge variant="purple" size="sm">
							{creator.primary_platform}
						</Badge>
					{/if}
				</div>
				<p class="text-xs text-gray-400 mt-0.5 font-mono">
					@{creator?.handle || ''} • Métricas de rendimiento, ingresos y audiencia
				</p>
			</div>
		</div>

		<!-- Action buttons con Drawer a la DERECHA -->
		<div class="flex items-center gap-3">
			<FilterTriggerButton
				isOpen={isFilterDrawerOpen}
				activeCount={activeFiltersCount}
				label="Filtros del Creador"
				size="sm"
				onclick={() => (isFilterDrawerOpen = !isFilterDrawerOpen)}
			/>

			<a
				href="/roster/{creatorId}"
				class="inline-flex items-center gap-1.5 rounded-xl border border-[#2D3748] bg-[#111827] px-3 py-1.5 text-xs font-semibold text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
			>
				<span>Ver Perfil y Tablas</span>
			</a>
		</div>
	</div>

	<!-- KPIs Grid Reactivo -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<StatCard
			title="Ingresos Totales (Periodo)"
			value={formatCurrency(summary.totalEarnings)}
			icon={DollarSign}
			iconColor="emerald"
			subtitle="Streams + Videos"
		/>

		<StatCard
			title="Horas en Directo"
			value={`${summary.totalHours} hrs`}
			icon={Clock}
			iconColor="indigo"
			subtitle={`${summary.totalSessions} directos analizados`}
		/>

		<StatCard
			title="Media de Concurrencia (CCV)"
			value={formatNumber(summary.avgCcv)}
			icon={Users}
			iconColor="cyan"
			subtitle={`Pico máx: ${formatNumber(summary.peakViewers)}`}
		/>

		<StatCard
			title="Eficiencia ($ / Hora)"
			value={formatCurrency(summary.earningsPerHour)}
			icon={Zap}
			iconColor="amber"
			subtitle="Rendimiento streaming"
		/>
	</div>

	<!-- Gráficos ECharts -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Gráfico de Concurrencia -->
		<div class="lg:col-span-2 rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-4">
				<h3 class="text-sm font-semibold text-white">Evolución de Concurrencia (CCV y Picos)</h3>
				<span class="text-xs text-gray-500 font-mono">{sessions.length} directos</span>
			</div>
			<div class="h-72 w-full">
				<EChart options={concurrencyChartOptions} />
			</div>
		</div>

		<!-- Gráfico de Mix Streams vs Videos -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-4">
				<h3 class="text-sm font-semibold text-white">Mix de Ingresos</h3>
			</div>
			<div class="h-72 w-full">
				<EChart options={revenueMixOptions} />
			</div>
		</div>
	</div>

	<!-- Gráfico de Ingresos por Día -->
	<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-sm font-semibold text-white">Ingresos por Publicidad y Suscripciones</h3>
		</div>
		<div class="h-64 w-full">
			<EChart options={earningsChartOptions} />
		</div>
	</div>

	<!-- Drawer de Filtros a la DERECHA -->
	<FilterDrawer
		isOpen={isFilterDrawerOpen}
		position="right"
		title="Filtros de Rendimiento"
		activeCount={activeFiltersCount}
		onClose={() => (isFilterDrawerOpen = false)}
		onReset={resetFilters}
	>
		<FilterSection title="Periodo de Tiempo" defaultOpen={true}>
			<DateRangeFilter
				value={filters.dateRange}
				onchange={(val) => (filters.dateRange = val)}
			/>
		</FilterSection>

		<FilterSection title="Plataformas" defaultOpen={true}>
			<PlatformFilter
				selectedPlatforms={filters.platforms}
				onchange={(p) => (filters.platforms = p)}
			/>
		</FilterSection>

		<FilterSection title="Umbrales de Métricas" defaultOpen={false}>
			<div class="space-y-3">
				<RangeFilter
					label="Concurrencia Mínima (CCV)"
					min={filters.minCcv}
					onchange={(r) => (filters.minCcv = r.min)}
				/>
				<RangeFilter
					label="Ingresos Mínimos ($)"
					unit="$ USD"
					min={filters.minEarnings}
					onchange={(r) => (filters.minEarnings = r.min)}
				/>
			</div>
		</FilterSection>
	</FilterDrawer>
</div>
