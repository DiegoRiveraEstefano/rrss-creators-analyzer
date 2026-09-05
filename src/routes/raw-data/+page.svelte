<script lang="ts">
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import { analyticsService, type StreamingSession } from '$lib/services/analyticsService';
	import {
		videoService,
		type Video,
		type VideoPublication,
		type VideoRelation
	} from '$lib/services/videoService';
	import { importService, type ImportBatch } from '$lib/services/importService';
	import { supabase } from '$lib/supabase/client';
	import DataTable from '$lib/components/ui/DataTable.svelte';
	import type { Column } from '$lib/types/ui';
	import Button from '$lib/components/ui/Button.svelte';
	import {
		Database,
		Radio,
		Video as VideoIcon,
		FileSpreadsheet,
		RefreshCw,
		Layers,
		Link2
	} from 'lucide-svelte';

	import {
		FilterDrawer,
		FilterTriggerButton,
		FilterSection,
		DateRangeFilter,
		PlatformFilter,
		RangeFilter,
		type RawDataTableFilterState
	} from '$lib/components/filters';

	let activeTable = $state<'sessions' | 'videos' | 'publications' | 'relations' | 'batches'>(
		'sessions'
	);
	let sessions = $state<StreamingSession[]>([]);
	let masterVideos = $state<Video[]>([]);
	let publications = $state<VideoPublication[]>([]);
	let relations = $state<VideoRelation[]>([]);
	let batches = $state<ImportBatch[]>([]);
	let isLoading = $state(true);
	let isFilterOpen = $state(false);

	let filters = $state<RawDataTableFilterState>({
		dateRange: { preset: 'all' },
		platforms: [],
		minDurationMinutes: null,
		minEarnings: null,
		minCcv: null
	});

	let activeFilterCount = $derived.by(() => {
		let count = 0;
		if (filters.dateRange.preset !== 'all') count++;
		if (filters.platforms.length > 0) count++;
		if (filters.minCcv != null && filters.minCcv > 0) count++;
		if (filters.minEarnings != null && filters.minEarnings > 0) count++;
		if (filters.minDurationMinutes != null && filters.minDurationMinutes > 0) count++;
		return count;
	});

	function resetFilters() {
		filters = {
			dateRange: { preset: 'all' },
			platforms: [],
			minDurationMinutes: null,
			minEarnings: null,
			minCcv: null
		};
	}

	function matchesDateRange(dateStr?: string | null): boolean {
		if (!dateStr || filters.dateRange.preset === 'all') return true;
		const d = new Date(dateStr).getTime();
		const now = Date.now();
		if (filters.dateRange.preset === '7d') return d >= now - 7 * 86400000;
		if (filters.dateRange.preset === '30d') return d >= now - 30 * 86400000;
		if (filters.dateRange.preset === '90d') return d >= now - 90 * 86400000;
		if (filters.dateRange.preset === 'year') return d >= now - 365 * 86400000;
		if (filters.dateRange.preset === 'custom') {
			if (filters.dateRange.from && d < new Date(filters.dateRange.from).getTime()) return false;
			if (filters.dateRange.to && d > new Date(filters.dateRange.to).getTime() + 86400000) return false;
		}
		return true;
	}

	let filteredSessions = $derived.by(() => {
		return sessions.filter((s) => {
			if (filters.platforms.length > 0 && !filters.platforms.includes(s.platform as any)) {
				return false;
			}
			if (!matchesDateRange(s.streamed_at)) return false;
			if (filters.minCcv != null && (s.avg_ccv || 0) < filters.minCcv) return false;
			if (filters.minEarnings != null && (s.total_earnings || 0) < filters.minEarnings) return false;
			if (
				filters.minDurationMinutes != null &&
				(s.duration_seconds || 0) / 60 < filters.minDurationMinutes
			) {
				return false;
			}
			return true;
		});
	});

	let filteredMasterVideos = $derived.by(() => {
		return masterVideos.filter((v) => {
			if (!matchesDateRange(v.created_at)) return false;
			if (
				filters.minDurationMinutes != null &&
				(v.duration_seconds || 0) / 60 < filters.minDurationMinutes
			) {
				return false;
			}
			return true;
		});
	});

	let filteredPublications = $derived.by(() => {
		return publications.filter((p) => {
			if (filters.platforms.length > 0 && !filters.platforms.includes(p.platform as any)) {
				return false;
			}
			if (!matchesDateRange(p.published_at)) return false;
			if (filters.minEarnings != null && (p.estimated_revenue || 0) < filters.minEarnings) {
				return false;
			}
			return true;
		});
	});

	let filteredBatches = $derived.by(() => {
		return batches.filter((b) => {
			if (filters.platforms.length > 0 && !filters.platforms.includes(b.source_platform as any)) {
				return false;
			}
			if (!matchesDateRange(b.created_at)) return false;
			return true;
		});
	});

	async function loadRawData() {
		if (!tenantStore.currentOrg) return;
		isLoading = true;
		try {
			const orgId = tenantStore.currentOrg.id;

			const { data: rawVideos } = await supabase
				.from('videos')
				.select('*')
				.eq('organization_id', orgId)
				.order('created_at', { ascending: false });

			const [s, p, r, b] = await Promise.all([
				analyticsService.getSessions(orgId),
				videoService.getRawPublications(orgId, 200),
				videoService.getRawRelations(orgId, 200),
				importService.getImportBatches(orgId)
			]);

			sessions = s;
			masterVideos = rawVideos || [];
			publications = p;
			relations = r;
			batches = b;
		} catch (error) {
			console.error('Error loading raw data:', error);
		} finally {
			isLoading = false;
		}
	}

	$effect(() => {
		if (tenantStore.currentOrg) {
			loadRawData();
		}
	});

	// 1. Columnas Sesiones
	const sessionColumns: Column<StreamingSession>[] = [
		{ key: 'id', label: 'UUID', isMono: true, sortable: true },
		{ key: 'session_title', label: 'Título', sortable: true },
		{ key: 'game_or_category', label: 'Juego/Cat', sortable: true },
		{ key: 'platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'streamed_at', label: 'Fecha UTC', isMono: true, sortable: true },
		{ key: 'duration_seconds', label: 'Segundos', align: 'right', isMono: true, sortable: true },
		{ key: 'hours_streamed', label: 'Horas', align: 'right', isMono: true, sortable: true },
		{ key: 'avg_ccv', label: 'CCV', align: 'right', isMono: true, sortable: true },
		{ key: 'peak_viewers', label: 'Pico', align: 'right', isMono: true, sortable: true },
		{ key: 'ad_revenue', label: 'Ads ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'subs_revenue', label: 'Subs ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'total_earnings', label: 'Total ($)', align: 'right', isMono: true, sortable: true }
	];

	// 2. Columnas Videos Master
	const masterVideoColumns: Column<Video>[] = [
		{ key: 'id', label: 'UUID', isMono: true, sortable: true },
		{ key: 'title', label: 'Título Principal', sortable: true },
		{ key: 'internal_name', label: 'Nombre Interno', isMono: true, sortable: true },
		{ key: 'category', label: 'Categoría', sortable: true },
		{ key: 'duration_seconds', label: 'Duración (s)', align: 'right', isMono: true, sortable: true },
		{ key: 'production_cost', label: 'Costo ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'status', label: 'Estado', align: 'center', sortable: true },
		{ key: 'created_at', label: 'Creado UTC', isMono: true, sortable: true }
	];

	// 3. Columnas Publicaciones
	const publicationColumns: Column<VideoPublication>[] = [
		{ key: 'id', label: 'UUID', isMono: true, sortable: true },
		{ key: 'video_id', label: 'Video ID (FK)', isMono: true, sortable: true },
		{ key: 'platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'publication_type', label: 'Formato', align: 'center', sortable: true },
		{ key: 'published_at', label: 'Publicado UTC', isMono: true, sortable: true },
		{ key: 'views_count', label: 'Vistas', align: 'right', isMono: true, sortable: true },
		{ key: 'likes_count', label: 'Likes', align: 'right', isMono: true, sortable: true },
		{ key: 'comments_count', label: 'Comentarios', align: 'right', isMono: true, sortable: true },
		{ key: 'estimated_revenue', label: 'Ingresos ($)', align: 'right', isMono: true, sortable: true }
	];

	// 4. Columnas Relaciones
	const relationColumns: Column<VideoRelation>[] = [
		{ key: 'id', label: 'UUID', isMono: true, sortable: true },
		{ key: 'source_video_id', label: 'Video Origen (FK)', isMono: true, sortable: true },
		{ key: 'target_session_id', label: 'Live Session (FK)', isMono: true, sortable: true },
		{ key: 'target_video_id', label: 'Video Destino (FK)', isMono: true, sortable: true },
		{ key: 'relation_type', label: 'Tipo de Relación', align: 'center', sortable: true },
		{ key: 'description', label: 'Descripción / Notas', sortable: true },
		{ key: 'created_at', label: 'Fecha Vínculo', isMono: true, sortable: true }
	];

	// 5. Columnas Lotes
	const batchColumns: Column<ImportBatch>[] = [
		{ key: 'id', label: 'Batch ID', isMono: true, sortable: true },
		{ key: 'filename', label: 'Nombre Archivo', sortable: true },
		{ key: 'source_platform', label: 'Origen', align: 'center', sortable: true },
		{ key: 'status', label: 'Estado', align: 'center', sortable: true },
		{ key: 'total_rows', label: 'Total Filas', align: 'right', isMono: true, sortable: true },
		{ key: 'valid_rows', label: 'Filas Válidas', align: 'right', isMono: true, sortable: true },
		{ key: 'error_count', label: 'Errores', align: 'right', isMono: true, sortable: true },
		{ key: 'created_at', label: 'Fecha Ingesta', isMono: true, sortable: true }
	];
</script>

<svelte:head>
	<title>Explorador de Tablas Crudas | RRSS Creators Analyzer</title>
</svelte:head>

<div class="space-y-6">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<Database class="text-indigo-400" size={24} />
				<span>Explorador de Tablas y Datos Crudos</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				Inspección directa de las tablas normalizadas de PostgreSQL en Supabase sin transformaciones intermedias.
			</p>
		</div>

		<div class="flex items-center gap-2">
			<FilterTriggerButton
				activeCount={activeFilterCount}
				isOpen={isFilterOpen}
				onclick={() => (isFilterOpen = !isFilterOpen)}
			/>

			<Button variant="secondary" size="sm" onclick={loadRawData} isLoading={isLoading}>
				<RefreshCw size={14} />
				Recargar Datos
			</Button>
		</div>
	</div>

	<!-- Selector de Tabla Cruda -->
	<div class="flex flex-wrap items-center gap-2 border-b border-[#1F2937] pb-3">
		<button
			onclick={() => (activeTable = 'sessions')}
			class="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl transition-all {activeTable ===
			'sessions'
				? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 shadow-sm'
				: 'text-gray-400 hover:text-white hover:bg-gray-800'}"
		>
			<Radio size={14} />
			<span>streaming_sessions ({filteredSessions.length})</span>
		</button>

		<button
			onclick={() => (activeTable = 'videos')}
			class="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl transition-all {activeTable ===
			'videos'
				? 'bg-cyan-600/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
				: 'text-gray-400 hover:text-white hover:bg-gray-800'}"
		>
			<VideoIcon size={14} />
			<span>videos ({filteredMasterVideos.length})</span>
		</button>

		<button
			onclick={() => (activeTable = 'publications')}
			class="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl transition-all {activeTable ===
			'publications'
				? 'bg-emerald-600/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
				: 'text-gray-400 hover:text-white hover:bg-gray-800'}"
		>
			<Layers size={14} />
			<span>video_publications ({filteredPublications.length})</span>
		</button>

		<button
			onclick={() => (activeTable = 'relations')}
			class="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl transition-all {activeTable ===
			'relations'
				? 'bg-amber-600/20 text-amber-300 border border-amber-500/40 shadow-sm'
				: 'text-gray-400 hover:text-white hover:bg-gray-800'}"
		>
			<Link2 size={14} />
			<span>video_relations ({relations.length})</span>
		</button>

		<button
			onclick={() => (activeTable = 'batches')}
			class="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl transition-all {activeTable ===
			'batches'
				? 'bg-purple-600/20 text-purple-300 border border-purple-500/40 shadow-sm'
				: 'text-gray-400 hover:text-white hover:bg-gray-800'}"
		>
			<FileSpreadsheet size={14} />
			<span>import_batches ({filteredBatches.length})</span>
		</button>
	</div>

	<!-- Tabla Dinámica TanStack Table -->
	{#if activeTable === 'sessions'}
		<DataTable
			data={filteredSessions}
			columns={sessionColumns}
			searchPlaceholder="Buscar en streaming_sessions..."
			searchKeys={['session_title', 'game_or_category', 'platform']}
		/>
	{:else if activeTable === 'videos'}
		<DataTable
			data={filteredMasterVideos}
			columns={masterVideoColumns}
			searchPlaceholder="Buscar en videos master..."
			searchKeys={['title', 'category', 'internal_name', 'status']}
		/>
	{:else if activeTable === 'publications'}
		<DataTable
			data={filteredPublications}
			columns={publicationColumns}
			searchPlaceholder="Buscar en video_publications..."
			searchKeys={['platform', 'publication_type']}
		/>
	{:else if activeTable === 'relations'}
		<DataTable
			data={relations}
			columns={relationColumns}
			searchPlaceholder="Buscar en video_relations..."
			searchKeys={['relation_type', 'description']}
		/>
	{:else}
		<DataTable
			data={filteredBatches}
			columns={batchColumns}
			searchPlaceholder="Buscar en import_batches..."
			searchKeys={['filename', 'source_platform', 'status']}
		/>
	{/if}
</div>

<!-- Drawer de Filtros (Derecha) -->
<FilterDrawer
	isOpen={isFilterOpen}
	title="Filtros de Tablas Crudas"
	position="right"
	activeCount={activeFilterCount}
	onClose={() => (isFilterOpen = false)}
	onReset={resetFilters}
>
	<!-- Rango Temporal -->
	<FilterSection title="Rango de Fechas" defaultOpen={true}>
		<DateRangeFilter bind:value={filters.dateRange} />
	</FilterSection>

	<!-- Plataformas -->
	<FilterSection title="Plataformas de Origen" defaultOpen={true}>
		<PlatformFilter bind:selected={filters.platforms} />
	</FilterSection>

	<!-- Audiencia y Finanzas (Streaming Sessions) -->
	<FilterSection title="Métricas de Transmisión" defaultOpen={true}>
		<div class="space-y-4">
			<RangeFilter
				label="Audiencia Promedio (Avg CCV)"
				unit="ccv"
				step={50}
				bind:min={filters.minCcv}
			/>

			<RangeFilter
				label="Ingresos Mínimos"
				unit="$"
				step={10}
				bind:min={filters.minEarnings}
			/>

			<RangeFilter
				label="Duración Mínima"
				unit="min"
				step={15}
				bind:min={filters.minDurationMinutes}
			/>
		</div>
	</FilterSection>
</FilterDrawer>
