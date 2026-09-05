<script lang="ts">
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import { alertsService, type ChannelAlert } from '$lib/services/alertsService';
	import { formatDateTime } from '$lib/utils/formatters';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import {
		AlertTriangle,
		ShieldAlert,
		CheckCircle2,
		Clock,
		Radio,
		HelpCircle,
		ShieldCheck
	} from 'lucide-svelte';

	import { createQuery, useQueryClient } from '@tanstack/svelte-query';
	import { alertsQueryOptions, alertsQueryKeys } from '$lib/query/alerts';
	import {
		FilterDrawer,
		FilterTriggerButton,
		FilterSection,
		MultiSelectFilter
	} from '$lib/components/filters';

	const queryClient = useQueryClient();

	const alertsQuery = createQuery(() =>
		alertsQueryOptions(tenantStore.currentOrg?.id, tenantStore.selectedCreatorId)
	);

	let alerts = $derived(alertsQuery.data || []);
	let isLoading = $derived(alertsQuery.isLoading);
	let selectedAlert = $state<ChannelAlert | null>(null);
	let isModalOpen = $state(false);
	let resolutionNotes = $state('');
	let isResolving = $state(false);
	let isFilterOpen = $state(false);

	let filters = $state<{
		severities: string[];
		status: 'all' | 'active' | 'resolved';
		alertTypes: string[];
	}>({
		severities: [],
		status: 'all',
		alertTypes: []
	});

	let availableAlertTypes = $derived.by(() => {
		const types = new Set<string>();
		for (const a of alerts) {
			if (a.alert_type) types.add(a.alert_type);
		}
		return Array.from(types).map((t) => ({ value: t, label: t }));
	});

	let activeFilterCount = $derived.by(() => {
		let count = 0;
		if (filters.severities.length > 0) count++;
		if (filters.status !== 'all') count++;
		if (filters.alertTypes.length > 0) count++;
		return count;
	});

	function resetFilters() {
		filters = {
			severities: [],
			status: 'all',
			alertTypes: []
		};
	}

	let filteredAlerts = $derived.by(() => {
		return alerts.filter((a) => {
			if (filters.severities.length > 0 && !filters.severities.includes(a.severity)) {
				return false;
			}
			if (filters.alertTypes.length > 0 && !filters.alertTypes.includes(a.alert_type)) {
				return false;
			}
			if (filters.status === 'active' && a.status !== 'active') return false;
			if (filters.status === 'resolved' && a.status !== 'resolved') return false;
			return true;
		});
	});

	function openResolveModal(alert: ChannelAlert) {
		selectedAlert = alert;
		resolutionNotes = '';
		isModalOpen = true;
	}

	async function handleResolveAlert() {
		if (!selectedAlert) return;
		isResolving = true;
		try {
			await alertsService.resolveAlert(selectedAlert.id, resolutionNotes);
			queryClient.invalidateQueries({ queryKey: alertsQueryKeys.all });
			isModalOpen = false;
		} catch (e) {
			console.error('Error resolving alert:', e);
		} finally {
			isResolving = false;
		}
	}

	let activeAlerts = $derived(filteredAlerts.filter((a) => a.status === 'active'));
	let resolvedAlerts = $derived(filteredAlerts.filter((a) => a.status === 'resolved'));
</script>

