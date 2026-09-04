<script lang="ts">
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import { videoService, type PublishedVideo } from '$lib/services/videoService';
	import { formatCurrency, formatNumber, formatDate } from '$lib/utils/formatters';
	import StatCard from '$lib/components/ui/StatCard.svelte';
	import DataTable from '$lib/components/ui/DataTable.svelte';
	import type { Column } from '$lib/types/ui';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import AddVideoModal from '$lib/components/creators/AddVideoModal.svelte';
	import {
		Video,
		Plus,
		DollarSign,
		Eye,
		ThumbsUp,
		MessageSquare,
		ExternalLink
	} from 'lucide-svelte';

	let videos = $state<PublishedVideo[]>([]);
	let isLoading = $state(true);
	let isAddModalOpen = $state(false);

	async function loadVideos() {
		if (!tenantStore.currentOrg) return;
		isLoading = true;
		try {
			if (tenantStore.selectedCreatorId) {
				videos = await videoService.getVideosByCreator(tenantStore.selectedCreatorId);
			} else {
				videos = await videoService.getVideosByOrganization(tenantStore.currentOrg.id);
			}
		} catch (error) {
			console.error('Error loading videos:', error);
		} finally {
			isLoading = false;
		}
	}

	$effect(() => {
		if (tenantStore.currentOrg) {
			const _ = tenantStore.selectedCreatorId;
			loadVideos();
		}
	});

	let totalViews = $derived(videos.reduce((acc, v) => acc + (v.views_count || 0), 0));
	let totalRevenue = $derived(videos.reduce((acc, v) => acc + Number(v.estimated_revenue || 0), 0));
	let totalLikes = $derived(videos.reduce((acc, v) => acc + (v.likes_count || 0), 0));

	const videoColumns: Column<PublishedVideo>[] = [
		{ key: 'title', label: 'Título del Video', sortable: true },
		{ key: 'platform', label: 'Plataforma', align: 'center', sortable: true },
		{ key: 'views_count', label: 'Vistas', align: 'right', isMono: true, sortable: true },
		{ key: 'likes_count', label: 'Likes', align: 'right', isMono: true, sortable: true },
		{ key: 'comments_count', label: 'Comentarios', align: 'right', isMono: true, sortable: true },
		{ key: 'shares_count', label: 'Shares', align: 'right', isMono: true, sortable: true },
		{ key: 'estimated_revenue', label: 'Ingresos Est. ($)', align: 'right', isMono: true, sortable: true }
	];
</script>

<svelte:head>
	<title>Videos Subidos | RRSS Creators Analyzer</title>
</svelte:head>

<div class="space-y-6">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<Video class="text-cyan-400" size={24} />
				<span>Videos Subidos y VODs</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				Registro y análisis de reproducciones, engagement y monetización de videos en YouTube, TikTok y VODs.
			</p>
		</div>

		<Button variant="primary" size="md" onclick={() => (isAddModalOpen = true)}>
			<Plus size={16} />
			Ingestar Video
		</Button>
	</div>

	<!-- KPIs -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<StatCard
			title="Total Visualizaciones"
			value={formatNumber(totalViews, true)}
			icon={Eye}
			iconColor="cyan"
			subtitle={`${videos.length} videos subidos`}
		/>

		<StatCard
			title="Ingresos Estimados por Videos"
			value={formatCurrency(totalRevenue)}
			icon={DollarSign}
			iconColor="emerald"
		/>

		<StatCard
			title="Total Likes / Me Gusta"
			value={formatNumber(totalLikes, true)}
			icon={ThumbsUp}
			iconColor="purple"
		/>

		<StatCard
			title="Videos Registrados"
			value={videos.length}
			icon={Video}
			iconColor="indigo"
		/>
	</div>

	<!-- Tabla de Videos -->
	<div class="space-y-3">
		<div class="flex items-center justify-between">
			<h3 class="text-base font-semibold text-white">Catálogo de Videos Publicados</h3>
		</div>

		<DataTable
			data={videos}
			columns={videoColumns}
			searchPlaceholder="Buscar por título de video o plataforma..."
			searchKeys={['title', 'platform']}
		/>
	</div>

	<!-- Modal para Ingestar Video -->
	{#if tenantStore.currentOrg && tenantStore.creators.length > 0}
		<AddVideoModal
			isOpen={isAddModalOpen}
			organizationId={tenantStore.currentOrg.id}
			creatorId={tenantStore.selectedCreatorId || tenantStore.creators[0].id}
			onClose={() => (isAddModalOpen = false)}
			onAdded={loadVideos}
		/>
	{/if}
</div>
