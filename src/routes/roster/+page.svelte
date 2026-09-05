<script lang="ts">
	import { createQuery, useQueryClient } from '@tanstack/svelte-query';
	import { creatorsQueryOptions, creatorsQueryKeys } from '$lib/query/creators';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import { creatorService, type CreatorWithChannels } from '$lib/services/creatorService';
	import { formatNumber } from '$lib/utils/formatters';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import EditCreatorModal from '$lib/components/creators/EditCreatorModal.svelte';
	import type { PlatformType } from '$lib/supabase/database.types';
	import {
		Users,
		Plus,
		ExternalLink,
		Radio,
		Activity,
		Tv,
		Edit,
		BarChart3,
		UserCheck,
		Loader2
	} from 'lucide-svelte';

	import {
		FilterDrawer,
		FilterTriggerButton,
		FilterSection,
		PlatformFilter,
		RangeFilter,
		type RosterFilterState
	} from '$lib/components/filters';

	const queryClient = useQueryClient();

	const creatorsQuery = createQuery(() => creatorsQueryOptions(tenantStore.currentOrg?.id));

	let creators = $derived(creatorsQuery.data || []);
	let isLoading = $derived(creatorsQuery.isLoading);

	let isCreateModalOpen = $state(false);
	let isEditModalOpen = $state(false);
	let selectedCreatorForEdit = $state<CreatorWithChannels | null>(null);
	let isCreating = $state(false);
	let isFilterOpen = $state(false);

	let filters = $state<{
		platforms: PlatformType[];
		status: 'all' | 'live' | 'offline';
		minFollowers: number | null;
	}>({
		platforms: [],
		status: 'all',
		minFollowers: null
	});

	let activeFilterCount = $derived.by(() => {
		let count = 0;
		if (filters.platforms.length > 0) count++;
		if (filters.status !== 'all') count++;
		if (filters.minFollowers != null && filters.minFollowers > 0) count++;
		return count;
	});

	function resetFilters() {
		filters = {
			platforms: [],
			status: 'all',
			minFollowers: null
		};
	}

	let filteredCreators = $derived.by(() => {
		return creators.filter((creator) => {
			if (filters.platforms.length > 0) {
				const hasMatchingPlatform =
					filters.platforms.includes(creator.primary_platform) ||
					creator.channels.some((c) => filters.platforms.includes(c.platform as any));
				if (!hasMatchingPlatform) return false;
			}

			const isLive = creator.channels.some((c) => c.is_live);
			if (filters.status === 'live' && !isLive) return false;
			if (filters.status === 'offline' && isLive) return false;

			if (filters.minFollowers != null && filters.minFollowers > 0) {
				const totalFollowers = creator.channels.reduce(
					(acc, c) => acc + (c.followers_count || 0),
					0
				);
				if (totalFollowers < filters.minFollowers) return false;
			}

			return true;
		});
	});

	let newDisplayName = $state('');
	let newHandle = $state('');
	let newPlatform = $state<string>('twitch');
	let newBio = $state('');
	let newAvatarUrl = $state('');

	async function handleCreateCreator() {
		if (!tenantStore.currentOrg || !newDisplayName || !newHandle) return;
		isCreating = true;
		try {
			await creatorService.createCreator({
				organization_id: tenantStore.currentOrg.id,
				display_name: newDisplayName,
				handle: newHandle.replace('@', ''),
				primary_platform: newPlatform as PlatformType,
				avatar_url: newAvatarUrl || `https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80`,
				bio: newBio || null
			});
			await queryClient.invalidateQueries({ queryKey: creatorsQueryKeys.all });
			await tenantStore.loadCreators();
			isCreateModalOpen = false;
			// Reset form
			newDisplayName = '';
			newHandle = '';
			newBio = '';
			newAvatarUrl = '';
		} catch (error) {
			console.error('Error creating creator:', error);
		} finally {
			isCreating = false;
		}
	}

	function openEditModal(creator: CreatorWithChannels) {
		selectedCreatorForEdit = creator;
		isEditModalOpen = true;
	}
</script>

