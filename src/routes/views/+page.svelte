<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { createQuery, useQueryClient } from '@tanstack/svelte-query';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import {
		analyticsService,
		type MvCreatorPerformance,
		type MvPlatformCategoryStats,
		type MvPlatformPerformance,
		type MvMonthlyRevenue,
		type MvCreatorContentTypeMetrics,
		type VDailyStreamAnalytics,
		type VCreatorOverallRankings,
		type VVideoPublicationDetails,
		type VRecentChannelActivity
	} from '$lib/services/analyticsService';
	import {
		materializedCreatorSummaryQueryOptions,
		platformPerformanceQueryOptions,
		platformCategoryStatsQueryOptions,
		monthlyRevenueQueryOptions,
		creatorContentTypeMetricsQueryOptions,
		creatorRankingsQueryOptions,
		dailyStreamAnalyticsQueryOptions,
		videoPublicationDetailsQueryOptions,
		recentActivityQueryOptions
	} from '$lib/query';
	import DataTable from '$lib/components/ui/DataTable.svelte';
	import type { Column } from '$lib/types/ui';
	import Button from '$lib/components/ui/Button.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import {
		FilterDrawer,
		FilterTriggerButton,
		FilterSection,
		DateRangeFilter,
		PlatformFilter,
		RangeFilter,
		type ViewsFilterState
	} from '$lib/components/filters';
	import type { PlatformType } from '$lib/supabase/database.types';
	import {
		Database,
		Layers,
		Zap,
		RefreshCw,
		Download,
		Info,
		CheckCircle2,
		Radio,
		Video,
		Trophy,
		Calendar,
		Sparkles,
		Eye,
		Activity,
		Table,
		SlidersHorizontal
	} from 'lucide-svelte';

	const queryClient = useQueryClient();

	type ViewTab =
		| 'mv_creator_performance'
		| 'mv_platform_performance'
		| 'mv_platform_category'
		| 'mv_monthly_revenue'
		| 'mv_content_type'
		| 'v_creator_rankings'
		| 'v_daily_stream'
		| 'v_video_details'
		| 'v_recent_activity';

	// Sincronización bidireccional con URL (?tab=...)
	let urlTab = $derived(page.url.searchParams.get('tab') as ViewTab | null);
	let activeTab = $derived<ViewTab>(urlTab || 'mv_creator_performance');

	const VIEW_METADATA: Record<ViewTab, { title: string; subtitle: string; icon: any; group: string }> = {
		mv_creator_performance: {
			title: 'Rendimiento y Métricas por Creador',
			subtitle: 'Consolidación de horas en directo, media de concurrencia (CCV) y métricas de publicaciones por cada talento.',
			icon: Zap,
			group: 'Vistas Materializadas'
		},
		mv_platform_performance: {
			title: 'Rendimiento Comparativo de Plataformas',
			subtitle: 'Comparativa acumulada por red social evaluando emisiones en vivo vs. publicaciones de video.',
			icon: Layers,
			group: 'Vistas Materializadas'
		},
		mv_platform_category: {
			title: 'Estadísticas por Categoría y Juego',
			subtitle: 'Desglose multidimensional de sesiones, horas transmitidas y retención de audiencia por temática.',
			icon: Radio,
			group: 'Vistas Materializadas'
		},
		mv_monthly_revenue: {
			title: 'Evolución Mensual de Streams y Videos',
			subtitle: 'Rollup temporal mensual con horas de directo, CCV promedio y rendimiento financiero consolidado.',
			icon: Calendar,
			group: 'Vistas Materializadas'
		},
		mv_content_type: {
			title: 'Métricas por Formato de Contenido',
			subtitle: 'Rendimiento diferenciado entre videos Standard, Shorts/Reels, VODs completos y Clips destacados.',
			icon: Video,
			group: 'Vistas Materializadas'
		},
		v_creator_rankings: {
			title: 'Leaderboard & Rankings del Roster',
			subtitle: 'Clasificación posicional con funciones de ventana por ingresos combinados, CCV medio y horas de transmisión.',
			icon: Trophy,
			group: 'Consultas SQL'
		},
		v_daily_stream: {
			title: 'Analítica Diaria de Transmisiones',
			subtitle: 'Registro de métricas por día con horas emitidas, CCV promedio, nuevos seguidores y actividad en chat.',
			icon: Activity,
			group: 'Consultas SQL'
		},
		v_video_details: {
			title: 'Detalle de Videos & Rendimiento ROI',
			subtitle: 'Métricas unitarias por publicación con visualizaciones, likes, tasa de engagement y rentabilidad calculada.',
			icon: Eye,
			group: 'Consultas SQL'
		},
		v_recent_activity: {
			title: 'Timeline de Actividad Reciente',
			subtitle: 'Flujo cronológico consolidado de directos realizados, videos subidos y eventos del canal.',
			icon: Sparkles,
			group: 'Consultas SQL'
		}
	};

	let activeViewMeta = $derived(VIEW_METADATA[activeTab] || VIEW_METADATA.mv_creator_performance);

	function selectTab(tab: ViewTab) {
		goto(`/views?tab=${tab}`, { keepFocus: true, noScroll: true });
	}

	let isRefreshing = $state(false);
	let refreshMessage = $state<string | null>(null);
	let isFilterDrawerOpen = $state(false);

	// Estado centralizado de filtros para cada una de las 9 tablas
	let filters = $state<ViewsFilterState>({
		creatorPerf: {
			platforms: [],
			minStreams: null,
			minCombinedRevenue: null,
			minAvgCcv: null
		},
		platformPerf: {
			platforms: [],
			minTotalHours: null,
			minCombinedRevenue: null
		},
		platformCategory: {
			platforms: [],
			minSessions: null,
			minCcv: null,
			minRevenue: null,
			categories: []
		},
		monthlyRevenue: {
			dateRange: { preset: 'all' },
			minMonthlyRevenue: null,
			minStreamHours: null
		},
		contentType: {
			platforms: [],
			publicationTypes: [],
			minViews: null,
			minEngagementRate: null,
			minRevenue: null
		},
		creatorRankings: {
			platforms: [],
			topN: null,
			minAvgCcv: null
		},
		dailyStream: {
			dateRange: { preset: 'all' },
			platforms: [],
			minEarningsPerHour: null,
			minAvgCcv: null
		},
		videoDetails: {
			platforms: [],
			publicationTypes: [],
			categories: [],
			minRoiPercentage: null,
			minViews: null,
			minRevenue: null
		},
		recentActivity: {
			dateRange: { preset: 'all' },
			activityTypes: [],
			platforms: []
		}
	});

	// Conteo de filtros activos por tabla
	let activeFilterCount = $derived.by(() => {
		let count = 0;
		if (activeTab === 'mv_creator_performance') {
			const f = filters.creatorPerf;
			if (f.platforms.length > 0) count++;
			if (f.minStreams) count++;
			if (f.minCombinedRevenue) count++;
			if (f.minAvgCcv) count++;
		} else if (activeTab === 'mv_platform_performance') {
			const f = filters.platformPerf;
			if (f.platforms.length > 0) count++;
			if (f.minTotalHours) count++;
			if (f.minCombinedRevenue) count++;
		} else if (activeTab === 'mv_platform_category') {
			const f = filters.platformCategory;
			if (f.platforms.length > 0) count++;
			if (f.minSessions) count++;
			if (f.minCcv) count++;
			if (f.minRevenue) count++;
		} else if (activeTab === 'mv_monthly_revenue') {
			const f = filters.monthlyRevenue;
			if (f.dateRange.preset !== 'all') count++;
			if (f.minMonthlyRevenue) count++;
			if (f.minStreamHours) count++;
		} else if (activeTab === 'mv_content_type') {
			const f = filters.contentType;
			if (f.platforms.length > 0) count++;
			if (f.publicationTypes.length > 0) count++;
			if (f.minViews) count++;
			if (f.minEngagementRate) count++;
			if (f.minRevenue) count++;
		} else if (activeTab === 'v_creator_rankings') {
			const f = filters.creatorRankings;
			if (f.platforms.length > 0) count++;
			if (f.topN) count++;
			if (f.minAvgCcv) count++;
		} else if (activeTab === 'v_daily_stream') {
			const f = filters.dailyStream;
			if (f.dateRange.preset !== 'all') count++;
			if (f.platforms.length > 0) count++;
			if (f.minEarningsPerHour) count++;
			if (f.minAvgCcv) count++;
		} else if (activeTab === 'v_video_details') {
			const f = filters.videoDetails;
			if (f.platforms.length > 0) count++;
			if (f.publicationTypes.length > 0) count++;
			if (f.minRoiPercentage) count++;
			if (f.minViews) count++;
			if (f.minRevenue) count++;
		} else if (activeTab === 'v_recent_activity') {
			const f = filters.recentActivity;
			if (f.dateRange.preset !== 'all') count++;
			if (f.activityTypes.length > 0) count++;
			if (f.platforms.length > 0) count++;
		}
		return count;
	});

	function resetCurrentTabFilters() {
		if (activeTab === 'mv_creator_performance') {
			filters.creatorPerf = { platforms: [], minStreams: null, minCombinedRevenue: null, minAvgCcv: null };
		} else if (activeTab === 'mv_platform_performance') {
			filters.platformPerf = { platforms: [], minTotalHours: null, minCombinedRevenue: null };
		} else if (activeTab === 'mv_platform_category') {
			filters.platformCategory = { platforms: [], minSessions: null, minCcv: null, minRevenue: null, categories: [] };
		} else if (activeTab === 'mv_monthly_revenue') {
			filters.monthlyRevenue = { dateRange: { preset: 'all' }, minMonthlyRevenue: null, minStreamHours: null };
		} else if (activeTab === 'mv_content_type') {
			filters.contentType = { platforms: [], publicationTypes: [], minViews: null, minEngagementRate: null, minRevenue: null };
		} else if (activeTab === 'v_creator_rankings') {
			filters.creatorRankings = { platforms: [], topN: null, minAvgCcv: null };
		} else if (activeTab === 'v_daily_stream') {
			filters.dailyStream = { dateRange: { preset: 'all' }, platforms: [], minEarningsPerHour: null, minAvgCcv: null };
		} else if (activeTab === 'v_video_details') {
			filters.videoDetails = { platforms: [], publicationTypes: [], categories: [], minRoiPercentage: null, minViews: null, minRevenue: null };
		} else if (activeTab === 'v_recent_activity') {
			filters.recentActivity = { dateRange: { preset: 'all' }, activityTypes: [], platforms: [] };
		}
	}

	// Queries
	const mvCreatorPerfQuery = createQuery(() =>
		materializedCreatorSummaryQueryOptions(tenantStore.currentOrg?.id)
	);
	const mvPlatformPerfQuery = createQuery(() =>
		platformPerformanceQueryOptions(tenantStore.currentOrg?.id)
	);
	const mvCategoryQuery = createQuery(() =>
		platformCategoryStatsQueryOptions(tenantStore.currentOrg?.id)
	);
	const mvMonthlyQuery = createQuery(() =>
		monthlyRevenueQueryOptions(tenantStore.currentOrg?.id)
	);
	const mvContentTypeQuery = createQuery(() =>
		creatorContentTypeMetricsQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);
	const vRankingsQuery = createQuery(() =>
		creatorRankingsQueryOptions(tenantStore.currentOrg?.id)
	);
	const vDailyStreamQuery = createQuery(() =>
		dailyStreamAnalyticsQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);
	const vVideoDetailsQuery = createQuery(() =>
		videoPublicationDetailsQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);
	const vActivityQuery = createQuery(() =>
		recentActivityQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);

	// Raw Datasets from Supabase Queries (Aislados por Organización)
	let rawMvCreatorPerf = $derived(mvCreatorPerfQuery.data || []);
	let rawMvPlatformPerf = $derived(mvPlatformPerfQuery.data || []);
	let rawMvCategory = $derived(mvCategoryQuery.data || []);
	let rawMvMonthly = $derived(mvMonthlyQuery.data || []);
	let rawMvContentType = $derived(mvContentTypeQuery.data || []);
	let rawVRankings = $derived(vRankingsQuery.data || []);
	let rawVDailyStream = $derived(vDailyStreamQuery.data || []);
	let rawVVideoDetails = $derived(vVideoDetailsQuery.data || []);
	let rawVActivity = $derived(vActivityQuery.data || []);

	// FILTRADO REACTIVO POR CADA TABLA
	let filteredMvCreatorPerf = $derived.by(() => {
		const f = filters.creatorPerf;
		return rawMvCreatorPerf.filter((row) => {
			if (f.platforms.length > 0 && !f.platforms.includes(row.primary_platform)) return false;
			if (f.minStreams && row.total_streams < f.minStreams) return false;
			if (f.minCombinedRevenue && row.total_combined_revenue < f.minCombinedRevenue) return false;
			if (f.minAvgCcv && row.overall_avg_ccv < f.minAvgCcv) return false;
			return true;
		});
	});

	let filteredMvPlatformPerf = $derived.by(() => {
		const f = filters.platformPerf;
		return rawMvPlatformPerf.filter((row) => {
			if (f.platforms.length > 0 && !f.platforms.includes(row.platform)) return false;
			if (f.minTotalHours && row.total_stream_hours < f.minTotalHours) return false;
			if (f.minCombinedRevenue && row.total_combined_revenue < f.minCombinedRevenue) return false;
			return true;
		});
	});

	let filteredMvCategory = $derived.by(() => {
		const f = filters.platformCategory;
		return rawMvCategory.filter((row) => {
			if (f.platforms.length > 0 && !f.platforms.includes(row.platform)) return false;
			if (f.minSessions && row.session_count < f.minSessions) return false;
			if (f.minCcv && row.avg_ccv < f.minCcv) return false;
			if (f.minRevenue && row.total_revenue < f.minRevenue) return false;
			return true;
		});
	});

	let filteredMvMonthly = $derived.by(() => {
		const f = filters.monthlyRevenue;
		return rawMvMonthly.filter((row) => {
			if (f.minMonthlyRevenue && row.total_combined_revenue < f.minMonthlyRevenue) return false;
			if (f.minStreamHours && row.total_stream_hours < f.minStreamHours) return false;
			return true;
		});
	});

	let filteredMvContentType = $derived.by(() => {
		const f = filters.contentType;
		return rawMvContentType.filter((row) => {
			if (f.platforms.length > 0 && !f.platforms.includes(row.platform)) return false;
			if (f.publicationTypes.length > 0 && !f.publicationTypes.includes(row.publication_type)) return false;
			if (f.minViews && row.total_views < f.minViews) return false;
			if (f.minEngagementRate && row.avg_engagement_rate < f.minEngagementRate) return false;
			if (f.minRevenue && row.total_revenue < f.minRevenue) return false;
			return true;
		});
	});

	let filteredVRankings = $derived.by(() => {
		const f = filters.creatorRankings;
		let list = rawVRankings.filter((row) => {
			if (f.platforms.length > 0 && !f.platforms.includes(row.primary_platform)) return false;
			if (f.minAvgCcv && row.overall_avg_ccv < f.minAvgCcv) return false;
			return true;
		});
		if (f.topN && f.topN > 0) {
			list = list.slice(0, f.topN);
		}
		return list;
	});

	let filteredVDailyStream = $derived.by(() => {
		const f = filters.dailyStream;
		return rawVDailyStream.filter((row) => {
			if (f.platforms.length > 0 && !f.platforms.includes(row.platform)) return false;
			if (f.minEarningsPerHour && row.earnings_per_hour < f.minEarningsPerHour) return false;
			if (f.minAvgCcv && row.avg_ccv < f.minAvgCcv) return false;
			return true;
		});
	});

	let filteredVVideoDetails = $derived.by(() => {
		const f = filters.videoDetails;
		return rawVVideoDetails.filter((row) => {
			if (f.platforms.length > 0 && !f.platforms.includes(row.platform)) return false;
			if (f.publicationTypes.length > 0 && !f.publicationTypes.includes(row.publication_type)) return false;
			if (f.minRoiPercentage && (row.roi_percentage || 0) < f.minRoiPercentage) return false;
			if (f.minViews && row.views_count < f.minViews) return false;
			if (f.minRevenue && row.estimated_revenue < f.minRevenue) return false;
			return true;
		});
	});

	let filteredVActivity = $derived.by(() => {
		const f = filters.recentActivity;
		return rawVActivity.filter((row) => {
			if (f.activityTypes.length > 0 && !f.activityTypes.includes(row.activity_type as any)) return false;
			if (f.platforms.length > 0 && !f.platforms.includes(row.platform)) return false;
			return true;
		});
	});

	async function handleRefreshMaterializedViews() {
		isRefreshing = true;
		refreshMessage = null;
		try {
			const ok = await analyticsService.refreshMaterializedViews();
			if (ok) {
				refreshMessage = 'Vistas materializadas actualizadas exitosamente con REFRESH CONCURRENT.';
				await queryClient.invalidateQueries();
			} else {
				refreshMessage = 'Actualizadas vistas en modo local reactivo.';
			}
		} catch (e) {
			console.error(e);
			refreshMessage = 'Error al ejecutar el procedimiento almacenado de refresco.';
		} finally {
			isRefreshing = false;
			setTimeout(() => {
				refreshMessage = null;
			}, 4000);
		}
	}

	function exportCurrentViewToCsv() {
		let currentData: any[] = [];
		let filename = `${activeTab}_export.csv`;

		if (activeTab === 'mv_creator_performance') currentData = filteredMvCreatorPerf;
		else if (activeTab === 'mv_platform_performance') currentData = filteredMvPlatformPerf;
		else if (activeTab === 'mv_platform_category') currentData = filteredMvCategory;
		else if (activeTab === 'mv_monthly_revenue') currentData = filteredMvMonthly;
		else if (activeTab === 'mv_content_type') currentData = filteredMvContentType;
		else if (activeTab === 'v_creator_rankings') currentData = filteredVRankings;
		else if (activeTab === 'v_daily_stream') currentData = filteredVDailyStream;
		else if (activeTab === 'v_video_details') currentData = filteredVVideoDetails;
		else if (activeTab === 'v_recent_activity') currentData = filteredVActivity;

		if (!currentData || currentData.length === 0) return;

		const headers = Object.keys(currentData[0]);
		const csvRows = [
			headers.join(','),
			...currentData.map((row) =>
				headers
					.map((h) => {
						const val = row[h];
						if (val === null || val === undefined) return '""';
						return `"${String(val).replace(/"/g, '""')}"`;
					})
					.join(',')
			)
		];

		const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
		const url = URL.createObjectURL(blob);
		const link = document.createElement('a');
		link.setAttribute('href', url);
		link.setAttribute('download', filename);
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}

	// COLUMNAS DE TABLAS
	const mvCreatorPerfColumns: Column<MvCreatorPerformance>[] = [
		{ key: 'display_name', label: 'Creador', sortable: true },
		{ key: 'handle', label: 'Handle', isMono: true, sortable: true },
		{ key: 'primary_platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'total_streams', label: 'Streams', align: 'right', isMono: true, sortable: true },
		{ key: 'total_hours_streamed', label: 'Horas Live', align: 'right', isMono: true, sortable: true },
		{ key: 'overall_avg_ccv', label: 'Media CCV', align: 'right', isMono: true, sortable: true },
		{ key: 'max_peak_viewers', label: 'Pico CCV', align: 'right', isMono: true, sortable: true },
		{ key: 'total_stream_earnings', label: '$ Streams', align: 'right', isMono: true, sortable: true },
		{ key: 'total_videos', label: 'Videos', align: 'right', isMono: true, sortable: true },
		{ key: 'total_publications', label: 'Publicaciones', align: 'right', isMono: true, sortable: true },
		{ key: 'total_video_views', label: 'Vistas Video', align: 'right', isMono: true, sortable: true },
		{ key: 'total_video_earnings', label: '$ Videos', align: 'right', isMono: true, sortable: true },
		{ key: 'total_combined_revenue', label: '$ Total Combinado', align: 'right', isMono: true, sortable: true }
	];

	const mvPlatformPerfColumns: Column<MvPlatformPerformance>[] = [
		{ key: 'platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'total_creators', label: 'Creadores', align: 'right', isMono: true, sortable: true },
		{ key: 'total_streams', label: 'Total Streams', align: 'right', isMono: true, sortable: true },
		{ key: 'total_stream_hours', label: 'Horas Live', align: 'right', isMono: true, sortable: true },
		{ key: 'avg_ccv', label: 'Media CCV', align: 'right', isMono: true, sortable: true },
		{ key: 'max_peak_viewers', label: 'Pico Máx', align: 'right', isMono: true, sortable: true },
		{ key: 'stream_subs_revenue', label: 'Subs ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'stream_ad_revenue', label: 'Ads Live ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'total_stream_earnings', label: 'Ingresos Live ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'total_publications', label: 'Publicaciones Video', align: 'right', isMono: true, sortable: true },
		{ key: 'total_video_views', label: 'Vistas Video', align: 'right', isMono: true, sortable: true },
		{ key: 'avg_engagement_rate', label: 'Engage %', align: 'right', isMono: true, sortable: true },
		{ key: 'total_video_earnings', label: 'Ingresos Videos ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'total_combined_revenue', label: 'Total Ingresos ($)', align: 'right', isMono: true, sortable: true }
	];

	const mvCategoryColumns: Column<MvPlatformCategoryStats>[] = [
		{ key: 'category_name', label: 'Categoría / Juego', sortable: true },
		{ key: 'platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'session_count', label: 'Sesiones', align: 'right', isMono: true, sortable: true },
		{ key: 'total_hours', label: 'Horas Totales', align: 'right', isMono: true, sortable: true },
		{ key: 'avg_ccv', label: 'Media CCV', align: 'right', isMono: true, sortable: true },
		{ key: 'max_peak', label: 'Pico Máx', align: 'right', isMono: true, sortable: true },
		{ key: 'total_revenue', label: 'Ingresos Generados ($)', align: 'right', isMono: true, sortable: true }
	];

	const mvMonthlyColumns: Column<MvMonthlyRevenue>[] = [
		{ key: 'period_label', label: 'Periodo (YYYY-MM)', isMono: true, sortable: true },
		{ key: 'total_streams', label: 'Directos', align: 'right', isMono: true, sortable: true },
		{ key: 'total_stream_hours', label: 'Horas Live', align: 'right', isMono: true, sortable: true },
		{ key: 'avg_ccv', label: 'Avg CCV', align: 'right', isMono: true, sortable: true },
		{ key: 'peak_viewers', label: 'Pico Viewers', align: 'right', isMono: true, sortable: true },
		{ key: 'stream_subs_revenue', label: 'Subs ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'stream_ad_revenue', label: 'Ads ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'total_stream_earnings', label: 'Total Live ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'total_publications', label: 'Videos Pub.', align: 'right', isMono: true, sortable: true },
		{ key: 'total_video_views', label: 'Vistas Video', align: 'right', isMono: true, sortable: true },
		{ key: 'total_video_earnings', label: 'Total Videos ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'total_combined_revenue', label: 'Ingresos Mes ($)', align: 'right', isMono: true, sortable: true }
	];

	const mvContentTypeColumns: Column<MvCreatorContentTypeMetrics>[] = [
		{ key: 'creator_name', label: 'Creador', sortable: true },
		{ key: 'platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'publication_type', label: 'Formato Video', align: 'center', sortable: true },
		{ key: 'total_publications', label: 'Videos', align: 'right', isMono: true, sortable: true },
		{ key: 'total_views', label: 'Vistas Totales', align: 'right', isMono: true, sortable: true },
		{ key: 'avg_views_per_video', label: 'Media Vistas/Video', align: 'right', isMono: true, sortable: true },
		{ key: 'total_likes', label: 'Likes', align: 'right', isMono: true, sortable: true },
		{ key: 'total_comments', label: 'Comentarios', align: 'right', isMono: true, sortable: true },
		{ key: 'avg_engagement_rate', label: 'Engagement %', align: 'right', isMono: true, sortable: true },
		{ key: 'total_revenue', label: 'Ingresos ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'avg_revenue_per_video', label: 'Media $/Video', align: 'right', isMono: true, sortable: true }
	];

	const vRankingsColumns: Column<VCreatorOverallRankings>[] = [
		{ key: 'revenue_rank', label: 'Rank $', align: 'center', isMono: true, sortable: true },
		{ key: 'ccv_rank', label: 'Rank CCV', align: 'center', isMono: true, sortable: true },
		{ key: 'hours_rank', label: 'Rank Horas', align: 'center', isMono: true, sortable: true },
		{ key: 'display_name', label: 'Creador', sortable: true },
		{ key: 'primary_platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'total_combined_revenue', label: 'Ingresos Totales ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'total_stream_earnings', label: 'Ingresos Live ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'total_video_earnings', label: 'Ingresos Video ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'overall_avg_ccv', label: 'Media CCV', align: 'right', isMono: true, sortable: true },
		{ key: 'total_hours_streamed', label: 'Horas Live', align: 'right', isMono: true, sortable: true }
	];

	const vDailyStreamColumns: Column<VDailyStreamAnalytics>[] = [
		{ key: 'stream_date', label: 'Fecha (UTC)', isMono: true, sortable: true },
		{ key: 'creator_name', label: 'Creador', sortable: true },
		{ key: 'platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'session_count', label: 'Directos', align: 'right', isMono: true, sortable: true },
		{ key: 'total_hours_streamed', label: 'Horas Emitidas', align: 'right', isMono: true, sortable: true },
		{ key: 'avg_ccv', label: 'Media CCV', align: 'right', isMono: true, sortable: true },
		{ key: 'max_peak_viewers', label: 'Pico CCV', align: 'right', isMono: true, sortable: true },
		{ key: 'total_chat_messages', label: 'Mensajes Chat', align: 'right', isMono: true, sortable: true },
		{ key: 'total_new_followers', label: 'Followers +', align: 'right', isMono: true, sortable: true },
		{ key: 'total_earnings', label: 'Ingresos ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'earnings_per_hour', label: 'Rendimiento ($/h)', align: 'right', isMono: true, sortable: true }
	];

	const vVideoDetailsColumns: Column<VVideoPublicationDetails>[] = [
		{ key: 'video_title', label: 'Título Video Master', sortable: true },
		{ key: 'creator_name', label: 'Creador', sortable: true },
		{ key: 'platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'publication_type', label: 'Formato', align: 'center', sortable: true },
		{ key: 'duration_minutes', label: 'Minutos', align: 'right', isMono: true, sortable: true },
		{ key: 'production_cost', label: 'Costo ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'views_count', label: 'Vistas', align: 'right', isMono: true, sortable: true },
		{ key: 'likes_count', label: 'Likes', align: 'right', isMono: true, sortable: true },
		{ key: 'engagement_rate', label: 'Engage %', align: 'right', isMono: true, sortable: true },
		{ key: 'estimated_revenue', label: 'Ingresos ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'net_profit', label: 'Beneficio Neto ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'roi_percentage', label: 'ROI %', align: 'right', isMono: true, sortable: true },
		{ key: 'rpm_estimated', label: 'RPM ($/1k)', align: 'right', isMono: true, sortable: true }
	];

	const vActivityColumns: Column<VRecentChannelActivity>[] = [
		{ key: 'timestamp', label: 'Fecha / Hora (UTC)', isMono: true, sortable: true },
		{ key: 'activity_type', label: 'Tipo Evento', align: 'center', sortable: true },
		{ key: 'creator_name', label: 'Creador', sortable: true },
		{ key: 'platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'title', label: 'Título / Resumen', sortable: true },
		{ key: 'subtitle', label: 'Detalle / Categoría', sortable: true },
		{ key: 'primary_metric', label: 'Métrica Primaria', align: 'right', isMono: true, sortable: true },
		{ key: 'metric_unit', label: 'Unidad', align: 'center', sortable: true },
		{ key: 'monetary_value', label: 'Valor ($)', align: 'right', isMono: true, sortable: true }
	];
</script>

<svelte:head>
	<title>{activeViewMeta.title} | RRSS Creators Analyzer</title>
</svelte:head>

<div class="space-y-6">
	<!-- Individualized View Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<div class="flex items-center gap-2 text-xs text-indigo-400 font-mono mb-1">
				<span>{activeViewMeta.group}</span>
				<span>/</span>
				<span class="text-white font-semibold">{activeViewMeta.title}</span>
			</div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				{#if activeViewMeta.icon}
					{@const IconComponent = activeViewMeta.icon}
					<IconComponent class="text-indigo-400" size={24} />
				{/if}
				<span>{activeViewMeta.title}</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				{activeViewMeta.subtitle}
			</p>
		</div>

		<div class="flex items-center gap-2.5">
			<!-- Botón de Filtros Dedicados para la vista actual -->
			<FilterTriggerButton
				isOpen={isFilterDrawerOpen}
				activeCount={activeFilterCount}
				label="Filtros de Vista"
				size="sm"
				onclick={() => (isFilterDrawerOpen = !isFilterDrawerOpen)}
			/>

			<Button
				variant="secondary"
				size="sm"
				onclick={handleRefreshMaterializedViews}
				isLoading={isRefreshing}
			>
				<RefreshCw size={14} class={isRefreshing ? 'animate-spin' : ''} />
				<span>Refrescar Datos</span>
			</Button>

			<Button variant="outline" size="sm" onclick={exportCurrentViewToCsv}>
				<Download size={14} />
				<span>Exportar CSV</span>
			</Button>
		</div>
	</div>

	<!-- Feedback Notification -->
	{#if refreshMessage}
		<div class="flex items-center gap-2 rounded-xl border border-indigo-500/30 bg-indigo-950/40 p-3 text-xs text-indigo-200">
			<CheckCircle2 size={16} class="text-indigo-400 shrink-0" />
			<span>{refreshMessage}</span>
		</div>
	{/if}

	<!-- TABLA DE DATOS SEGÚN PESTAÑA ACTIVA -->
	{#if activeTab === 'mv_creator_performance'}
		<DataTable
			data={filteredMvCreatorPerf}
			columns={mvCreatorPerfColumns}
			searchPlaceholder="Buscar en mv_creator_performance_summary..."
			searchKeys={['display_name', 'handle', 'primary_platform']}
		/>
	{:else if activeTab === 'mv_platform_performance'}
		<DataTable
			data={filteredMvPlatformPerf}
			columns={mvPlatformPerfColumns}
			searchPlaceholder="Buscar en mv_platform_performance_summary..."
			searchKeys={['platform']}
		/>
	{:else if activeTab === 'mv_platform_category'}
		<DataTable
			data={filteredMvCategory}
			columns={mvCategoryColumns}
			searchPlaceholder="Buscar en mv_platform_category_stats..."
			searchKeys={['category_name', 'platform']}
		/>
	{:else if activeTab === 'mv_monthly_revenue'}
		<DataTable
			data={filteredMvMonthly}
			columns={mvMonthlyColumns}
			searchPlaceholder="Buscar por periodo..."
			searchKeys={['period_label']}
		/>
	{:else if activeTab === 'mv_content_type'}
		<DataTable
			data={filteredMvContentType}
			columns={mvContentTypeColumns}
			searchPlaceholder="Buscar por formato o creador..."
			searchKeys={['creator_name', 'creator_handle', 'publication_type', 'platform']}
		/>
	{:else if activeTab === 'v_creator_rankings'}
		<DataTable
			data={filteredVRankings}
			columns={vRankingsColumns}
			searchPlaceholder="Buscar creador en leaderboard..."
			searchKeys={['display_name', 'handle', 'primary_platform']}
		/>
	{:else if activeTab === 'v_daily_stream'}
		<DataTable
			data={filteredVDailyStream}
			columns={vDailyStreamColumns}
			searchPlaceholder="Buscar por fecha o creador..."
			searchKeys={['stream_date', 'creator_name', 'creator_handle', 'platform']}
		/>
	{:else if activeTab === 'v_video_details'}
		<DataTable
			data={filteredVVideoDetails}
			columns={vVideoDetailsColumns}
			searchPlaceholder="Buscar video por título o creador..."
			searchKeys={['video_title', 'creator_name', 'category', 'platform']}
		/>
	{:else}
		<DataTable
			data={filteredVActivity}
			columns={vActivityColumns}
			searchPlaceholder="Buscar actividad..."
			searchKeys={['title', 'creator_name', 'activity_type', 'platform']}
		/>
	{/if}
</div>

<!-- DRAWER DE FILTROS ESPECÍFICOS POR TABLA -->
<FilterDrawer
	isOpen={isFilterDrawerOpen}
	position="right"
	title={`Filtros: ${activeTab}`}
	activeCount={activeFilterCount}
	onClose={() => (isFilterDrawerOpen = false)}
	onReset={resetCurrentTabFilters}
>
	{#if activeTab === 'mv_creator_performance'}
		<FilterSection title="Plataformas Primarias" defaultOpen={true}>
			<PlatformFilter bind:selected={filters.creatorPerf.platforms} />
		</FilterSection>

		<FilterSection title="Métricas del Creador" defaultOpen={true}>
			<div class="space-y-4">
				<RangeFilter
					label="Directos Mínimos"
					unit="streams"
					step={1}
					bind:min={filters.creatorPerf.minStreams}
				/>
				<RangeFilter
					label="Ingresos Totales Mínimos"
					unit="$"
					step={100}
					bind:min={filters.creatorPerf.minCombinedRevenue}
				/>
				<RangeFilter
					label="Media CCV Mínima"
					unit="ccv"
					step={1000}
					bind:min={filters.creatorPerf.minAvgCcv}
				/>
			</div>
		</FilterSection>
	{:else if activeTab === 'mv_platform_performance'}
		<FilterSection title="Plataformas" defaultOpen={true}>
			<PlatformFilter bind:selected={filters.platformPerf.platforms} />
		</FilterSection>

		<FilterSection title="Umbrales de Rendimiento" defaultOpen={true}>
			<div class="space-y-4">
				<RangeFilter
					label="Horas Transmitidas Mínimas"
					unit="hrs"
					step={5}
					bind:min={filters.platformPerf.minTotalHours}
				/>
				<RangeFilter
					label="Ingresos Totales Mínimos"
					unit="$"
					step={500}
					bind:min={filters.platformPerf.minCombinedRevenue}
				/>
			</div>
		</FilterSection>
	{:else if activeTab === 'mv_platform_category'}
		<FilterSection title="Plataformas" defaultOpen={true}>
			<PlatformFilter bind:selected={filters.platformCategory.platforms} />
		</FilterSection>

		<FilterSection title="Métricas de Categoría" defaultOpen={true}>
			<div class="space-y-4">
				<RangeFilter
					label="Sesiones Mínimas"
					unit="sesiones"
					step={1}
					bind:min={filters.platformCategory.minSessions}
				/>
				<RangeFilter
					label="Media CCV Mínima"
					unit="ccv"
					step={500}
					bind:min={filters.platformCategory.minCcv}
				/>
				<RangeFilter
					label="Ingresos Mínimos"
					unit="$"
					step={100}
					bind:min={filters.platformCategory.minRevenue}
				/>
			</div>
		</FilterSection>
	{:else if activeTab === 'mv_monthly_revenue'}
		<FilterSection title="Umbrales Mensuales" defaultOpen={true}>
			<div class="space-y-4">
				<RangeFilter
					label="Ingresos Mensuales Mínimos"
					unit="$"
					step={1000}
					bind:min={filters.monthlyRevenue.minMonthlyRevenue}
				/>
				<RangeFilter
					label="Horas Live Mínimas"
					unit="hrs"
					step={5}
					bind:min={filters.monthlyRevenue.minStreamHours}
				/>
			</div>
		</FilterSection>
	{:else if activeTab === 'mv_content_type'}
		<FilterSection title="Plataformas" defaultOpen={true}>
			<PlatformFilter bind:selected={filters.contentType.platforms} />
		</FilterSection>

		<FilterSection title="Métricas de Video" defaultOpen={true}>
			<div class="space-y-4">
				<RangeFilter
					label="Visualizaciones Mínimas"
					unit="vistas"
					step={50000}
					bind:min={filters.contentType.minViews}
				/>
				<RangeFilter
					label="Tasa de Engagement Mínima"
					unit="%"
					step={1}
					bind:min={filters.contentType.minEngagementRate}
				/>
				<RangeFilter
					label="Ingresos Mínimos"
					unit="$"
					step={100}
					bind:min={filters.contentType.minRevenue}
				/>
			</div>
		</FilterSection>
	{:else if activeTab === 'v_creator_rankings'}
		<FilterSection title="Plataformas" defaultOpen={true}>
			<PlatformFilter bind:selected={filters.creatorRankings.platforms} />
		</FilterSection>

		<FilterSection title="Filtros de Ranking" defaultOpen={true}>
			<div class="space-y-4">
				<RangeFilter
					label="Mostrar Top N"
					unit="creadores"
					step={1}
					bind:min={filters.creatorRankings.topN}
				/>
				<RangeFilter
					label="Media CCV Mínima"
					unit="ccv"
					step={5000}
					bind:min={filters.creatorRankings.minAvgCcv}
				/>
			</div>
		</FilterSection>
	{:else if activeTab === 'v_daily_stream'}
		<FilterSection title="Plataformas" defaultOpen={true}>
			<PlatformFilter bind:selected={filters.dailyStream.platforms} />
		</FilterSection>

		<FilterSection title="Eficiencia de Emisión" defaultOpen={true}>
			<div class="space-y-4">
				<RangeFilter
					label="Rendimiento Mínimo ($/Hora)"
					unit="$/h"
					step={50}
					bind:min={filters.dailyStream.minEarningsPerHour}
				/>
				<RangeFilter
					label="Media CCV Mínima"
					unit="ccv"
					step={1000}
					bind:min={filters.dailyStream.minAvgCcv}
				/>
			</div>
		</FilterSection>
	{:else if activeTab === 'v_video_details'}
		<FilterSection title="Plataformas" defaultOpen={true}>
			<PlatformFilter bind:selected={filters.videoDetails.platforms} />
		</FilterSection>

		<FilterSection title="Métricas Financieras & ROI" defaultOpen={true}>
			<div class="space-y-4">
				<RangeFilter
					label="ROI Mínimo (%)"
					unit="%"
					step={50}
					bind:min={filters.videoDetails.minRoiPercentage}
				/>
				<RangeFilter
					label="Vistas Mínimas"
					unit="vistas"
					step={100000}
					bind:min={filters.videoDetails.minViews}
				/>
				<RangeFilter
					label="Ingresos Mínimos"
					unit="$"
					step={200}
					bind:min={filters.videoDetails.minRevenue}
				/>
			</div>
		</FilterSection>
	{:else}
		<FilterSection title="Plataformas" defaultOpen={true}>
			<PlatformFilter bind:selected={filters.recentActivity.platforms} />
		</FilterSection>
	{/if}
</FilterDrawer>
