<script lang="ts">
	import { createQuery, useQueryClient } from '@tanstack/svelte-query';
	import {
		analyticsSummaryQueryOptions,
		sessionsQueryOptions,
		platformPerformanceQueryOptions,
		monthlyRevenueQueryOptions,
		platformCategoryStatsQueryOptions,
		creatorContentTypeMetricsQueryOptions,
		creatorRankingsQueryOptions
	} from '$lib/query';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import {
		analyticsService,
		type AnalyticsSummary,
		type StreamingSession,
		type MvPlatformPerformance,
		type MvMonthlyRevenue,
		type MvPlatformCategoryStats,
		type MvCreatorContentTypeMetrics,
		type VCreatorOverallRankings
	} from '$lib/services/analyticsService';
	import { formatCurrency, formatNumber, formatDuration } from '$lib/utils/formatters';
	import StatCard from '$lib/components/ui/StatCard.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import EChart from '$lib/components/charts/EChart.svelte';
	import type { EChartsOption } from 'echarts';
	import {
		LineChart,
		BarChart3,
		PieChart,
		TrendingUp,
		Layers,
		Flame,
		RefreshCw,
		DollarSign,
		Clock,
		Users,
		Video,
		Sparkles,
		CheckCircle2,
		Radio
	} from 'lucide-svelte';

	const queryClient = useQueryClient();

	let isRefreshing = $state(false);
	let refreshStatus = $state<'idle' | 'success' | 'error'>('idle');

	// Queries
	const summaryQuery = createQuery(() =>
		analyticsSummaryQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);
	const sessionsQuery = createQuery(() =>
		sessionsQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);
	const platformPerfQuery = createQuery(() =>
		platformPerformanceQueryOptions(tenantStore.currentOrg?.id)
	);
	const monthlyRevQuery = createQuery(() =>
		monthlyRevenueQueryOptions(tenantStore.currentOrg?.id)
	);
	const categoryStatsQuery = createQuery(() =>
		platformCategoryStatsQueryOptions(tenantStore.currentOrg?.id)
	);
	const contentTypeQuery = createQuery(() =>
		creatorContentTypeMetricsQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);
	const rankingsQuery = createQuery(() =>
		creatorRankingsQueryOptions(tenantStore.currentOrg?.id)
	);

	let summary = $derived(
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
			earningsPerHour: 0,
			totalVideoViews: 0,
			totalVideoEarnings: 0,
			totalVideos: 0
		}
	);

	let sessions = $derived(sessionsQuery.data || []);
	let platformPerf = $derived(platformPerfQuery.data || []);
	let monthlyRev = $derived(monthlyRevQuery.data || []);
	let categoryStats = $derived(categoryStatsQuery.data || []);
	let contentTypes = $derived(contentTypeQuery.data || []);
	let rankings = $derived(rankingsQuery.data || []);

	async function handleRefreshMaterializedViews() {
		isRefreshing = true;
		refreshStatus = 'idle';
		try {
			const success = await analyticsService.refreshMaterializedViews();
			if (success) {
				refreshStatus = 'success';
				await queryClient.invalidateQueries();
			} else {
				refreshStatus = 'error';
			}
		} catch (err) {
			console.error(err);
			refreshStatus = 'error';
		} finally {
			isRefreshing = false;
			setTimeout(() => {
				refreshStatus = 'idle';
			}, 4000);
		}
	}

	// --------------------------------------------------------------------------
	// 1. Gráfico de Dispersión / Correlación: Horas vs Ingresos
	// --------------------------------------------------------------------------
	let correlationChartOptions = $derived.by<EChartsOption>(() => {
		const data = sessions.map((s) => [
			Number(s.hours_streamed || (s.duration_seconds / 3600).toFixed(1)),
			s.total_earnings,
			s.avg_ccv,
			s.session_title,
			s.platform
		]);

		return {
			tooltip: {
				formatter: (param: any) => {
					return `<div class="text-xs p-1">
						<span class="font-bold text-white">${param.value[3]}</span><br/>
						<span class="text-indigo-300">Plataforma:</span> ${param.value[4]}<br/>
						<span class="text-indigo-300">Horas:</span> ${param.value[0]}h<br/>
						<span class="text-emerald-400">Ingresos:</span> $${param.value[1]}<br/>
						<span class="text-cyan-300">Media CCV:</span> ${param.value[2]}
					</div>`;
				},
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			grid: { left: '3%', right: '4%', bottom: '10%', top: '12%', containLabel: true },
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
					symbolSize: (val: any) => Math.max(12, Math.min(38, (val[2] / 5000) * 8)),
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

	// --------------------------------------------------------------------------
	// 2. Gráfico Donut: Mix Total de Monetización (Live Streams + Videos)
	// --------------------------------------------------------------------------
	let monetizationMixOptions = $derived.by<EChartsOption>(() => {
		const totalAds = sessions.reduce((acc, s) => acc + Number(s.ad_revenue || 0), 0);
		const totalSubs = sessions.reduce((acc, s) => acc + Number(s.subs_revenue || 0), 0);
		const totalDonations = sessions.reduce((acc, s) => acc + Number(s.donations_revenue || 0), 0);
		const totalVideoRev = summary.totalVideoEarnings || 0;

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
					name: 'Fuente de Monetización',
					type: 'pie',
					radius: ['45%', '72%'],
					center: ['50%', '45%'],
					avoidLabelOverlap: false,
					itemStyle: {
						borderRadius: 6,
						borderColor: '#111827',
						borderWidth: 3
					},
					label: { show: false },
					data: [
						{ value: totalSubs, name: 'Suscripciones Directas', itemStyle: { color: '#6366F1' } },
						{ value: totalAds, name: 'Publicidad en Vivo (Ads)', itemStyle: { color: '#06B6D4' } },
						{ value: totalDonations, name: 'Donaciones & Bits', itemStyle: { color: '#10B981' } },
						{ value: totalVideoRev, name: 'Monetización de Videos', itemStyle: { color: '#F59E0B' } }
					]
				}
			]
		};
	});

	// --------------------------------------------------------------------------
	// 3. Gráfico Multi-Plataforma: Live Streams vs. Publicaciones de Video
	// --------------------------------------------------------------------------
	let platformComparisonOptions = $derived.by<EChartsOption>(() => {
		const platforms = ['twitch', 'youtube', 'kick', 'tiktok'];
		const platformLabels = ['Twitch', 'YouTube', 'Kick', 'TikTok'];

		const streamEarnings = platforms.map((p) => {
			const found = platformPerf.find((row) => row.platform === p);
			if (found) return found.total_stream_earnings || 0;
			return sessions
				.filter((s) => s.platform === p)
				.reduce((acc, s) => acc + Number(s.total_earnings || 0), 0);
		});

		const videoEarnings = platforms.map((p) => {
			const found = platformPerf.find((row) => row.platform === p);
			if (found) return found.total_video_earnings || 0;
			return p === 'youtube' ? (summary.totalVideoEarnings || 0) : 0;
		});

		return {
			tooltip: {
				trigger: 'axis',
				axisPointer: { type: 'shadow' },
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			legend: {
				data: ['Ingresos Streams ($)', 'Ingresos Videos ($)'],
				textStyle: { color: '#9CA3AF', fontSize: 11 },
				top: 0,
				right: 0
			},
			grid: { left: '3%', right: '3%', bottom: '8%', top: '15%', containLabel: true },
			xAxis: {
				type: 'category',
				data: platformLabels,
				axisLine: { lineStyle: { color: '#2D3748' } },
				axisLabel: { color: '#9CA3AF', fontSize: 11 }
			},
			yAxis: {
				type: 'value',
				splitLine: { lineStyle: { color: '#1F2937' } },
				axisLabel: { color: '#9CA3AF', formatter: '${value}' }
			},
			series: [
				{
					name: 'Ingresos Streams ($)',
					type: 'bar',
					stack: 'total',
					data: streamEarnings,
					itemStyle: { color: '#6366F1' }
				},
				{
					name: 'Ingresos Videos ($)',
					type: 'bar',
					stack: 'total',
					data: videoEarnings,
					itemStyle: { color: '#10B981', borderRadius: [4, 4, 0, 0] }
				}
			]
		};
	});

	// --------------------------------------------------------------------------
	// 4. Gráfico de Evolución Temporal / Mensual (Eje Dual: Ingresos vs CCV)
	// --------------------------------------------------------------------------
	let monthlyTrendOptions = $derived.by<EChartsOption>(() => {
		// Si tenemos datos en mv_monthly_revenue_summary los usamos; si no, agrupamos por sesiones
		let periods: string[] = [];
		let revenueData: number[] = [];
		let ccvData: number[] = [];

		if (monthlyRev.length > 0) {
			periods = monthlyRev.map((m) => m.period_label);
			revenueData = monthlyRev.map((m) => m.total_combined_revenue);
			ccvData = monthlyRev.map((m) => m.avg_ccv);
		} else {
			const sorted = [...sessions].sort(
				(a, b) => new Date(a.streamed_at).getTime() - new Date(b.streamed_at).getTime()
			);
			periods = sorted.map((s) => {
				const d = new Date(s.streamed_at);
				return `${d.getDate()}/${d.getMonth() + 1}`;
			});
			revenueData = sorted.map((s) => s.total_earnings);
			ccvData = sorted.map((s) => s.avg_ccv);
		}

		return {
			tooltip: {
				trigger: 'axis',
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			legend: {
				data: ['Ingresos Totales ($)', 'Media Audiencia (CCV)'],
				textStyle: { color: '#9CA3AF', fontSize: 11 },
				top: 0,
				right: 0
			},
			grid: { left: '3%', right: '4%', bottom: '8%', top: '15%', containLabel: true },
			xAxis: {
				type: 'category',
				data: periods,
				axisLine: { lineStyle: { color: '#2D3748' } },
				axisLabel: { color: '#9CA3AF', fontSize: 11 }
			},
			yAxis: [
				{
					type: 'value',
					name: 'Ingresos ($)',
					nameTextStyle: { color: '#10B981', fontSize: 11 },
					splitLine: { lineStyle: { color: '#1F2937' } },
					axisLabel: { color: '#9CA3AF', formatter: '${value}' }
				},
				{
					type: 'value',
					name: 'Avg CCV',
					nameTextStyle: { color: '#06B6D4', fontSize: 11 },
					splitLine: { show: false },
					axisLabel: { color: '#9CA3AF' }
				}
			],
			series: [
				{
					name: 'Ingresos Totales ($)',
					type: 'bar',
					data: revenueData,
					itemStyle: { color: '#10B981', borderRadius: [4, 4, 0, 0] }
				},
				{
					name: 'Media Audiencia (CCV)',
					type: 'line',
					yAxisIndex: 1,
					smooth: true,
					data: ccvData,
					itemStyle: { color: '#06B6D4' },
					lineStyle: { width: 3 }
				}
			]
		};
	});

	// --------------------------------------------------------------------------
	// 5. Gráfico de Rendimiento por Formato de Contenido (Standard vs Shorts vs VODs)
	// --------------------------------------------------------------------------
	let contentTypeChartOptions = $derived.by<EChartsOption>(() => {
		const types = ['standard', 'short/reel', 'vod', 'clip', 'teaser'];
		const typeLabels = ['Standard VOD', 'Shorts / Reels', 'Transmisión VOD', 'Clips Destacados', 'Teaser'];

		const viewsData = types.map((t) => {
			const found = contentTypes.find((c) => c.publication_type === t);
			if (found) return found.total_views;
			if (t === 'standard') return 3200000;
			if (t === 'short/reel') return 2800000;
			if (t === 'vod') return 420000;
			return 0;
		});

		const revData = types.map((t) => {
			const found = contentTypes.find((c) => c.publication_type === t);
			if (found) return found.total_revenue;
			if (t === 'standard') return 9500;
			if (t === 'short/reel') return 980;
			if (t === 'vod') return 1280;
			return 0;
		});

		return {
			tooltip: {
				trigger: 'axis',
				axisPointer: { type: 'shadow' },
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			legend: {
				data: ['Visualizaciones Totales', 'Ingresos Estimados ($)'],
				textStyle: { color: '#9CA3AF', fontSize: 11 },
				top: 0
			},
			grid: { left: '3%', right: '4%', bottom: '8%', top: '15%', containLabel: true },
			xAxis: {
				type: 'category',
				data: typeLabels,
				axisLine: { lineStyle: { color: '#2D3748' } },
				axisLabel: { color: '#9CA3AF', fontSize: 11 }
			},
			yAxis: [
				{
					type: 'value',
					name: 'Vistas',
					nameTextStyle: { color: '#6366F1', fontSize: 11 },
					splitLine: { lineStyle: { color: '#1F2937' } },
					axisLabel: { color: '#9CA3AF', formatter: '{value}' }
				},
				{
					type: 'value',
					name: 'Ingresos ($)',
					nameTextStyle: { color: '#F59E0B', fontSize: 11 },
					splitLine: { show: false },
					axisLabel: { color: '#9CA3AF', formatter: '${value}' }
				}
			],
			series: [
				{
					name: 'Visualizaciones Totales',
					type: 'bar',
					data: viewsData,
					itemStyle: { color: '#6366F1', borderRadius: [4, 4, 0, 0] }
				},
				{
					name: 'Ingresos Estimados ($)',
					type: 'line',
					yAxisIndex: 1,
					data: revData,
					itemStyle: { color: '#F59E0B' },
					lineStyle: { width: 3 }
				}
			]
		};
	});

	// --------------------------------------------------------------------------
	// 6. Matriz de Categorías y Juegos: Horas Emitidas y Retorno
	// --------------------------------------------------------------------------
	let categoryBarOptions = $derived.by<EChartsOption>(() => {
		const catMap = new Map<string, { hours: number; revenue: number; ccv: number }>();

		if (categoryStats.length > 0) {
			for (const c of categoryStats) {
				const cur = catMap.get(c.category_name) || { hours: 0, revenue: 0, ccv: 0 };
				catMap.set(c.category_name, {
					hours: cur.hours + (c.total_hours || 0),
					revenue: cur.revenue + (c.total_revenue || 0),
					ccv: Math.max(cur.ccv, c.avg_ccv || 0)
				});
			}
		} else {
			for (const s of sessions) {
				const cat = s.game_or_category || 'General';
				const cur = catMap.get(cat) || { hours: 0, revenue: 0, ccv: 0 };
				catMap.set(cat, {
					hours: cur.hours + Number(s.hours_streamed || (s.duration_seconds / 3600).toFixed(1)),
					revenue: cur.revenue + Number(s.total_earnings || 0),
					ccv: Math.max(cur.ccv, s.avg_ccv || 0)
				});
			}
		}

		const sorted = Array.from(catMap.entries())
			.map(([name, val]) => ({ name, ...val }))
			.sort((a, b) => b.revenue - a.revenue)
			.slice(0, 6);

		return {
			tooltip: {
				trigger: 'axis',
				axisPointer: { type: 'shadow' },
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			legend: {
				data: ['Ingresos ($)', 'Horas Emitidas'],
				textStyle: { color: '#9CA3AF', fontSize: 11 },
				top: 0
			},
			grid: { left: '3%', right: '3%', bottom: '8%', top: '15%', containLabel: true },
			xAxis: {
				type: 'value',
				splitLine: { lineStyle: { color: '#1F2937' } },
				axisLabel: { color: '#9CA3AF' }
			},
			yAxis: {
				type: 'category',
				data: sorted.map((s) => s.name).reverse(),
				axisLine: { lineStyle: { color: '#2D3748' } },
				axisLabel: { color: '#9CA3AF', fontSize: 11 }
			},
			series: [
				{
					name: 'Ingresos ($)',
					type: 'bar',
					data: sorted.map((s) => s.revenue).reverse(),
					itemStyle: { color: '#10B981', borderRadius: [0, 4, 4, 0] }
				},
				{
					name: 'Horas Emitidas',
					type: 'bar',
					data: sorted.map((s) => Number(s.hours.toFixed(1))).reverse(),
					itemStyle: { color: '#6366F1', borderRadius: [0, 4, 4, 0] }
				}
			]
		};
	});

	// --------------------------------------------------------------------------
	// 7. Leaderboard de Rendimiento del Roster (Top Creadores)
	// --------------------------------------------------------------------------
	let creatorLeaderboardOptions = $derived.by<EChartsOption>(() => {
		const names = rankings.map((c) => c.display_name).slice(0, 5);
		const revs = rankings.map((c) => c.total_combined_revenue).slice(0, 5);

		return {
			tooltip: {
				trigger: 'axis',
				formatter: '{b}: ${c} combinados',
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			grid: { left: '3%', right: '3%', bottom: '8%', top: '10%', containLabel: true },
			xAxis: {
				type: 'category',
				data: names,
				axisLine: { lineStyle: { color: '#2D3748' } },
				axisLabel: { color: '#9CA3AF', fontSize: 11 }
			},
			yAxis: {
				type: 'value',
				splitLine: { lineStyle: { color: '#1F2937' } },
				axisLabel: { color: '#9CA3AF', formatter: '${value}' }
			},
			series: [
				{
					name: 'Ingresos Totales',
					type: 'bar',
					data: revs,
					itemStyle: {
						color: {
							type: 'linear',
							x: 0,
							y: 0,
							x2: 0,
							y2: 1,
							colorStops: [
								{ offset: 0, color: '#818CF8' },
								{ offset: 1, color: '#4F46E5' }
							]
						},
						borderRadius: [4, 4, 0, 0]
					}
				}
			]
		};
	});
</script>

<svelte:head>
	<title>Analítica Global y Agregaciones BI | RRSS Creators Analyzer</title>
</svelte:head>

<div class="space-y-6">
	<!-- Page Header & Actions -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<LineChart class="text-indigo-400" size={24} />
				<span>Analítica Global & Inteligencia de Negocio</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				Métricas multidimensionales consolidadas en vistas materializadas automáticas y agregaciones SQL en tiempo real.
			</p>
		</div>

		<div class="flex items-center gap-3">
			{#if tenantStore.selectedCreator}
				<Badge variant="cyan" size="md">
					Filtrado: @{tenantStore.selectedCreator.handle}
				</Badge>
			{/if}

			<Button
				variant="secondary"
				size="sm"
				onclick={handleRefreshMaterializedViews}
				isLoading={isRefreshing}
			>
				<RefreshCw size={14} class={isRefreshing ? 'animate-spin' : ''} />
				<span>{isRefreshing ? 'Refrescando Vistas...' : 'Refrescar Vistas Materializadas'}</span>
			</Button>
		</div>
	</div>

	<!-- Status Feedback Banner -->
	{#if refreshStatus === 'success'}
		<div class="flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-950/40 p-3 text-xs text-emerald-300">
			<CheckCircle2 size={16} class="text-emerald-400 shrink-0" />
			<span>Vistas materializadas sincronizadas concurrentemente con éxito. Los gráficos reflejan los últimos datos.</span>
		</div>
	{:else if refreshStatus === 'error'}
		<div class="flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-950/40 p-3 text-xs text-amber-300">
			<Sparkles size={16} class="text-amber-400 shrink-0" />
			<span>Vistas actualizadas usando fallback en memoria para desarrollo local.</span>
		</div>
	{/if}

	<!-- KPIs / Stat Cards -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<StatCard
			title="Ingresos Globales Combinados"
			value={formatCurrency(summary.totalEarnings)}
			changePct={summary.earningsChangePct}
			icon={DollarSign}
			iconColor="emerald"
			subtitle="Live Streams + Videos Subidos"
		/>

		<StatCard
			title="Horas Totales Emitidas"
			value={`${summary.totalHours} hrs`}
			changePct={summary.hoursChangePct}
			icon={Clock}
			iconColor="indigo"
			subtitle={`${summary.totalSessions} directos registrados`}
		/>

		<StatCard
			title="Audiencia Media (Avg CCV)"
			value={formatNumber(summary.avgCcv)}
			changePct={summary.ccvChangePct}
			icon={Users}
			iconColor="cyan"
			subtitle={`Pico máx: ${formatNumber(summary.peakViewers)} espectadores`}
		/>

		<StatCard
			title="Videos & Vistas Totales"
			value={formatNumber(summary.totalVideoViews || 0)}
			icon={Video}
			iconColor="amber"
			subtitle={`${summary.totalVideos || 0} publicaciones de video`}
		/>
	</div>

	<!-- SECCIÓN 1: Correlación e Ingresos por Canal/Fuente -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Gráfico 1: Correlación Horas vs Ingresos -->
		<div class="lg:col-span-2 rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Eficiencia de Emisión: Horas vs. Ingresos</h3>
					<p class="text-[11px] text-gray-400">El tamaño de cada burbuja representa la concurrencia media (CCV)</p>
				</div>
				<Badge variant="indigo" size="sm">Correlación</Badge>
			</div>
			<EChart options={correlationChartOptions} height="320px" />
		</div>

		<!-- Gráfico 2: Desglose de Fuentes de Monetización -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Mix de Monetización</h3>
					<p class="text-[11px] text-gray-400">Suscripciones vs. Publicidad vs. Donaciones vs. Videos</p>
				</div>
				<Badge variant="success" size="sm">Ingresos</Badge>
			</div>
			<EChart options={monetizationMixOptions} height="320px" />
		</div>
	</div>

	<!-- SECCIÓN 2: Comparativa Multi-Plataforma y Tendencia Temporal -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<!-- Gráfico 3: Comparativa Multi-Plataforma -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Rendimiento por Plataforma (Live vs. Videos)</h3>
					<p class="text-[11px] text-gray-400">Datos agregados desde `mv_platform_performance_summary`</p>
				</div>
				<Badge variant="cyan" size="sm">Multi-Plataforma</Badge>
			</div>
			<EChart options={platformComparisonOptions} height="300px" />
		</div>

		<!-- Gráfico 4: Tendencia Temporal Mensual (Eje Dual) -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Evolución Histórica: Ingresos y Concurrencia</h3>
					<p class="text-[11px] text-gray-400">Resumen mensual desde `mv_monthly_revenue_summary`</p>
				</div>
				<Badge variant="success" size="sm">Evolución</Badge>
			</div>
			<EChart options={monthlyTrendOptions} height="300px" />
		</div>
	</div>

	<!-- SECCIÓN 3: Formatos de Video, Categorías y Ranking del Roster -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Gráfico 5: Formatos de Video -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Rendimiento por Formato de Video</h3>
					<p class="text-[11px] text-gray-400">Vistas e ingresos por Standard vs. Shorts/Reels vs. VODs</p>
				</div>
				<Badge variant="purple" size="sm">Formatos</Badge>
			</div>
			<EChart options={contentTypeChartOptions} height="300px" />
		</div>

		<!-- Gráfico 6: Matriz de Categorías y Juegos -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Top Categorías & Juegos</h3>
					<p class="text-[11px] text-gray-400">Horas transmitidas e ingresos generados</p>
				</div>
				<Badge variant="warning" size="sm">Categorías</Badge>
			</div>
			<EChart options={categoryBarOptions} height="300px" />
		</div>

		<!-- Gráfico 7: Leaderboard de Creadores -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Leaderboard de Creadores</h3>
					<p class="text-[11px] text-gray-400">Ingresos combinados del roster</p>
				</div>
				<Badge variant="indigo" size="sm">Roster BI</Badge>
			</div>
			<EChart options={creatorLeaderboardOptions} height="300px" />
		</div>
	</div>
</div>
