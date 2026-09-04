<script lang="ts">
	import { page } from '$app/state';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import { creatorService, type CreatorWithChannels } from '$lib/services/creatorService';
	import { analyticsService, type StreamingSession, type AnalyticsSummary } from '$lib/services/analyticsService';
	import { videoService, type PublishedVideo } from '$lib/services/videoService';
	import { formatCurrency, formatNumber } from '$lib/utils/formatters';
	import StatCard from '$lib/components/ui/StatCard.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import EChart from '$lib/components/charts/EChart.svelte';
	import type { EChartsOption } from 'echarts';
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

	let creatorId = $derived(page.params.id);
	let creator = $state<CreatorWithChannels | null>(null);
	let sessions = $state<StreamingSession[]>([]);
	let videos = $state<PublishedVideo[]>([]);
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

	let isLoading = $state(true);

	async function loadDashboard() {
		if (!creatorId || !tenantStore.currentOrg) return;
		isLoading = true;
		try {
			const [c, s, v, sum] = await Promise.all([
				creatorService.getCreatorById(creatorId),
				analyticsService.getSessions(tenantStore.currentOrg.id, creatorId),
				videoService.getVideosByCreator(creatorId),
				analyticsService.getSummary(tenantStore.currentOrg.id, creatorId)
			]);

			creator = c;
			sessions = s;
			videos = v;
			summary = sum;
		} catch (error) {
			console.error('Error loading creator dashboard:', error);
		} finally {
			isLoading = false;
		}
	}

	$effect(() => {
		if (creatorId && tenantStore.currentOrg) {
			loadDashboard();
		}
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
				axisLabel: { color: '#9CA3AF' }
			},
			yAxis: {
				type: 'value',
				splitLine: { lineStyle: { color: '#1F2937' } },
				axisLabel: { color: '#9CA3AF' }
			},
			series: [
				{
					name: 'Media CCV',
					type: 'line',
					smooth: true,
					data: ccv,
					itemStyle: { color: '#06B6D4' },
					areaStyle: {
						color: {
							type: 'linear',
							x: 0,
							y: 0,
							x2: 0,
							y2: 1,
							colorStops: [
								{ offset: 0, color: 'rgba(6, 182, 212, 0.4)' },
								{ offset: 1, color: 'rgba(6, 182, 212, 0.0)' }
							]
						}
					}
				},
				{
					name: 'Pico Viewers',
					type: 'line',
					smooth: true,
					data: peak,
					itemStyle: { color: '#6366F1' },
					lineStyle: { type: 'dashed', width: 2 }
				}
			]
		};
	});

	// Gráfico 2: Monetización por Categoría
	let categoryChartOptions = $derived.by<EChartsOption>(() => {
		const categoryMap: Record<string, number> = {};
		for (const s of sessions) {
			const cat = s.game_or_category || 'General';
			categoryMap[cat] = (categoryMap[cat] || 0) + Number(s.total_earnings || 0);
		}

		const categories = Object.keys(categoryMap);
		const earnings = Object.values(categoryMap);

		return {
			tooltip: {
				trigger: 'axis',
				formatter: '{b}: ${c}',
				backgroundColor: '#1F2937',
				borderColor: '#374151',
				textStyle: { color: '#F9FAFB' }
			},
			grid: { left: '3%', right: '3%', bottom: '8%', top: '15%', containLabel: true },
			xAxis: {
				type: 'category',
				data: categories,
				axisLine: { lineStyle: { color: '#2D3748' } },
				axisLabel: { color: '#9CA3AF', rotate: 15, fontSize: 10 }
			},
			yAxis: {
				type: 'value',
				splitLine: { lineStyle: { color: '#1F2937' } },
				axisLabel: { color: '#9CA3AF', formatter: '${value}' }
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

	// Gráfico 3: Desglose Streams vs Videos
	let revenueMixOptions = $derived.by<EChartsOption>(() => {
		const streamEarnings = sessions.reduce((acc, s) => acc + Number(s.total_earnings || 0), 0);
		const videoEarnings = videos.reduce((acc, v) => acc + Number(v.estimated_revenue || 0), 0);

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
					type: 'pie',
					radius: ['45%', '70%'],
					itemStyle: {
						borderRadius: 6,
						borderColor: '#111827',
						borderWidth: 3
					},
					data: [
						{ value: streamEarnings, name: 'Transmisiones en Vivo', itemStyle: { color: '#6366F1' } },
						{ value: videoEarnings, name: 'Videos Subidos / VODs', itemStyle: { color: '#06B6D4' } }
					]
				}
			]
		};
	});
</script>

<svelte:head>
	<title>Dashboard Analítico de {creator?.display_name || 'Creador'} | RRSS Creators Analyzer</title>
</svelte:head>

<div class="space-y-6">
	<!-- Top Navigation -->
	<div class="flex items-center justify-between">
		<a href="/roster/{creatorId}" class="inline-flex items-center gap-1.5 text-xs text-gray-400 hover:text-white transition-colors">
			<ArrowLeft size={14} />
			<span>Volver a Perfil de {creator?.display_name || 'Creador'}</span>
		</a>

		<div class="flex items-center gap-2">
			<Badge variant="cyan" size="md">
				Dashboard Individual
			</Badge>
		</div>
	</div>

	<!-- Title Header -->
	<div class="flex items-center gap-4">
		{#if creator?.avatar_url}
			<img
				src={creator.avatar_url}
				alt={creator.display_name}
				class="h-12 w-12 rounded-xl object-cover ring-2 ring-cyan-500/40"
			/>
		{/if}
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<span>Dashboard Analítico: {creator?.display_name || 'Creador'}</span>
			</h1>
			<p class="text-xs text-gray-400">
				Métricas avanzadas de monetización, visualizaciones y retención exclusivas de este talento.
			</p>
		</div>
	</div>

	<!-- KPIs -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<StatCard
			title="Ingresos Totales Combinados"
			value={formatCurrency(summary.totalEarnings)}
			icon={DollarSign}
			iconColor="emerald"
		/>

		<StatCard
			title="Horas en Vivo"
			value={`${summary.totalHours}h`}
			icon={Clock}
			iconColor="indigo"
		/>

		<StatCard
			title="Media CCV"
			value={formatNumber(summary.avgCcv)}
			icon={Users}
			iconColor="cyan"
		/>

		<StatCard
			title="Rendimiento $/Hora Stream"
			value={`${formatCurrency(summary.earningsPerHour)}/h`}
			icon={Zap}
			iconColor="amber"
		/>
	</div>

	<!-- Visualizaciones Gráficas -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<div class="rounded-xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Evolución de Audiencia en Directo (CCV)</h3>
					<p class="text-[11px] text-gray-400">Media de espectadores concurrentes y picos</p>
				</div>
				<Badge variant="cyan" size="sm">Streams</Badge>
			</div>
			<EChart options={concurrencyChartOptions} height="280px" />
		</div>

		<div class="rounded-xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
			<div class="flex items-center justify-between mb-3">
				<div>
					<h3 class="text-sm font-semibold text-white">Mix de Ingresos: Streams vs. Videos</h3>
					<p class="text-[11px] text-gray-400">Distribución de monetización total</p>
				</div>
				<Badge variant="indigo" size="sm">Monetización</Badge>
			</div>
			<EChart options={revenueMixOptions} height="280px" />
		</div>
	</div>

	<div class="rounded-xl border border-[#1F2937] bg-[#111827] p-5 shadow-xl">
		<div class="flex items-center justify-between mb-3">
			<div>
				<h3 class="text-sm font-semibold text-white">Ingresos por Categoría / Contenido</h3>
				<p class="text-[11px] text-gray-400">Juegos y tipos de transmisión más rentables</p>
			</div>
			<Badge variant="success" size="sm">Categorías</Badge>
		</div>
		<EChart options={categoryChartOptions} height="280px" />
	</div>
</div>