<div class="space-y-6">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<Users class="text-indigo-400" size={24} />
				<span>Roster de Creadores y Canales</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				Gestiona los talentos representados, canales vinculados y monitoreo de transmisiones en vivo.
			</p>
		</div>

		<div class="flex items-center gap-2">
			<FilterTriggerButton
				activeCount={activeFilterCount}
				isOpen={isFilterOpen}
				onclick={() => (isFilterOpen = !isFilterOpen)}
			/>

			<Button variant="primary" size="md" onclick={() => (isCreateModalOpen = true)}>
				<Plus size={16} />
				Añadir Creador al Roster
			</Button>
		</div>
	</div>

	<!-- Roster Grid -->
	{#if isLoading && creators.length === 0}
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-16 text-center space-y-3 flex flex-col items-center justify-center">
			<Loader2 size={32} class="animate-spin text-indigo-400" />
			<p class="text-xs text-gray-400 mt-2">Cargando creadores del roster...</p>
		</div>
	{:else if creators.length === 0}
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-12 text-center space-y-3">
			<div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
				<Users size={28} />
			</div>
			<h3 class="text-base font-bold text-white">No hay creadores registrados en esta organización</h3>
			<p class="text-xs text-gray-400 max-w-sm mx-auto">
				Comienza añadiendo el primer creador al roster para ingestar sus sesiones y métricas.
			</p>
			<div class="pt-2">
				<Button variant="primary" size="sm" onclick={() => (isCreateModalOpen = true)}>
					<Plus size={14} />
					Añadir Primer Creador
				</Button>
			</div>
		</div>
	{:else if filteredCreators.length === 0}
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-12 text-center space-y-3">
			<div class="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-gray-800 text-gray-400 border border-gray-700">
				<Users size={24} />
			</div>
			<h3 class="text-base font-bold text-white">Ningún creador coincide con los filtros aplicados</h3>
			<p class="text-xs text-gray-400 max-w-sm mx-auto">
				Prueba cambiando la plataforma seleccionada, el estado de transmisión o los umbrales numéricos.
			</p>
			<div class="pt-2">
				<Button variant="secondary" size="sm" onclick={resetFilters}>
					Limpiar Filtros
				</Button>
			</div>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
			{#each filteredCreators as creator}
				{@const isLive = creator.channels.some((c) => c.is_live)}
				{@const totalFollowers = creator.channels.reduce((acc, c) => acc + (c.followers_count || 0), 0)}
				{@const totalSubs = creator.channels.reduce((acc, c) => acc + (c.subscribers_count || 0), 0)}

				<div
					class="relative overflow-hidden rounded-2xl bg-[#111827] border border-[#1F2937] p-5 shadow-xl transition-all duration-200 hover:border-indigo-500/40 hover:shadow-indigo-500/5 flex flex-col justify-between"
				>
					<div>
						<!-- Header con Avatar y Estado Live -->
						<div class="flex items-start justify-between">
							<div class="flex items-center gap-3.5">
								<div class="relative">
									<img
										src={creator.avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80'}
										alt={creator.display_name}
										class="h-14 w-14 rounded-2xl object-cover ring-2 {isLive ? 'ring-cyan-500 shadow-lg shadow-cyan-500/20' : 'ring-gray-700'}"
									/>
									{#if isLive}
										<span class="absolute -bottom-1 -right-1 flex h-4 w-4">
											<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
											<span class="relative inline-flex rounded-full h-4 w-4 bg-cyan-500 items-center justify-center">
												<Radio size={9} class="text-white" />
											</span>
										</span>
									{/if}
								</div>

								<div class="space-y-0.5">
									<a href="/roster/{creator.id}" class="text-base font-bold text-white hover:text-indigo-400 transition-colors flex items-center gap-1.5">
										{creator.display_name}
									</a>
									<div class="flex items-center gap-2 text-xs text-gray-400 font-mono">
										<span>@{creator.handle}</span>
										<span>•</span>
										<Badge
											variant={creator.primary_platform === 'twitch' ? 'purple' : creator.primary_platform === 'youtube' ? 'danger' : 'cyan'}
											size="sm"
										>
											{creator.primary_platform}
										</Badge>
									</div>
								</div>
							</div>

							{#if isLive}
								<Badge variant="cyan" dot pulse size="sm">
									EN VIVO
								</Badge>
							{:else}
								<Badge variant="neutral" size="sm">
									Offline
								</Badge>
							{/if}
						</div>

						<!-- Bio -->
						{#if creator.bio}
							<p class="mt-3.5 text-xs text-gray-400 line-clamp-2">
								{creator.bio}
							</p>
						{/if}

						<!-- Métricas de Canal -->
						<div class="mt-4 grid grid-cols-2 gap-2 rounded-xl bg-[#090D16] border border-[#1F2937] p-3 text-center">
							<div>
								<div class="text-[10px] uppercase tracking-wider text-gray-400 font-medium">Seguidores</div>
								<div class="text-sm font-bold text-white font-mono mt-0.5">
									{formatNumber(totalFollowers, true)}
								</div>
							</div>
							<div>
								<div class="text-[10px] uppercase tracking-wider text-gray-400 font-medium">Suscripciones</div>
								<div class="text-sm font-bold text-indigo-400 font-mono mt-0.5">
									{formatNumber(totalSubs, true)}
								</div>
							</div>
						</div>
					</div>

					<!-- Botones de Acción -->
					<div class="mt-5 flex items-center gap-2 pt-3 border-t border-[#1F2937]">
						<a href="/roster/{creator.id}" class="flex-1">
							<Button variant="secondary" size="sm" class="w-full">
								<UserCheck size={14} />
								Detalle
							</Button>
						</a>

						<a href="/roster/{creator.id}/dashboard">
							<Button variant="outline" size="sm" title="Ver Dashboard Analítico">
								<BarChart3 size={14} />
							</Button>
						</a>

						<Button
							variant="outline"
							size="sm"
							onclick={() => openEditModal(creator)}
							title="Editar Creador"
						>
							<Edit size={14} />
						</Button>

						{#if creator.channels[0]?.channel_url}
							<a
								href={creator.channels[0].channel_url}
								target="_blank"
								rel="noopener noreferrer"
								class="rounded-lg border border-[#2D3748] bg-[#1F2937] p-2 text-gray-300 hover:text-white hover:border-indigo-500/50 transition-colors"
								title="Abrir canal en directo"
							>
								<ExternalLink size={14} />
							</a>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Drawer de Filtros (Derecha) -->
<FilterDrawer
	isOpen={isFilterOpen}
	title="Filtros de Creadores"
	position="right"
	activeCount={activeFilterCount}
	onClose={() => (isFilterOpen = false)}
	onReset={resetFilters}
>
	<!-- Plataformas -->
	<FilterSection title="Plataforma Principal" defaultOpen={true}>
		<PlatformFilter bind:selected={filters.platforms} />
	</FilterSection>

	<!-- Estado de Emisión -->
	<FilterSection title="Estado de Transmisión" defaultOpen={true}>
		<div class="grid grid-cols-3 gap-2">
			<button
				type="button"
				class="rounded-xl border px-3 py-2 text-xs font-semibold transition-all {filters.status === 'all'
					? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/40 shadow-sm'
					: 'border-[#1F2937] bg-[#111827] text-gray-400 hover:text-white hover:bg-gray-800'}"
				onclick={() => (filters.status = 'all')}
			>
				Todos
			</button>
			<button
				type="button"
				class="rounded-xl border px-3 py-2 text-xs font-semibold transition-all {filters.status === 'live'
					? 'bg-cyan-600/20 text-cyan-300 border-cyan-500/40 shadow-sm'
					: 'border-[#1F2937] bg-[#111827] text-gray-400 hover:text-white hover:bg-gray-800'}"
				onclick={() => (filters.status = 'live')}
			>
				En Vivo
			</button>
			<button
				type="button"
				class="rounded-xl border px-3 py-2 text-xs font-semibold transition-all {filters.status === 'offline'
					? 'bg-gray-700/50 text-gray-200 border-gray-600 shadow-sm'
					: 'border-[#1F2937] bg-[#111827] text-gray-400 hover:text-white hover:bg-gray-800'}"
				onclick={() => (filters.status = 'offline')}
			>
				Offline
			</button>
		</div>
	</FilterSection>

	<!-- Audiencia de Canales -->
	<FilterSection title="Comunidad / Seguidores" defaultOpen={true}>
		<RangeFilter
			label="Seguidores Mínimos"
			unit="fans"
			step={1000}
			bind:min={filters.minFollowers}
		/>
	</FilterSection>
</FilterDrawer>

<!-- Modal para añadir Creador -->
<Modal
	isOpen={isCreateModalOpen}
	title="Añadir Creador al Roster"
	onClose={() => (isCreateModalOpen = false)}
>
	<div class="space-y-4">
		<Input
			label="Nombre de Creador / Marca"
			placeholder="ej. Ibai Llanos"
			bind:value={newDisplayName}
		/>

		<Input
			label="Usuario / Handle"
			placeholder="ej. ibai"
			bind:value={newHandle}
			hint="Sin el símbolo @"
		/>

		<Select
			label="Plataforma Principal"
			options={[
				{ value: 'twitch', label: 'Twitch' },
				{ value: 'youtube', label: 'YouTube Gaming' },
				{ value: 'kick', label: 'Kick' },
				{ value: 'tiktok', label: 'TikTok Live' }
			]}
			bind:value={newPlatform}
		/>

		<Input
			label="URL de Foto / Avatar"
			placeholder="https://..."
			bind:value={newAvatarUrl}
			hint="Opcional. Si se deja en blanco se asignará uno por defecto."
		/>

		<Input
			label="Biografía / Descripción del Contenido"
			placeholder="Variedad, Just Chatting, Esports..."
			bind:value={newBio}
		/>
	</div>

	{#snippet footer()}
		<Button variant="ghost" size="sm" onclick={() => (isCreateModalOpen = false)}>
			Cancelar
		</Button>
		<Button
			variant="primary"
			size="sm"
			isLoading={isCreating}
			disabled={!newDisplayName || !newHandle}
			onclick={handleCreateCreator}
		>
			<Plus size={15} />
			Guardar Creador en Supabase
		</Button>
	{/snippet}
</Modal>

<!-- Modal para editar Creador -->
<EditCreatorModal
	isOpen={isEditModalOpen}
	creator={selectedCreatorForEdit}
	onClose={() => (isEditModalOpen = false)}
	onUpdated={() => {
		queryClient.invalidateQueries({ queryKey: creatorsQueryKeys.all });
		tenantStore.loadCreators();
	}}
/>
