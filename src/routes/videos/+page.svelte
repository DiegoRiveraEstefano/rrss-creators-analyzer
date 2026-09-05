<script lang="ts">
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import { videoService, type VideoWithDetails } from '$lib/services/videoService';
	import { formatCurrency, formatNumber, formatDuration } from '$lib/utils/formatters';
	import StatCard from '$lib/components/ui/StatCard.svelte';
	import DataTable from '$lib/components/ui/DataTable.svelte';
	import type { Column } from '$lib/types/ui';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import AddVideoModal from '$lib/components/creators/AddVideoModal.svelte';
	import EditVideoModal from '$lib/components/creators/EditVideoModal.svelte';
	import {
		Video,
		Plus,
		DollarSign,
		Eye,
		ThumbsUp,
		Radio,
		Layers,
		Sparkles,
		Edit3,
		ExternalLink
	} from 'lucide-svelte';

	import { createQuery, useQueryClient } from '@tanstack/svelte-query';
	import { videosQueryOptions, videosQueryKeys } from '$lib/query/videos';
	import {
		FilterDrawer,
		FilterTriggerButton,
		FilterSection,
		PlatformFilter,
		RangeFilter,
		MultiSelectFilter,
		CreatorFilter,
		type VideoTableFilterState
	} from '$lib/components/filters';

	const queryClient = useQueryClient();

	const videosQuery = createQuery(() =>
		videosQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);

	let videos = $derived(videosQuery.data || []);
	let isLoading = $derived(videosQuery.isLoading);
	let isAddModalOpen = $state(false);
	let isEditModalOpen = $state(false);
	let editingVideo = $state<VideoWithDetails | null>(null);
	let isFilterOpen = $state(false);

	let filters = $state<VideoTableFilterState>({
		creatorIds: [],
		platforms: [],
		categories: [],
		minViews: null,
		minRevenue: null,
		onlyLiveDerived: false
	});

	let availableCategories = $derived.by(() => {
		const cats = new Set<string>();
		for (const v of videos) {
			if (v.category) cats.add(v.category);
		}
		return Array.from(cats).map((c) => ({ value: c, label: c }));
	});

	let activeFilterCount = $derived.by(() => {
		let count = 0;
		if (filters.creatorIds.length > 0) count++;
		if (filters.platforms.length > 0) count++;
		if (filters.categories.length > 0) count++;
		if (filters.minViews != null && filters.minViews > 0) count++;
		if (filters.minRevenue != null && filters.minRevenue > 0) count++;
		if (filters.onlyLiveDerived) count++;
		return count;
	});

	function resetFilters() {
		filters = {
			creatorIds: [],
			platforms: [],
			categories: [],
			minViews: null,
			minRevenue: null,
			onlyLiveDerived: false
		};
	}

	let filteredVideos = $derived.by(() => {
		return videos.filter((v) => {
			if (filters.creatorIds.length > 0 && !filters.creatorIds.includes(v.creator_id)) {
				return false;
			}

			if (filters.platforms.length > 0) {
				const hasMatchingPlatform = v.platforms?.some((p) =>
					filters.platforms.includes(p as any)
				);
				if (!hasMatchingPlatform) return false;
			}

			if (filters.categories.length > 0) {
				if (!v.category || !filters.categories.includes(v.category)) return false;
			}

			if (filters.minViews != null && (v.total_views || 0) < filters.minViews) {
				return false;
			}

			if (filters.minRevenue != null && (v.total_revenue || 0) < filters.minRevenue) {
				return false;
			}

			if (filters.onlyLiveDerived && !v.has_live_relation) {
				return false;
			}

			return true;
		});
	});

	function handleDataChanged() {
		queryClient.invalidateQueries({ queryKey: videosQueryKeys.all });
	}

	function openEditModal(videoItem: VideoWithDetails) {
		editingVideo = videoItem;
		isEditModalOpen = true;
	}

	let totalViews = $derived(filteredVideos.reduce((acc, v) => acc + (v.total_views || 0), 0));
	let totalRevenue = $derived(
		filteredVideos.reduce((acc, v) => acc + Number(v.total_revenue || 0), 0)
	);
	let totalLikes = $derived(filteredVideos.reduce((acc, v) => acc + (v.total_likes || 0), 0));
	let liveDerivedCount = $derived(filteredVideos.filter((v) => v.has_live_relation).length);

	const videoColumns: Column<VideoWithDetails>[] = [
		{
			key: 'title',
			label: 'Video & Multi-Publicación',
			sortable: true
		},
		{
			key: 'category',
			label: 'Categoría',
			sortable: true
		},
		{
			key: 'duration_seconds',
			label: 'Duración',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'total_views',
			label: 'Vistas Totales',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'total_likes',
			label: 'Likes',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'total_revenue',
			label: 'Ingresos Est. ($)',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'id',
			label: 'Acciones',
			align: 'center',
			sortable: false
		}
	];