<div class="space-y-6">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<ShieldAlert class="text-amber-400" size={24} />
				<span>Centro de Alertas y Sanciones de Canal</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				Monitoreo de strikes DMCA, advertencias de Términos de Servicio de plataformas e incidentes técnicos.
			</p>
		</div>

		<div class="flex items-center gap-2">
			<FilterTriggerButton
				activeCount={activeFilterCount}
				isOpen={isFilterOpen}
				onclick={() => (isFilterOpen = !isFilterOpen)}
			/>

			<Badge variant="warning" dot pulse size="md">
				{activeAlerts.length} Activas
			</Badge>
			<Badge variant="success" size="md">
				{resolvedAlerts.length} Resueltas
			</Badge>
		</div>
	</div>

	<!-- Alertas Activas -->
	<div class="space-y-3">
		<h3 class="text-sm font-semibold uppercase tracking-wider text-gray-400">
			Alertas Activas que Requieren Atención
		</h3>

		{#if activeAlerts.length === 0}
			<div class="rounded-xl border border-emerald-500/20 bg-[#111827] p-8 text-center">
				<div class="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mb-3">
					<ShieldCheck size={24} />
				</div>
				<h4 class="text-sm font-semibold text-white">Canales 100% en Cumplimiento</h4>
				<p class="text-xs text-gray-400 mt-1">
					No hay sanciones ni advertencias pendientes de resolución para los creadores seleccionados.
				</p>
			</div>
		{:else}
			<div class="space-y-3">
				{#each activeAlerts as alert}
					<div
						class="rounded-xl border border-[#1F2937] bg-[#111827] p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all hover:border-amber-500/40"
					>
						<div class="flex items-start gap-4">
							<div
								class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border {alert.severity === 'critical'
									? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
									: 'bg-amber-500/10 text-amber-400 border-amber-500/30'}"
							>
								<AlertTriangle size={20} />
							</div>

							<div class="space-y-1">
								<div class="flex items-center gap-2.5">
									<h4 class="text-sm font-bold text-white">{alert.title}</h4>
									<Badge
										variant={alert.severity === 'critical' ? 'danger' : 'warning'}
										size="sm"
									>
										{alert.alert_type}
									</Badge>
								</div>

								{#if alert.description}
									<p class="text-xs text-gray-300">{alert.description}</p>
								{/if}

								<div class="flex items-center gap-3 text-[11px] text-gray-400 font-mono pt-1">
									<span class="flex items-center gap-1">
										<Clock size={12} />
										{formatDateTime(alert.occurred_at)}
									</span>
								</div>
							</div>
						</div>

						<Button
							variant="secondary"
							size="sm"
							onclick={() => openResolveModal(alert)}
						>
							<CheckCircle2 size={14} class="text-emerald-400" />
							Marcar como Resuelto
						</Button>
					</div>
				{/each}
			</div>
		{/if}
	</div>

	<!-- Historial de Alertas Resueltas -->
	{#if resolvedAlerts.length > 0}
		<div class="space-y-3 pt-6 border-t border-[#1F2937]">
			<h3 class="text-sm font-semibold uppercase tracking-wider text-gray-400">
				Historial de Incidentes Resueltos
			</h3>

			<div class="space-y-2">
				{#each resolvedAlerts as alert}
					<div
						class="rounded-xl border border-[#1F2937]/50 bg-[#0E1420] p-4 flex items-center justify-between text-xs opacity-75 hover:opacity-100 transition-opacity"
					>
						<div class="flex items-center gap-3">
							<CheckCircle2 size={16} class="text-emerald-400" />
							<div>
								<span class="font-medium text-white">{alert.title}</span>
								{#if alert.resolution_notes}
									<span class="text-gray-400 ml-2">— {alert.resolution_notes}</span>
								{/if}
							</div>
						</div>
						<span class="text-gray-400 font-mono text-[11px]">
							Resuelto el {formatDateTime(alert.resolved_at || alert.updated_at)}
						</span>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<!-- Drawer de Filtros (Derecha) -->
<FilterDrawer
	isOpen={isFilterOpen}
	title="Filtros de Alertas y Sanciones"
	position="right"
	activeCount={activeFilterCount}
	onClose={() => (isFilterOpen = false)}
	onReset={resetFilters}
>
	<!-- Estado -->
	<FilterSection title="Estado de Resolución" defaultOpen={true}>
		<div class="grid grid-cols-3 gap-2">
			<button
				type="button"
				class="rounded-xl border px-3 py-2 text-xs font-semibold transition-all {filters.status === 'all'
					? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/40 shadow-sm'
					: 'border-[#1F2937] bg-[#111827] text-gray-400 hover:text-white hover:bg-gray-800'}"
				onclick={() => (filters.status = 'all')}
			>
				Todas
			</button>
			<button
				type="button"
				class="rounded-xl border px-3 py-2 text-xs font-semibold transition-all {filters.status === 'active'
					? 'bg-amber-600/20 text-amber-300 border-amber-500/40 shadow-sm'
					: 'border-[#1F2937] bg-[#111827] text-gray-400 hover:text-white hover:bg-gray-800'}"
				onclick={() => (filters.status = 'active')}
			>
				Activas
			</button>
			<button
				type="button"
				class="rounded-xl border px-3 py-2 text-xs font-semibold transition-all {filters.status === 'resolved'
					? 'bg-emerald-600/20 text-emerald-300 border-emerald-500/40 shadow-sm'
					: 'border-[#1F2937] bg-[#111827] text-gray-400 hover:text-white hover:bg-gray-800'}"
				onclick={() => (filters.status = 'resolved')}
			>
				Resueltas
			</button>
		</div>
	</FilterSection>

	<!-- Severidad -->
	<FilterSection title="Severidad" defaultOpen={true}>
		<div class="flex flex-wrap gap-2">
			{#each [
				{ key: 'critical', label: 'Crítica', color: 'rose' },
				{ key: 'warning', label: 'Advertencia', color: 'amber' },
				{ key: 'info', label: 'Informativa', color: 'blue' }
			] as sev}
				{@const isSelected = filters.severities.includes(sev.key)}
				<button
					type="button"
					class="px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all {isSelected
						? 'bg-indigo-600 text-white border-indigo-500 shadow-md'
						: 'bg-[#111827] text-gray-400 border-[#1F2937] hover:text-white hover:border-gray-700'}"
					onclick={() => {
						if (isSelected) {
							filters.severities = filters.severities.filter((s) => s !== sev.key);
						} else {
							filters.severities = [...filters.severities, sev.key];
						}
					}}
				>
					{sev.label}
				</button>
			{/each}
		</div>
	</FilterSection>

	<!-- Tipo de Incidente -->
	{#if availableAlertTypes.length > 0}
		<FilterSection title="Tipo de Incidente" defaultOpen={true}>
			<MultiSelectFilter
				options={availableAlertTypes}
				bind:selected={filters.alertTypes}
				placeholder="Buscar tipo de alerta..."
			/>
		</FilterSection>
	{/if}
</FilterDrawer>

<!-- Modal para resolver alerta -->
<Modal
	isOpen={isModalOpen}
	title="Resolver Alerta de Canal"
	onClose={() => (isModalOpen = false)}
>
	<div class="space-y-4">
		<p class="text-xs text-gray-300">
			Confirmar que el incidente <b class="text-white">"{selectedAlert?.title}"</b> ha sido subsanado o apelado exitosamente ante la plataforma.
		</p>

		<Input
			label="Notas de Resolución (Opcional)"
			placeholder="ej. VOD silenciado y apelación DMCA aceptada"
			bind:value={resolutionNotes}
		/>
	</div>

	{#snippet footer()}
		<Button variant="ghost" size="sm" onclick={() => (isModalOpen = false)}>
			Cancelar
		</Button>
		<Button
			variant="primary"
			size="sm"
			isLoading={isResolving}
			onclick={handleResolveAlert}
		>
			<CheckCircle2 size={15} />
			Confirmar Resolución
		</Button>
	{/snippet}
</Modal>
