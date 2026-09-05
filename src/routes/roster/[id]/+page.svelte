<script lang="ts">
	import { page } from '$app/state';
	import { createQuery, useQueryClient } from '@tanstack/svelte-query';
	import { creatorDetailQueryOptions, creatorsQueryKeys } from '$lib/query/creators';
	import { sessionsQueryOptions, sessionsQueryKeys } from '$lib/query/sessions';
	import { videosQueryOptions, videosQueryKeys } from '$lib/query/videos';
	import { analyticsSummaryQueryOptions, analyticsQueryKeys } from '$lib/query/analytics';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import type { StreamingSession } from '$lib/services/analyticsService';
	import type { VideoWithDetails } from '$lib/services/videoService';
	import { formatCurrency, formatNumber, formatDuration, formatDate, formatDateTime } from '$lib/utils/formatters';
	import StatCard from '$lib/components/ui/StatCard.svelte';
	import DataTable from '$lib/components/ui/DataTable.svelte';
	import type { Column } from '$lib/types/ui';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import EditCreatorModal from '$lib/components/creators/EditCreatorModal.svelte';
	import EditLiveModal from '$lib/components/creators/EditLiveModal.svelte';
	import EditVideoModal from '$lib/components/creators/EditVideoModal.svelte';
	import AddSessionModal from '$lib/components/creators/AddSessionModal.svelte';
	import AddVideoModal from '$lib/components/creators/AddVideoModal.svelte';
	import {
		User,
		Radio,
		Video,
		DollarSign,
		Clock,
		Users,
		TrendingUp,
		Plus,
		Edit,
		Edit3,
		ExternalLink,
		ArrowLeft,
		BarChart3,
		Tv
	} from 'lucide-svelte';

	const queryClient = useQueryClient();

	let creatorId = $derived(page.params.id);

	const creatorQuery = createQuery(() => creatorDetailQueryOptions(creatorId));
	const sessionsQuery = createQuery(() => sessionsQueryOptions(tenantStore.currentOrg?.id, creatorId));
	const videosQuery = createQuery(() => videosQueryOptions(tenantStore.currentOrg?.id, creatorId));
	const summaryQuery = createQuery(() => analyticsSummaryQueryOptions(tenantStore.currentOrg?.id, creatorId));

	let creator = $derived(creatorQuery.data ?? null);
	let sessions = $derived(sessionsQuery.data ?? []);
	let videos = $derived(videosQuery.data ?? []);
	let summary = $derived(
		summaryQuery.data ?? {
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

	let isLoading = $derived(creatorQuery.isLoading);
	let isEditModalOpen = $state(false);
	let isAddSessionModalOpen = $state(false);
	let isAddVideoModalOpen = $state(false);
	let isEditLiveModalOpen = $state(false);
	let isEditVideoModalOpen = $state(false);
	let editingSession = $state<StreamingSession | null>(null);
	let editingVideo = $state<VideoWithDetails | null>(null);
	let activeTab = $state<'sessions' | 'videos'>('sessions');

	function handleInvalidateAll() {
		queryClient.invalidateQueries({ queryKey: creatorsQueryKeys.all });
		queryClient.invalidateQueries({ queryKey: sessionsQueryKeys.all });
		queryClient.invalidateQueries({ queryKey: videosQueryKeys.all });
		queryClient.invalidateQueries({ queryKey: analyticsQueryKeys.all });
		tenantStore.loadCreators();
	}

	function openEditSession(sessionItem: StreamingSession) {
		editingSession = sessionItem;
		isEditLiveModalOpen = true;
	}

	function openEditVideo(videoItem: VideoWithDetails) {
		editingVideo = videoItem;
		isEditVideoModalOpen = true;
	}

	// Columnas para Sesiones de Streaming
	const sessionColumns: Column<StreamingSession>[] = [
		{ key: 'session_title', label: 'Título de Emisión', sortable: true },
		{ key: 'game_or_category', label: 'Categoría', sortable: true },
		{ key: 'platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'hours_streamed', label: 'Duración', align: 'right', isMono: true, sortable: true },
		{ key: 'avg_ccv', label: 'Media CCV', align: 'right', isMono: true, sortable: true },
		{ key: 'peak_viewers', label: 'Pico Viewers', align: 'right', isMono: true, sortable: true },
		{ key: 'total_earnings', label: 'Ingresos ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'id', label: 'Acciones', align: 'center', sortable: false }
	];

	// Columnas para Videos
	const videoColumns: Column<VideoWithDetails>[] = [
		{ key: 'title', label: 'Título del Video', sortable: true },
		{ key: 'category', label: 'Categoría', sortable: true },
		{ key: 'duration_seconds', label: 'Duración (s)', align: 'right', isMono: true, sortable: true },
		{ key: 'total_views', label: 'Visualizaciones', align: 'right', isMono: true, sortable: true },
		{ key: 'total_likes', label: 'Likes', align: 'right', isMono: true, sortable: true },
		{ key: 'total_revenue', label: 'Ingresos Est. ($)', align: 'right', isMono: true, sortable: true },
		{ key: 'id', label: 'Acciones', align: 'center', sortable: false }
	];
</script>

<svelte:head>
	<title>{creator?.display_name || 'Creador'} | Detalle de Roster</title>
</svelte:head>

<div class="space-y-6">
	<!-- Top Breadcrumb & Navigation -->
	<div class="flex items-center justify-between">
		<a href="/roster" class="inline-flex items-center gap-1.5 text-xs text-gray-400 hover:text-white transition-colors">
			<ArrowLeft size={14} />
			<span>Volver al Roster</span>
		</a>

		<a href="/roster/{creatorId}/dashboard">
			<Button variant="cyan" size="sm">
				<BarChart3 size={15} />
				Ver Dashboard Analítico de {creator?.display_name || 'Creador'}
			</Button>
		</a>
	</div>

	{#if isLoading && !creator}
		<div class="py-16 text-center text-xs text-gray-400">
			<div class="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent mx-auto mb-3"></div>
			Cargando perfil del creador...
		</div>
	{:else if creator}
		<!-- Header Card con Perfil del Creador -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-6 shadow-xl flex flex-col md:flex-row md:items-start justify-between gap-6">
			<div class="flex items-start gap-5">
				<div class="relative">
					<img
						src={creator.avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80'}
						alt={creator.display_name}
						class="h-20 w-20 rounded-2xl object-cover ring-2 ring-indigo-500/40 shadow-lg"
					/>
				</div>

				<div class="space-y-1.5">
					<div class="flex flex-wrap items-center gap-2.5">
						<h1 class="text-xl font-bold text-white">{creator.display_name}</h1>
						<span class="text-xs text-gray-400 font-mono">@{creator.handle}</span>
						<Badge
							variant={creator.primary_platform === 'twitch' ? 'purple' : creator.primary_platform === 'youtube' ? 'danger' : 'cyan'}
							size="sm"
							class="capitalize"
						>
							{creator.primary_platform}
						</Badge>
						<Badge variant={creator.status === 'active' ? 'success' : 'neutral'} size="sm">
							{creator.status === 'active' ? 'Activo' : 'Inactivo'}
						</Badge>
					</div>

					{#if creator.bio}
						<p class="text-xs text-gray-300 max-w-xl">{creator.bio}</p>
					{/if}

					<!-- Canales vinculados -->
					{#if creator.channels && creator.channels.length > 0}
						<div class="flex flex-wrap items-center gap-2 pt-1">
							{#each creator.channels as ch}
								<a
									href={ch.channel_url || '#'}
									target="_blank"
									rel="noopener noreferrer"
									class="inline-flex items-center gap-1.5 rounded-lg border border-[#2D3748] bg-[#090D16] px-2.5 py-1 text-[11px] text-gray-300 hover:text-white hover:border-indigo-500/50 transition-colors font-mono"
								>
									<Tv size={12} class="text-cyan-400" />
									<span>{ch.platform}: {ch.platform_channel_id}</span>
									<ExternalLink size={10} class="text-gray-400" />
								</a>
							{/each}
						</div>
					{/if}
				</div>
			</div>

			<!-- Botones de Acción -->
			<div class="flex flex-wrap items-center gap-2.5 shrink-0">
				<Button variant="secondary" size="sm" onclick={() => (isEditModalOpen = true)}>
					<Edit size={14} />
					Editar Creador
				</Button>

				<Button variant="primary" size="sm" onclick={() => (isAddSessionModalOpen = true)}>
					<Radio size={14} />
					Ingestar Sesión Live
				</Button>

				<Button variant="outline" size="sm" onclick={() => (isAddVideoModalOpen = true)}>
					<Video size={14} />
					Ingestar Video
				</Button>
			</div>
		</div>

		<!-- Row de KPIs del Creador -->
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
			<StatCard
				title="Ingresos Totales (Streams + Videos)"
				value={formatCurrency(summary.totalEarnings)}
				icon={DollarSign}
				iconColor="emerald"
			/>

			<StatCard
				title="Horas en Vivo"
				value={`${summary.totalHours}h`}
				icon={Clock}
				iconColor="indigo"
				subtitle={`${sessions.length} emisiones registradas`}
			/>

			<StatCard
				title="Media Concurrencia CCV"
				value={formatNumber(summary.avgCcv)}
				icon={Users}
				iconColor="cyan"
				subtitle={`Pico máximo: ${formatNumber(summary.peakViewers)}`}
			/>

			<StatCard
				title="Visualizaciones de Videos"
				value={formatNumber(summary.totalVideoViews || 0, true)}
				icon={Video}
				iconColor="purple"
				subtitle={`${videos.length} videos publicados`}
			/>
		</div>

		<!-- Pestañas de Tablas Relacionadas: Sesiones vs Videos -->
		<div class="space-y-4">
			<div class="flex items-center gap-3 border-b border-[#1F2937] pb-2">
				<button
					onclick={() => (activeTab = 'sessions')}
					class="flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors {activeTab === 'sessions'
						? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
						: 'text-gray-400 hover:text-white'}"
				>
					<Radio size={14} />
					<span>Sesiones de Streaming ({sessions.length})</span>
				</button>

				<button
					onclick={() => (activeTab = 'videos')}
					class="flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors {activeTab === 'videos'
						? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
						: 'text-gray-400 hover:text-white'}"
				>
					<Video size={14} />
					<span>Videos Subidos ({videos.length})</span>
				</button>
			</div>

			{#if activeTab === 'sessions'}
				<DataTable
					data={sessions}
					columns={[
						...sessionColumns.slice(0, 7),
						{
							...sessionColumns[7],
							render: sessionActionCell
						}
					]}
					searchPlaceholder="Buscar en transmisiones del creador..."
					searchKeys={['session_title', 'game_or_category']}
				/>
			{:else}
				<DataTable
					data={videos}
					columns={[
						...videoColumns.slice(0, 6),
						{
							...videoColumns[6],
							render: videoActionCell
						}
					]}
					searchPlaceholder="Buscar en videos del creador..."
					searchKeys={['title', 'category']}
				/>
			{/if}
		</div>

		{#snippet sessionActionCell({ row }: { row: StreamingSession })}
			<div class="flex items-center justify-center">
				<Button
					variant="secondary"
					size="sm"
					onclick={() => openEditSession(row)}
					class="h-7 px-2.5 text-xs text-indigo-300 hover:text-white"
					title="Editar sesión"
				>
					<Edit3 size={13} />
					<span>Editar</span>
				</Button>
			</div>
		{/snippet}

		{#snippet videoActionCell({ row }: { row: VideoWithDetails })}
			<div class="flex items-center justify-center">
				<Button
					variant="secondary"
					size="sm"
					onclick={() => openEditVideo(row)}
					class="h-7 px-2.5 text-xs text-indigo-300 hover:text-white"
					title="Editar video"
				>
					<Edit3 size={13} />
					<span>Editar</span>
				</Button>
			</div>
		{/snippet}

		<!-- Modales de Edición e Ingesta -->
		<EditCreatorModal
			isOpen={isEditModalOpen}
			{creator}
			onClose={() => (isEditModalOpen = false)}
			onUpdated={handleInvalidateAll}
		/>

		{#if tenantStore.currentOrg}
			<EditLiveModal
				isOpen={isEditLiveModalOpen}
				session={editingSession}
				onClose={() => {
					isEditLiveModalOpen = false;
					editingSession = null;
				}}
				onUpdated={handleInvalidateAll}
				onDeleted={handleInvalidateAll}
			/>

			<EditVideoModal
				isOpen={isEditVideoModalOpen}
				video={editingVideo}
				organizationId={tenantStore.currentOrg.id}
				onClose={() => {
					isEditVideoModalOpen = false;
					editingVideo = null;
				}}
				onUpdated={handleInvalidateAll}
				onDeleted={handleInvalidateAll}
			/>

			<AddSessionModal
				isOpen={isAddSessionModalOpen}
				organizationId={tenantStore.currentOrg.id}
				creatorId={creator.id}
				onClose={() => (isAddSessionModalOpen = false)}
				onAdded={handleInvalidateAll}
			/>

			<AddVideoModal
				isOpen={isAddVideoModalOpen}
				organizationId={tenantStore.currentOrg.id}
				creatorId={creator.id}
				onClose={() => (isAddVideoModalOpen = false)}
				onAdded={handleInvalidateAll}
			/>
		{/if}
	{/if}
</div>
