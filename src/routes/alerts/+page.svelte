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

	let alerts = $state<ChannelAlert[]>([]);
	let isLoading = $state(true);
	let selectedAlert = $state<ChannelAlert | null>(null);
	let isModalOpen = $state(false);
	let resolutionNotes = $state('');
	let isResolving = $state(false);

	async function loadAlerts() {
		if (!tenantStore.currentOrg) return;
		isLoading = true;
		try {
			alerts = await alertsService.getAlerts(
				tenantStore.currentOrg.id,
				tenantStore.selectedCreatorId
			);
		} catch (e) {
			console.error('Error loading alerts:', e);
		} finally {
			isLoading = false;
		}
	}

	$effect(() => {
		if (tenantStore.currentOrg) {
			const _ = tenantStore.selectedCreatorId;
			loadAlerts();
		}
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
			await loadAlerts();
			isModalOpen = false;
		} catch (e) {
			console.error('Error resolving alert:', e);
		} finally {
			isResolving = false;
		}
	}

	let activeAlerts = $derived(alerts.filter((a) => a.status === 'active'));
	let resolvedAlerts = $derived(alerts.filter((a) => a.status === 'resolved'));
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
