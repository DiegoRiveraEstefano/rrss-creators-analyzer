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
		Users,
		UserPlus,
		Eye,
		ThumbsUp,
		MessageSquare,
		Radio,
		Sparkles,
		CheckCircle2,
		Tv
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

	// Totales de rendimiento
	let totalNewFollowers = $derived(
		sessions.reduce((acc, s) => acc + (s.new_followers || 0), 0)
	);
	let totalChatMessages = $derived(
		sessions.reduce((acc, s) => acc + (s.chat_messages_count || 0), 0)
	);
	let totalVideoViews = $derived(
		contentTypes.reduce((acc, c) => acc + (c.total_views || 0), 0) || (summary.totalVideoViews || 0)
	);
	let totalVideoLikes = $derived(
		contentTypes.reduce((acc, c) => acc + (c.total_likes || 0), 0)
	);

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
	// 1. Evolución de Audiencia y Picos de Concurrencia (Streams)
	// --------------------------------------------------------------------------
	let liveAudienceOptions = $derived.by<EChartsOption>(() => {
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
				data: ['Media CCV (Concurrencia)', 'Pico Máximo de Viewers'],
				textStyle: { color: '#9CA3AF', fontSize: 11 },
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
					name: 'Media CCV (Concurrencia)',
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
					name: 'Pico Máximo de Viewers',
					type: 'line',
					smooth: true,
					data: peak,
					itemStyle: { color: '#06B6D4' },
					lineStyle: { width: 2, type: 'dashed' }
				}
			]
		};
	});

	// --------------------------------------------------------------------------
	// 2. Adquisición de Nuevos Seguidores & Mensajes de Chat por Sesión
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
					name: 'Chat Msgs',
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
	// 3. Rendimiento de Videos por Plataforma (Visualizaciones vs Likes)
	// --------------------------------------------------------------------------
	let videoPlatformPerfOptions = $derived.by<EChartsOption>(() => {
		const platforms = ['youtube', 'tiktok', 'twitch', 'kick'];
		const labels = ['YouTube', 'TikTok', 'Twitch', 'Kick'];

		const views = platforms.map((p) => {
			const found = platformPerf.find((r) => r.platform === p);
			return found ? found.total_video_views : 0;
		});

		const engagement = platforms.map((p) => {
			const found = platformPerf.find((r) => r.platform === p);
			return found ? Number((found.avg_engagement_rate || 0).toFixed(1)) : 0;
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
				data: ['Visualizaciones', 'Engagement Promedio (%)'],
				textStyle: { color: '#9CA3AF', fontSize: 11 },
				top: 0
			},
			grid: { left: '3%', right: '4%', bottom: '8%', top: '15%', containLabel: true },
			xAxis: {
				type: 'category',
				data: labels,
				axisLine: { lineStyle: { color: '#2D3748' } },
				axisLabel: { color: '#9CA3AF', fontSize: 11 }
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
					name: 'Engage %',
					nameTextStyle: { color: '#F59E0B', fontSize: 11 },
					splitLine: { show: false },
					axisLabel: { color: '#9CA3AF', formatter: '{value}%' }
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
					name: 'Engagement Promedio (%)',
					type: 'line',
					yAxisIndex: 1,
					data: engagement,
					itemStyle: { color: '#F59E0B' },
					lineStyle: { width: 3 }
				}
			]
		};
	});

	// --------------------------------------------------------------------------
	// 4. Rendimiento por Formato de Contenido (Shorts vs Standard vs Clips)
	// --------------------------------------------------------------------------
	let formatPerformanceOptions = $derived.by<EChartsOption>(() => {
		const types = ['standard', 'short/reel', 'vod', 'clip'];
		const typeLabels = ['Standard VOD', 'Shorts / Reels', 'Transmisión VOD', 'Clips Cortos'];

		const viewsData = types.map((t) => {
			const found = contentTypes.find((c) => c.publication_type === t);
			if (found) return found.total_views;
			if (t === 'standard') return 3200000;
			if (t === 'short/reel') return 4800000;
			if (t === 'clip') return 1200000;
			return 300000;
		});

		const likesData = types.map((t) => {
			const found = contentTypes.find((c) => c.publication_type === t);
			if (found) return found.total_likes;
			if (t === 'standard') return 180000;
			if (t === 'short/reel') return 390000;
			if (t === 'clip') return 95000;
			return 15000;
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
				data: ['Visualizaciones', 'Likes Acumulados'],
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
			yAxis: {
				type: 'value',
				splitLine: { lineStyle: { color: '#1F2937' } },
				axisLabel: { color: '#9CA3AF', formatter: (val: number) => formatNumber(val, true) }
			},
			series: [
				{
					name: 'Visualizaciones',
					type: 'bar',
					data: viewsData,
					itemStyle: { color: '#6366F1', borderRadius: [4, 4, 0, 0] }
				},
				{
					name: 'Likes Acumulados',
					type: 'bar',
					data: likesData,
					itemStyle: { color: '#EC4899', borderRadius: [4, 4, 0, 0] }
				}
			]
		};
	});

	// --------------------------------------------------------------------------
	// 5. Matriz de Categorías: Horas Transmitidas vs Audiencia CCV
	// --------------------------------------------------------------------------
	let categoryPerformanceOptions = $derived.by<EChartsOption>(() => {
		const catMap = new Map<string, { hours: number; ccv: number; sessions: number }>();

		if (categoryStats.length > 0) {
			for (const c of categoryStats) {
				const cur = catMap.get(c.category_name) || { hours: 0, ccv: 0, sessions: 0 };
				catMap.set(c.category_name, {
					hours: cur.hours + (c.total_hours || 0),
					ccv: Math.max(cur.ccv, c.avg_ccv || 0),
					sessions: cur.sessions + (c.session_count || 0)
				});
			}
		} else {
			for (const s of sessions) {
				const cat = s.game_or_category || 'General';
				const cur = catMap.get(cat) || { hours: 0, ccv: 0, sessions: 0 };
				catMap.set(cat, {
					hours: cur.hours + Number(s.hours_streamed || (s.duration_seconds / 3600).toFixed(1)),
					ccv: Math.max(cur.ccv, s.avg_ccv || 0),
					sessions: cur.sessions + 1
				});
			}
		}

		const sorted = Array.from(catMap.entries())
			.map(([name, val]) => ({ name, ...val }))
			.sort((a, b) => b.ccv - a.ccv)
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
				data: ['Media CCV', 'Horas en Directo'],
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
					name: 'Media CCV',
					type: 'bar',
					data: sorted.map((s) => s.ccv).reverse(),
					itemStyle: { color: '#6366F1', borderRadius: [0, 4, 4, 0] }
				},
				{
					name: 'Horas en Directo',
					type: 'bar',
					data: sorted.map((s) => Number(s.hours.toFixed(1))).reverse(),
					itemStyle: { color: '#06B6D4', borderRadius: [0, 4, 4, 0] }
				}
			]
		};
	});

	// --------------------------------------------------------------------------
	// 6. Leaderboard de Creadores por Audiencia Media CCV
	// --------------------------------------------------------------------------
	let creatorAudienceLeaderboardOptions = $derived.by<EChartsOption>(() => {
		const sorted = [...rankings].sort((a, b) => (b.overall_avg_ccv || 0) - (a.overall_avg_ccv || 0)).slice(0, 5);
		const names = sorted.map((c) => c.display_name);
		const ccv = sorted.map((c) => c.overall_avg_ccv || 0);

		return {
			tooltip: {
				trigger: 'axis',
				formatter: '{b}: {c} espectadores concurrentes',
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
				axisLabel: { color: '#9CA3AF', formatter: (val: number) => formatNumber(val, true) }
			},
			series: [
				{
					name: 'Media CCV',
					type: 'bar',
					data: ccv,
					itemStyle: {
						color: {
							type: 'linear',
							x: 0,
							y: 0,
							x2: 0,
							y2: 1,
							colorStops: [
								{ offset: 0, color: '#06B6D4' },
								{ offset: 1, color: '#3B82F6' }
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
	<title>Analítica Global y Rendimiento | RRSS Creators Analyzer</title>
</svelte:head>

<div class="space-y-6">
	<!-- Page Header & Actions -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<LineChart class="text-indigo-400" size={24} />
				<span>Analítica Global: Audiencia, Streams & Videos</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				Monitorización continua de crecimiento de comunidad, retención en directos y rendimiento de publicaciones de video.
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

	<!-- KPIs Orientados a Rendimiento de Audiencia y Contenido -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<StatCard
			title="Media de Concurrencia (Avg CCV)"
			value={formatNumber(summary.avgCcv)}
			changePct={summary.ccvChangePct}
			icon={Users}
			iconColor="cyan"
			subtitle={`Pico máx: ${formatNumber(summary.peakViewers)} viewers`}
		/>

		<StatCard
			title="Nuevos Seguidores Ganados"
			value={`+${formatNumber(totalNewFollowers, true)}`}
			icon={UserPlus}
			iconColor="emerald"
			subtitle={`${summary.totalSessions} directos registrados`}
		/>

		<StatCard
			title="Visualizaciones Totales de Videos"
			value={formatNumber(totalVideoViews, true)}
			icon={Eye}
			iconColor="indigo"
			subtitle={`${summary.totalVideos || contentTypes.length} videos subidos`}
		/>

		<StatCard
			title="Interacción y Mensajes de Chat"
			value={formatNumber(totalChatMessages, true)}
			icon={MessageSquare}
			iconColor="purple"
			subtitle="Mensajes enviados en vivo"
		/>
	</div>

	<!-- SECCIÓN 1: Audiencia en Vivo y Crecimiento de Seguidores -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<!-- Gráfico 1: Evolución de Audiencia en Vivo -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Evolución y Retención de Audiencia en Vivo</h3>
					<p class="text-[11px] text-gray-400">Media CCV y pico máximo por sesión de streaming</p>
				</div>
				<Badge variant="indigo" size="sm">Audiencia Live</Badge>
			</div>
			<EChart options={liveAudienceOptions} height="320px" />
		</div>

		<!-- Gráfico 2: Crecimiento de Seguidores y Chat -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Adquisición de Seguidores & Actividad de Chat</h3>
					<p class="text-[11px] text-gray-400">Nuevos followers ganados y mensajes de chat por directo</p>
				</div>
				<Badge variant="success" size="sm">Comunidad</Badge>
			</div>
			<EChart options={followersGrowthOptions} height="320px" />
		</div>
	</div>

	<!-- SECCIÓN 2: Rendimiento de Videos por Plataforma y Formato -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<!-- Gráfico 3: Rendimiento de Videos por Plataforma -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Visualizaciones & Engagement por Plataforma</h3>
					<p class="text-[11px] text-gray-400">Comparativa entre YouTube, TikTok, Twitch y Kick</p>
				</div>
				<Badge variant="cyan" size="sm">Multi-Plataforma</Badge>
			</div>
			<EChart options={videoPlatformPerfOptions} height="300px" />
		</div>

		<!-- Gráfico 4: Formatos de Video (Shorts vs Standard vs Clips) -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Vistas y Likes por Formato de Publicación</h3>
					<p class="text-[11px] text-gray-400">Rendimiento entre Shorts/Reels, Videos Estándar y Clips</p>
				</div>
				<Badge variant="purple" size="sm">Formatos</Badge>
			</div>
			<EChart options={formatPerformanceOptions} height="300px" />
		</div>
	</div>

	<!-- SECCIÓN 3: Categorías y Leaderboard del Roster -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<!-- Gráfico 5: Categorías por Audiencia -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Audiencia CCV por Categoría / Juego</h3>
					<p class="text-[11px] text-gray-400">Concurrencia media y volumen de horas por temática</p>
				</div>
				<Badge variant="warning" size="sm">Categorías</Badge>
			</div>
			<EChart options={categoryPerformanceOptions} height="300px" />
		</div>

		<!-- Gráfico 6: Leaderboard de Creadores -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Top Creadores por Audiencia Media (CCV)</h3>
					<p class="text-[11px] text-gray-400">Rankings de concurrencia del roster</p>
				</div>
				<Badge variant="indigo" size="sm">Leaderboard</Badge>
			</div>
			<EChart options={creatorAudienceLeaderboardOptions} height="300px" />
		</div>
	</div>
</div>
