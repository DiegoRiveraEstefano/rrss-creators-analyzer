<script lang="ts">
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import { analyticsService, type StreamingSession } from '$lib/services/analyticsService';
	import { videoService, type PublishedVideo } from '$lib/services/videoService';
	import { importService, type ImportBatch } from '$lib/services/importService';
	import { formatCurrency, formatNumber, formatDate, formatDateTime } from '$lib/utils/formatters';
	import DataTable from '$lib/components/ui/DataTable.svelte';
	import type { Column } from '$lib/types/ui';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import {
		Database,
		Radio,
		Video,
		FileSpreadsheet,
		RefreshCw,
		Download
	} from 'lucide-svelte';

	let activeTable = $state<'sessions' | 'videos' | 'batches'>('sessions');
	let sessions = $state<StreamingSession[]>([]);
	let videos = $state<PublishedVideo[]>([]);
	let batches = $state<ImportBatch[]>([]);
	let isLoading = $state(true);

	async function loadRawData() {
		if (!tenantStore.currentOrg) return;
		isLoading = true;
		try {
			const orgId = tenantStore.currentOrg.id;
			const [s, v, b] = await Promise.all([
				analyticsService.getSessions(orgId),
				videoService.getVideosByOrganization(orgId, 200),
				importService.getImportBatches(orgId)
			]);

			sessions = s;
			videos = v;
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

	// Columnas para Sesiones de Streaming Crudas
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

	// Columnas para Videos Subidos Crudos
	const videoColumns: Column<PublishedVideo>[] = [
		{ key: 'id', label: 'UUID', isMono: true, sortable: true },
		{ key: 'title', label: 'Título del Video', sortable: true },
		{ key: 'platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'published_at', label: 'Publicado UTC', isMono: true, sortable: true },
		{ key: 'duration_seconds', label: 'Duración (s)', align: 'right', isMono: true, sortable: true },
		{ key: 'views_count', label: 'Views', align: 'right', isMono: true, sortable: true },
		{ key: 'likes_count', label: 'Likes', align: 'right', isMono: true, sortable: true },
		{ key: 'comments_count', label: 'Comments', align: 'right', isMono: true, sortable: true },
		{ key: 'estimated_revenue', label: 'Ingresos ($)', align: 'right', isMono: true, sortable: true }
	];

	// Columnas para Lotes de Importación
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
	<title>Explorador de Datos Crudos | RRSS Creators Analyzer</title>
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
				Inspección directa de las tablas de PostgreSQL en Supabase sin agregaciones intermedias.
			</p>
		</div>

		<Button variant="secondary" size="sm" onclick={loadRawData} isLoading={isLoading}>
			<RefreshCw size={14} />
			Recargar Datos
		</Button>
	</div>

	<!-- Selector de Tabla Cruda -->
	<div class="flex items-center gap-2 border-b border-[#1F2937] pb-3">
		<button
			onclick={() => (activeTable = 'sessions')}
			class="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl transition-all {activeTable === 'sessions'
				? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 shadow-sm shadow-indigo-500/10'
				: 'text-gray-400 hover:text-white hover:bg-gray-800'}"
		>
			<Radio size={14} />
			<span>streaming_sessions ({sessions.length})</span>
		</button>

		<button
			onclick={() => (activeTable = 'videos')}
			class="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl transition-all {activeTable === 'videos'
				? 'bg-cyan-600/20 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/10'
				: 'text-gray-400 hover:text-white hover:bg-gray-800'}"
		>
			<Video size={14} />
			<span>published_videos ({videos.length})</span>
		</button>

		<button
			onclick={() => (activeTable = 'batches')}
			class="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl transition-all {activeTable === 'batches'
				? 'bg-purple-600/20 text-purple-300 border border-purple-500/40 shadow-sm shadow-purple-500/10'
				: 'text-gray-400 hover:text-white hover:bg-gray-800'}"
		>
			<FileSpreadsheet size={14} />
			<span>import_batches ({batches.length})</span>
		</button>
	</div>

	<!-- Tabla Dinámica -->
	{#if activeTable === 'sessions'}
		<DataTable
			data={sessions}
			columns={sessionColumns}
			searchPlaceholder="Buscar en streaming_sessions..."
			searchKeys={['session_title', 'game_or_category', 'platform']}
		/>
	{:else if activeTable === 'videos'}
		<DataTable
			data={videos}
			columns={videoColumns}
			searchPlaceholder="Buscar en published_videos..."
			searchKeys={['title', 'platform']}
		/>
	{:else}
		<DataTable
			data={batches}
			columns={batchColumns}
			searchPlaceholder="Buscar en import_batches..."
			searchKeys={['filename', 'source_platform', 'status']}
		/>
	{/if}
</div>
