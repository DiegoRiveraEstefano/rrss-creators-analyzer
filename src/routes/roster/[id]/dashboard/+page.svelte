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
		Users,
		UserPlus,
		Eye,
		ThumbsUp,
		Clock,
		ArrowLeft,
		Video,
		Sparkles,
		Radio,
		MessageSquare
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
	let totalDurationSecs = $derived(sessions.reduce((acc, s) => acc + (s.duration_seconds || 0), 0));
	let totalHours = $derived(Number((totalDurationSecs / 3600).toFixed(1)));
	let avgCcv = $derived(
		sessions.length > 0
			? Math.round(sessions.reduce((acc, s) => acc + (s.avg_ccv || 0), 0) / sessions.length)
			: 0
	);
	let peakViewers = $derived(sessions.reduce((acc, s) => Math.max(acc, s.peak_viewers || 0), 0));
	let totalNewFollowers = $derived(sessions.reduce((acc, s) => acc + (s.new_followers || 0), 0));
	let totalVideoViews = $derived(videos.reduce((acc, v) => acc + (v.total_views || 0), 0));
	let totalVideoLikes = $derived(videos.reduce((acc, v) => acc + (v.total_likes || 0), 0));

	// --------------------------------------------------------------------------
	// Gráfico 1: Concurrencia de Audiencia en Vivo (CCV y Picos)
	// --------------------------------------------------------------------------
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

	// --------------------------------------------------------------------------
	// Gráfico 2: Crecimiento de Seguidores y Actividad de Chat por Directo
	// --------------------------------------------------------------------------
	let followersGrowthOptions = $derived.by<EChartsOption>(() => {
		const sorted = [...sessions].sort(
			(a, b) => new Date(a.streamed_at).getTime() - new Date(b.streamed_at).getTime()
		);
		const dates = sorted.map((s) => {
			const d = new Date(s.streamed_at);
			return `${d.getDate()}/${d.getMonth() + 1}`;
		});
		const followers = sorted.map((s) => s.new_followers || 0);
		const chat = sorted.map((s) => s.chat_messages_count || 0);

		return {
			tooltip: {
				trigger: 'axis',
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			legend: {
				data: ['Nuevos Seguidores (+)', 'Mensajes de Chat'],
				textStyle: { color: '#9CA3AF', fontSize: 11 },
				top: 0
			},
			grid: { left: '3%', right: '4%', bottom: '8%', top: '15%', containLabel: true },
			xAxis: {
				type: 'category',
				data: dates,
				axisLine: { lineStyle: { color: '#2D3748' } },
				axisLabel: { color: '#9CA3AF', fontSize: 11 }
			},
			yAxis: [
				{
					type: 'value',
					name: 'Followers',
					nameTextStyle: { color: '#10B981', fontSize: 11 },
					splitLine: { lineStyle: { color: '#1F2937' } },
					axisLabel: { color: '#9CA3AF' }
				},
				{
					type: 'value',
					name: 'Chat',
					nameTextStyle: { color: '#A855F7', fontSize: 11 },
					splitLine: { show: false },
					axisLabel: { color: '#9CA3AF' }
				}
			],
			series: [
				{
					name: 'Nuevos Seguidores (+)',
					type: 'bar',
					data: followers,
					itemStyle: { color: '#10B981', borderRadius: [4, 4, 0, 0] }
				},
				{
					name: 'Mensajes de Chat',
					type: 'line',
					yAxisIndex: 1,
					smooth: true,
					data: chat,
					itemStyle: { color: '#A855F7' },
					lineStyle: { width: 2 }
				}
			]
		};
	});

	// --------------------------------------------------------------------------
	// Gráfico 3: Rendimiento de Videos (Vistas vs Likes)
	// --------------------------------------------------------------------------
	let videoPerformanceOptions = $derived.by<EChartsOption>(() => {
		const topVideos = [...videos].sort((a, b) => (b.total_views || 0) - (a.total_views || 0)).slice(0, 6);
		const titles = topVideos.map((v) => (v.title.length > 20 ? v.title.substring(0, 18) + '...' : v.title));
		const views = topVideos.map((v) => v.total_views || 0);
		const likes = topVideos.map((v) => v.total_likes || 0);

		return {
			tooltip: {
				trigger: 'axis',
				axisPointer: { type: 'shadow' },
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			legend: {
				data: ['Visualizaciones', 'Likes'],
				textStyle: { color: '#9CA3AF', fontSize: 11 },
				top: 0
			},
			grid: { left: '3%', right: '4%', bottom: '8%', top: '15%', containLabel: true },
			xAxis: {
				type: 'category',
				data: titles,
				axisLine: { lineStyle: { color: '#2D3748' } },
				axisLabel: { color: '#9CA3AF', fontSize: 10, rotate: 15 }
			},
			yAxis: [
				{
					type: 'value',
					name: 'Vistas',
					nameTextStyle: { color: '#06B6D4', fontSize: 11 },
					splitLine: { lineStyle: { color: '#1F2937' } },
					axisLabel: { color: '#9CA3AF', formatter: (val: number) => formatNumber(val, true) }
				},
				{
					type: 'value',
					name: 'Likes',
					nameTextStyle: { color: '#EC4899', fontSize: 11 },
					splitLine: { show: false },
					axisLabel: { color: '#9CA3AF', formatter: (val: number) => formatNumber(val, true) }
				}
			],
			series: [
				{
					name: 'Visualizaciones',
					type: 'bar',
					data: views,
					itemStyle: { color: '#06B6D4', borderRadius: [4, 4, 0, 0] }
				},
				{
					name: 'Likes',
					type: 'line',
					yAxisIndex: 1,
					data: likes,
					itemStyle: { color: '#EC4899' },
					lineStyle: { width: 3 }
				}
			]
		};
	});

	// --------------------------------------------------------------------------
	// Gráfico 4: Distribución de Vistas por Plataforma
	// --------------------------------------------------------------------------
	let platformViewsMixOptions = $derived.by<EChartsOption>(() => {
		const platMap = new Map<string, number>();
		for (const v of videos) {
			for (const pub of v.publications || []) {
				platMap.set(pub.platform, (platMap.get(pub.platform) || 0) + (pub.views_count || 0));
			}
		}

		const pieData = Array.from(platMap.entries()).map(([name, value]) => ({
			name: name.toUpperCase(),
			value
		}));

		if (pieData.length === 0) {
			pieData.push({ name: 'SIN DATOS', value: 1 });
		}

		return {
			tooltip: {
				trigger: 'item',
				formatter: '{b}: {c} vistas ({d}%)',
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
					name: 'Vistas por Red',
					type: 'pie',
					radius: ['45%', '72%'],
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
</script>

<svelte:head>
	<title>{creator?.display_name || 'Creador'} | BI Rendimiento</title>
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
						<span>Dashboard de Rendimiento: {creator?.display_name || '...'}</span>
					</h1>
					{#if creator?.primary_platform}
						<Badge variant="purple" size="sm">
							{creator.primary_platform}
						</Badge>
					{/if}
				</div>
				<p class="text-xs text-gray-400 mt-0.5 font-mono">
					@{creator?.handle || ''} • Métricas de retención, crecimiento de seguidores y visualizaciones
				</p>
			</div>
		</div>

		<!-- Action buttons -->
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

	<!-- KPIs Grid Reactivo Enfocado en Rendimiento -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<StatCard
			title="Audiencia Media (Avg CCV)"
			value={formatNumber(avgCcv)}
			icon={Users}
			iconColor="cyan"
			subtitle={`Pico máx: ${formatNumber(peakViewers)} viewers`}
		/>

		<StatCard
			title="Nuevos Seguidores Ganados"
			value={`+${formatNumber(totalNewFollowers, true)}`}
			icon={UserPlus}
			iconColor="emerald"
			subtitle={`${sessions.length} directos analizados`}
		/>

		<StatCard
			title="Visualizaciones de Videos"
			value={formatNumber(totalVideoViews, true)}
			icon={Eye}
			iconColor="indigo"
			subtitle={`${videos.length} videos publicados`}
		/>

		<StatCard
			title="Likes Totales en Videos"
			value={formatNumber(totalVideoLikes, true)}
			icon={ThumbsUp}
			iconColor="purple"
			subtitle="Engagement de publicaciones"
		/>
	</div>

	<!-- Gráficos ECharts -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<!-- Gráfico 1: Concurrencia de Audiencia Live -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-4">
				<h3 class="text-sm font-semibold text-white">Evolución de Concurrencia en Vivo (CCV y Picos)</h3>
				<span class="text-xs text-gray-500 font-mono">{sessions.length} directos</span>
			</div>
			<div class="h-72 w-full">
				<EChart options={concurrencyChartOptions} />
			</div>
		</div>

		<!-- Gráfico 2: Crecimiento de Seguidores y Chat -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-4">
				<h3 class="text-sm font-semibold text-white">Adquisición de Followers & Chat por Directo</h3>
			</div>
			<div class="h-72 w-full">
				<EChart options={followersGrowthOptions} />
			</div>
		</div>
	</div>

	<!-- Gráficos de Video -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Gráfico 3: Rendimiento de Videos (Vistas vs Likes) -->
		<div class="lg:col-span-2 rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-4">
				<h3 class="text-sm font-semibold text-white">Top Videos por Visualizaciones & Likes</h3>
			</div>
			<div class="h-72 w-full">
				<EChart options={videoPerformanceOptions} />
			</div>
		</div>

		<!-- Gráfico 4: Distribución de Vistas por Plataforma -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-4">
				<h3 class="text-sm font-semibold text-white">Cuota de Vistas por Red</h3>
			</div>
			<div class="h-72 w-full">
				<EChart options={platformViewsMixOptions} />
			</div>
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
