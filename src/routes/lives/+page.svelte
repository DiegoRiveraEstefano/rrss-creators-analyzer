<script lang="ts">
	import { createQuery, useQueryClient } from '@tanstack/svelte-query';
	import { sessionsQueryOptions, sessionsQueryKeys } from '$lib/query/sessions';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import type { StreamingSession } from '$lib/services/analyticsService';
	import { formatCurrency, formatNumber, formatDuration, formatDateTime } from '$lib/utils/formatters';
	import StatCard from '$lib/components/ui/StatCard.svelte';
	import DataTable from '$lib/components/ui/DataTable.svelte';
	import type { Column } from '$lib/types/ui';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import AddLiveModal from '$lib/components/creators/AddLiveModal.svelte';
	import EditLiveModal from '$lib/components/creators/EditLiveModal.svelte';
	import {
		FilterDrawer,
		FilterTriggerButton,
		FilterSection,
		DateRangeFilter,
		PlatformFilter,
		RangeFilter,
		MultiSelectFilter,
		CreatorFilter,
		type DateRangeFilterValue,
		type LiveTableFilterState
	} from '$lib/components/filters';
	import type { PlatformType } from '$lib/supabase/database.types';
	import {
		Radio,
		Plus,
		DollarSign,
		Users,
		Clock,
		Flame,
		Sparkles,
		MessageSquare,
		Gamepad2,
		Layers,
		Edit3
	} from 'lucide-svelte';

	const queryClient = useQueryClient();

	const sessionsQuery = createQuery(() =>
		sessionsQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);

	let sessions = $derived(sessionsQuery.data || []);
	let isLoading = $derived(sessionsQuery.isLoading);
	let isAddModalOpen = $state(false);
	let isEditModalOpen = $state(false);
	let editingSession = $state<StreamingSession | null>(null);
	let isFilterOpen = $state(false);

	let filters = $state<LiveTableFilterState>({
		creatorIds: [],
		dateRange: { preset: 'all' },
		platforms: [],
		categories: [],
		minCcv: null,
		minPeak: null,
		minEarnings: null,
		minDurationHours: null
	});

	let availableCategories = $derived.by(() => {
		const cats = new Set<string>();
		for (const s of sessions) {
			if (s.game_or_category) cats.add(s.game_or_category);
		}
		return Array.from(cats).map((c) => ({ value: c, label: c }));
	});

	let activeFilterCount = $derived.by(() => {
		let count = 0;
		if (filters.creatorIds.length > 0) count++;
		if (filters.dateRange.preset !== 'all') count++;
		if (filters.platforms.length > 0) count++;
		if (filters.categories.length > 0) count++;
		if (filters.minCcv != null && filters.minCcv > 0) count++;
		if (filters.minPeak != null && filters.minPeak > 0) count++;
		if (filters.minEarnings != null && filters.minEarnings > 0) count++;
		if (filters.minDurationHours != null && filters.minDurationHours > 0) count++;
		return count;
	});

	function resetFilters() {
		filters = {
			creatorIds: [],
			dateRange: { preset: 'all' },
			platforms: [],
			categories: [],
			minCcv: null,
			minPeak: null,
			minEarnings: null,
			minDurationHours: null
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
			if (filters.creatorIds.length > 0 && !filters.creatorIds.includes(s.creator_id)) {
				return false;
			}

			if (filters.platforms.length > 0 && !filters.platforms.includes(s.platform)) {
				return false;
			}

			if (filters.categories.length > 0) {
				if (!s.game_or_category || !filters.categories.includes(s.game_or_category)) {
					return false;
				}
			}

			if (!matchesDateRange(s.streamed_at)) return false;

			if (filters.minCcv != null && (s.avg_ccv || 0) < filters.minCcv) {
				return false;
			}

			if (filters.minPeak != null && (s.peak_viewers || 0) < filters.minPeak) {
				return false;
			}

			if (filters.minEarnings != null && (s.total_earnings || 0) < filters.minEarnings) {
				return false;
			}

			if (filters.minDurationHours != null) {
				const hours = (s.duration_seconds || 0) / 3600;
				if (hours < filters.minDurationHours) return false;
			}

			return true;
		});
	});

	function handleDataChanged() {
		queryClient.invalidateQueries({ queryKey: sessionsQueryKeys.all });
	}

	function openEditModal(sessionItem: StreamingSession) {
		editingSession = sessionItem;
		isEditModalOpen = true;
	}

	// Métricas Reactivas para StatCards
	let totalDurationSecs = $derived(
		filteredSessions.reduce((acc, s) => acc + (s.duration_seconds || 0), 0)
	);
	let totalHours = $derived(Number((totalDurationSecs / 3600).toFixed(1)));
	let totalEarnings = $derived(
		filteredSessions.reduce((acc, s) => acc + Number(s.total_earnings || 0), 0)
	);
	let avgCcv = $derived(
		filteredSessions.length > 0
			? Math.round(
					filteredSessions.reduce((acc, s) => acc + (s.avg_ccv || 0), 0) / filteredSessions.length
				)
			: 0
	);
	let peakViewers = $derived(
		filteredSessions.reduce((acc, s) => Math.max(acc, s.peak_viewers || 0), 0)
	);

	// Columnas de la Tabla
	const sessionColumns: Column<StreamingSession>[] = [
		{
			key: 'session_title',
			label: 'Sesión & Categoría',
			sortable: true
		},
		{
			key: 'platform',
			label: 'Plataforma',
			align: 'center',
			sortable: true
		},
		{
			key: 'streamed_at',
			label: 'Fecha UTC',
			isMono: true,
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
			key: 'avg_ccv',
			label: 'Media CCV',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'peak_viewers',
			label: 'Pico Máx',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'chat_messages_count',
			label: 'Chat',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'ad_revenue',
			label: 'Ads ($)',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'subs_revenue',
			label: 'Subs ($)',
			align: 'right',
			isMono: true,
			sortable: true
		},
		{
			key: 'total_earnings',
			label: 'Total ($)',
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

{#snippet titleCell({ row }: { row: StreamingSession })}
	<div class="space-y-1 py-1">
		<div class="font-semibold text-white truncate max-w-sm">
			{row.session_title}
		</div>
		<div class="flex items-center gap-2 text-[11px] text-gray-400">
			{#if row.game_or_category}
				<span class="inline-flex items-center gap-1 text-indigo-300 font-medium">
					<Gamepad2 size={12} />
					{row.game_or_category}
				</span>
			{/if}
			{#if row.new_followers > 0}
				<span class="text-gray-500">•</span>
				<span class="text-emerald-400 font-mono">+{row.new_followers} followers</span>
			{/if}
		</div>
	</div>
{/snippet}

{#snippet platformCell({ row }: { row: StreamingSession })}
	<Badge
		variant={row.platform === 'twitch' ? 'purple' : row.platform === 'youtube' ? 'danger' : row.platform === 'kick' ? 'success' : 'cyan'}
		size="sm"
	>
		{row.platform}
	</Badge>
{/snippet}

{#snippet dateCell({ row }: { row: StreamingSession })}
	<span class="font-mono text-xs text-gray-300">
		{formatDateTime(row.streamed_at)}
	</span>
{/snippet}

{#snippet durationCell({ row }: { row: StreamingSession })}
	<span class="font-mono text-xs text-gray-300">
		{formatDuration(row.duration_seconds)}
	</span>
{/snippet}

{#snippet ccvCell({ row }: { row: StreamingSession })}
	<span class="font-mono text-xs font-semibold text-white">
		{formatNumber(row.avg_ccv)}
	</span>
{/snippet}

{#snippet peakCell({ row }: { row: StreamingSession })}
	<span class="font-mono text-xs font-bold text-amber-400">
		{formatNumber(row.peak_viewers, true)}
	</span>
{/snippet}

{#snippet chatCell({ row }: { row: StreamingSession })}
	<span class="font-mono text-xs text-gray-400">
		{formatNumber(row.chat_messages_count, true)}
	</span>
{/snippet}

{#snippet adsCell({ row }: { row: StreamingSession })}
	<span class="font-mono text-xs text-gray-400">
		{formatCurrency(row.ad_revenue)}
	</span>
{/snippet}

{#snippet subsCell({ row }: { row: StreamingSession })}
	<span class="font-mono text-xs text-gray-300">
		{formatCurrency(row.subs_revenue)}
	</span>
{/snippet}

{#snippet totalCell({ row }: { row: StreamingSession })}
	<span class="font-mono text-xs font-bold text-emerald-400">
		{formatCurrency(row.total_earnings)}
	</span>
{/snippet}

{#snippet actionsCell({ row }: { row: StreamingSession })}
	<div class="flex items-center justify-center gap-1.5">
		<Button
			variant="secondary"
			size="sm"
			onclick={() => openEditModal(row)}
			class="h-7 px-2.5 text-xs text-indigo-300 hover:text-white"
			title="Editar sesión en vivo"
		>
			<Edit3 size={13} />
			<span>Editar</span>
		</Button>
	</div>
{/snippet}

<svelte:head>
	<title>Sesiones en Vivo (Lives) | RRSS Creators Analyzer</title>
</svelte:head>

<div class="space-y-6">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<Radio class="text-rose-400" size={24} />
				<span>Sesiones de Transmisión en Vivo (Lives)</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				Registro histórico de emisiones en directo, retención de audiencia concurrente y desglose de ingresos por canal.
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
				Registrar Live
			</Button>
		</div>
	</div>

	<!-- KPIs -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<StatCard
			title="Horas Transmitidas"
			value={`${totalHours} hrs`}
			icon={Clock}
			iconColor="indigo"
			subtitle={`${filteredSessions.length} emisiones registradas`}
		/>

		<StatCard
			title="Media de Espectadores (Avg CCV)"
			value={formatNumber(avgCcv)}
			icon={Users}
			iconColor="cyan"
		/>

		<StatCard
			title="Pico Máximo Concurrente"
			value={formatNumber(peakViewers, true)}
			icon={Flame}
			iconColor="amber"
		/>

		<StatCard
			title="Ingresos Totales por Lives"
			value={formatCurrency(totalEarnings)}
			icon={DollarSign}
			iconColor="emerald"
		/>
	</div>

	<!-- Tabla de Sesiones -->
	<div class="space-y-3">
		<div class="flex items-center justify-between">
			<h3 class="text-base font-semibold text-white flex items-center gap-2">
				<Layers size={18} class="text-indigo-400" />
				<span>Emisiones y Rendimiento en Directo</span>
			</h3>
		</div>

		<DataTable
			data={filteredSessions}
			columns={[
				{ ...sessionColumns[0], render: titleCell },
				{ ...sessionColumns[1], render: platformCell },
				{ ...sessionColumns[2], render: dateCell },
				{ ...sessionColumns[3], render: durationCell },
				{ ...sessionColumns[4], render: ccvCell },
				{ ...sessionColumns[5], render: peakCell },
				{ ...sessionColumns[6], render: chatCell },
				{ ...sessionColumns[7], render: adsCell },
				{ ...sessionColumns[8], render: subsCell },
				{ ...sessionColumns[9], render: totalCell },
				{ ...sessionColumns[10], render: actionsCell }
			]}
			searchPlaceholder="Buscar por título, categoría o plataforma..."
			searchKeys={['session_title', 'game_or_category', 'platform']}
		/>
	</div>

	<!-- Modal para Registrar Sesión en Vivo -->
	{#if tenantStore.currentOrg}
		<AddLiveModal
			isOpen={isAddModalOpen}
			organizationId={tenantStore.currentOrg.id}
			creatorId={tenantStore.selectedCreatorId}
			onClose={() => (isAddModalOpen = false)}
			onAdded={handleDataChanged}
		/>

		<EditLiveModal
			isOpen={isEditModalOpen}
			session={editingSession}
			onClose={() => {
				isEditModalOpen = false;
				editingSession = null;
			}}
			onUpdated={handleDataChanged}
			onDeleted={handleDataChanged}
		/>
	{/if}
</div>

<!-- Drawer de Filtros (Derecha) -->
<FilterDrawer
	isOpen={isFilterOpen}
	title="Filtros de Sesiones en Vivo"
	position="right"
	activeCount={activeFilterCount}
	onClose={() => (isFilterOpen = false)}
	onReset={resetFilters}
>
	<!-- Creadores / Talentos -->
	<FilterSection title="Creadores / Talentos" defaultOpen={true}>
		<CreatorFilter bind:selected={filters.creatorIds} />
	</FilterSection>

	<!-- Rango Temporal -->
	<FilterSection title="Rango de Fechas" defaultOpen={true}>
		<DateRangeFilter bind:value={filters.dateRange} />
	</FilterSection>

	<!-- Plataformas -->
	<FilterSection title="Plataformas de Emisión" defaultOpen={true}>
		<PlatformFilter bind:selected={filters.platforms} />
	</FilterSection>

	<!-- Categorías / Juegos -->
	{#if availableCategories.length > 0}
		<FilterSection title="Juegos y Categorías" defaultOpen={true}>
			<MultiSelectFilter
				options={availableCategories}
				bind:selected={filters.categories}
				placeholder="Buscar juego o categoría..."
			/>
		</FilterSection>
	{/if}

	<!-- Métricas de Audiencia -->
	<FilterSection title="Audiencia en Directo" defaultOpen={true}>
		<div class="space-y-4">
			<RangeFilter
				label="Media Concurrente (Avg CCV)"
				unit="ccv"
				step={50}
				bind:min={filters.minCcv}
			/>

			<RangeFilter
				label="Pico Máximo de Viewers"
				unit="pico"
				step={100}
				bind:min={filters.minPeak}
			/>
		</div>
	</FilterSection>

	<!-- Rendimiento Financiero & Duración -->
	<FilterSection title="Finanzas y Tiempo" defaultOpen={true}>
		<div class="space-y-4">
			<RangeFilter
				label="Ingresos Mínimos ($)"
				unit="$"
				step={10}
				bind:min={filters.minEarnings}
			/>

			<RangeFilter
				label="Duración Mínima (Horas)"
				unit="hrs"
				step={0.5}
				bind:min={filters.minDurationHours}
			/>
		</div>
	</FilterSection>
</FilterDrawer>