</script>

{#snippet titleCell({ row }: { row: VideoWithDetails })}
	<div class="space-y-1 py-1">
		<div class="flex items-center gap-2">
			<span class="font-semibold text-white truncate max-w-sm">{row.title}</span>
			{#if row.has_live_relation}
				<Badge variant="cyan" size="sm">
					<Radio size={11} class="mr-1 inline" />
					Clip de Live
				</Badge>
			{/if}
		</div>
		<div class="flex items-center gap-2 text-[11px] text-gray-400">
			{#if row.internal_name}
				<span class="font-mono text-gray-500">{row.internal_name} •</span>
			{/if}
			<div class="flex items-center gap-1.5 flex-wrap">
				{#each row.publications as pub}
					<span
						class="px-1.5 py-0.5 rounded text-[10px] font-mono uppercase font-semibold {pub.platform === 'youtube'
							? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
							: pub.platform === 'tiktok'
								? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
								: pub.platform === 'twitch'
									? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
									: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'}"
						title="{pub.publication_type} - {formatNumber(pub.views_count || 0)} vistas"
					>
						{pub.platform} ({pub.publication_type})
					</span>
				{/each}
			</div>
		</div>
	</div>
{/snippet}

{#snippet categoryCell({ row }: { row: VideoWithDetails })}
	<div>
		<span class="text-xs text-gray-300">{row.category || 'General'}</span>
		{#if row.tags && row.tags.length > 0}
			<div class="text-[10px] text-gray-500 truncate max-w-[120px]">
				#{row.tags.slice(0, 2).join(' #')}
			</div>
		{/if}
	</div>
{/snippet}

{#snippet durationCell({ row }: { row: VideoWithDetails })}
	<span class="font-mono text-xs text-gray-300">
		{formatDuration(row.duration_seconds)}
	</span>
{/snippet}

{#snippet viewsCell({ row }: { row: VideoWithDetails })}
	<span class="font-mono text-xs font-semibold text-white">
		{formatNumber(row.total_views, true)}
	</span>
{/snippet}

{#snippet likesCell({ row }: { row: VideoWithDetails })}
	<span class="font-mono text-xs text-gray-300">
		{formatNumber(row.total_likes, true)}
	</span>
{/snippet}

{#snippet revenueCell({ row }: { row: VideoWithDetails })}
	<span class="font-mono text-xs font-semibold text-emerald-400">
		{formatCurrency(row.total_revenue)}
	</span>
{/snippet}

{#snippet actionsCell({ row }: { row: VideoWithDetails })}
	<div class="flex items-center justify-center gap-1.5">
		<Button
			variant="secondary"
			size="sm"
			onclick={() => openEditModal(row)}
			class="h-7 px-2.5 text-xs text-indigo-300 hover:text-white"
			title="Editar video y publicaciones"
		>
			<Edit3 size={13} />
			<span>Editar</span>
		</Button>
	</div>
{/snippet}

<svelte:head>
	<title>Catálogo de Videos | RRSS Creators Analyzer</title>
</svelte:head>

<div class="space-y-6">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<Video class="text-cyan-400" size={24} />
				<span>Catálogo de Videos & Multi-Publicación</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				Estructura en 3 capas: Video Master, Publicaciones multi-plataforma (YouTube, TikTok) y Trazabilidad con directos.
			</p>
		</div>

		<div class="flex items-center gap-2">
			<FilterTriggerButton
				activeCount={activeFilterCount}
				isOpen={isFilterOpen}
				onclick={() => (isFilterOpen = !isFilterOpen)}
			/>

			<Button variant="primary" size="md" onclick={() => (isAddModalOpen = true)}>
				<Plus size={16} />
				Registrar Video
			</Button>
		</div>
	</div>

	<!-- KPIs -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<StatCard
			title="Total Visualizaciones"
			value={formatNumber(totalViews, true)}
			icon={Eye}
			iconColor="cyan"
			subtitle={`${filteredVideos.length} videos filtrados`}
		/>

		<StatCard
			title="Ingresos Estimados por Videos"
			value={formatCurrency(totalRevenue)}
			icon={DollarSign}
			iconColor="emerald"
		/>

		<StatCard
			title="Total Likes Acumulados"
			value={formatNumber(totalLikes, true)}
			icon={ThumbsUp}
			iconColor="purple"
		/>

		<StatCard
			title="Clips Derivados de Lives"
			value={liveDerivedCount}
			icon={Radio}
			iconColor="indigo"
			subtitle="Trazabilidad activa"
		/>
	</div>

	<!-- Tabla de Videos -->
	<div class="space-y-3">
		<div class="flex items-center justify-between">
			<h3 class="text-base font-semibold text-white flex items-center gap-2">
				<Layers size={18} class="text-indigo-400" />
				<span>Activos de Video & Multi-Publicación</span>
			</h3>
		</div>

		<DataTable
			data={filteredVideos}
			columns={[
				{ ...videoColumns[0], render: titleCell },
				{ ...videoColumns[1], render: categoryCell },
				{ ...videoColumns[2], render: durationCell },
				{ ...videoColumns[3], render: viewsCell },
				{ ...videoColumns[4], render: likesCell },
				{ ...videoColumns[5], render: revenueCell },
				{ ...videoColumns[6], render: actionsCell }
			]}
			searchPlaceholder="Buscar por título, categoría o tags..."
			searchKeys={['title', 'category', 'internal_name']}
		/>
	</div>

	<!-- Modal para Registrar Video -->
	{#if tenantStore.currentOrg}
		<AddVideoModal
			isOpen={isAddModalOpen}
			organizationId={tenantStore.currentOrg.id}
			creatorId={tenantStore.selectedCreatorId}
			onClose={() => (isAddModalOpen = false)}
			onAdded={handleDataChanged}
		/>

		<EditVideoModal
			isOpen={isEditModalOpen}
			video={editingVideo}
			organizationId={tenantStore.currentOrg.id}
			onClose={() => {
				isEditModalOpen = false;
				editingVideo = null;
			}}
			onUpdated={handleDataChanged}
			onDeleted={handleDataChanged}
		/>
	{/if}
</div>

<!-- Drawer de Filtros (Derecha) -->
<FilterDrawer
	isOpen={isFilterOpen}
	title="Filtros del Catálogo de Videos"
	position="right"
	activeCount={activeFilterCount}
	onClose={() => (isFilterOpen = false)}
	onReset={resetFilters}
>
	<!-- Creadores / Talentos -->
	<FilterSection title="Creadores / Talentos" defaultOpen={true}>
		<CreatorFilter bind:selected={filters.creatorIds} />
	</FilterSection>

	<!-- Plataformas de Publicación -->
	<FilterSection title="Plataformas Publicadas" defaultOpen={true}>
		<PlatformFilter bind:selected={filters.platforms} />
	</FilterSection>

	<!-- Categorías -->
	{#if availableCategories.length > 0}
		<FilterSection title="Categorías" defaultOpen={true}>
			<MultiSelectFilter
				options={availableCategories}
				bind:selected={filters.categories}
				placeholder="Buscar categoría..."
			/>
		</FilterSection>
	{/if}

	<!-- Métricas de Rendimiento -->
	<FilterSection title="Rendimiento del Video" defaultOpen={true}>
		<div class="space-y-4">
			<RangeFilter
				label="Visualizaciones Mínimas"
				unit="vistas"
				step={500}
				bind:min={filters.minViews}
			/>

			<RangeFilter
				label="Ingresos Mínimos ($)"
				unit="$"
				step={10}
				bind:min={filters.minRevenue}
			/>
		</div>
	</FilterSection>

	<!-- Trazabilidad / Clips -->
	<FilterSection title="Trazabilidad & Tipo" defaultOpen={true}>
		<label class="flex items-center gap-3 cursor-pointer select-none rounded-xl border border-[#1F2937] bg-[#111827] p-3 hover:border-gray-700 transition-colors">
			<input
				type="checkbox"
				bind:checked={filters.onlyLiveDerived}
				class="h-4 w-4 rounded border-gray-700 bg-gray-900 text-indigo-600 focus:ring-indigo-500/20"
			/>
			<div>
				<span class="text-xs font-semibold text-white block">Solo clips derivados de Live</span>
				<span class="text-[10px] text-gray-400">Filtrar videos generados o extraídos de directos</span>
			</div>
		</label>
	</FilterSection>
</FilterDrawer>
