<script lang="ts">
	import { analyticsService } from '$lib/services/analyticsService';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import type { PlatformType } from '$lib/supabase/database.types';
	import { formatCurrency } from '$lib/utils/formatters';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import { Radio, Plus, AlertCircle, DollarSign, Users, Clock, MessageSquare, Zap } from 'lucide-svelte';

	interface Props {
		isOpen: boolean;
		organizationId: string;
		creatorId?: string | null;
		onClose: () => void;
		onAdded: () => void;
	}

	let {
		isOpen = $bindable(false),
		organizationId,
		creatorId,
		onClose,
		onAdded
	}: Props = $props();

	let selectedCreatorId = $state('');
	$effect(() => {
		if (creatorId) {
			selectedCreatorId = creatorId;
		} else if (!selectedCreatorId && tenantStore.creators[0]?.id) {
			selectedCreatorId = tenantStore.creators[0].id;
		}
	});
	let sessionTitle = $state('');
	let gameOrCategory = $state('Just Chatting');
	let platform = $state<PlatformType>('twitch');
	let streamedAt = $state(new Date().toISOString().substring(0, 16));
	let durationHours = $state(3.5);

	// Métricas de Audiencia
	let avgCcv = $state(1850);
	let peakViewers = $state(4200);
	let chatMessagesCount = $state(12400);
	let newFollowers = $state(180);

	// Métricas de Monetización
	let adRevenue = $state(95.5);
	let subsRevenue = $state(280.0);
	let donationsRevenue = $state(45.0);

	let isSaving = $state(false);
	let errorMessage = $state<string | null>(null);

	// Cálculos en tiempo real
	let calculatedTotalEarnings = $derived(
		Number((Number(adRevenue || 0) + Number(subsRevenue || 0) + Number(donationsRevenue || 0)).toFixed(2))
	);
	let calculatedEarningsPerHour = $derived(
		durationHours > 0 ? Number((calculatedTotalEarnings / Number(durationHours)).toFixed(2)) : 0
	);

	$effect(() => {
		if (creatorId) {
			selectedCreatorId = creatorId;
		} else if (tenantStore.selectedCreatorId) {
			selectedCreatorId = tenantStore.selectedCreatorId;
		} else if (tenantStore.creators.length > 0 && !selectedCreatorId) {
			selectedCreatorId = tenantStore.creators[0].id;
		}
	});

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!sessionTitle || !organizationId || !selectedCreatorId) {
			errorMessage = 'Por favor completa todos los campos requeridos.';
			return;
		}

		isSaving = true;
		errorMessage = null;

		const durationSeconds = Math.round(Number(durationHours || 0) * 3600);

		try {
			await analyticsService.addSession({
				organization_id: organizationId,
				creator_id: selectedCreatorId,
				session_title: sessionTitle.trim(),
				game_or_category: gameOrCategory.trim() || null,
				platform,
				streamed_at: new Date(streamedAt).toISOString(),
				duration_seconds: durationSeconds,
				avg_ccv: Number(avgCcv) || 0,
				peak_viewers: Number(peakViewers) || 0,
				chat_messages_count: Number(chatMessagesCount) || 0,
				new_followers: Number(newFollowers) || 0,
				ad_revenue: Number(adRevenue) || 0,
				subs_revenue: Number(subsRevenue) || 0,
				donations_revenue: Number(donationsRevenue) || 0,
				total_earnings: calculatedTotalEarnings,
				earnings_per_hour: calculatedEarningsPerHour
			});

			onAdded();
			onClose();

			// Reset form
			sessionTitle = '';
			gameOrCategory = 'Just Chatting';
			durationHours = 3.5;
			avgCcv = 1850;
			peakViewers = 4200;
			adRevenue = 95.5;
			subsRevenue = 280.0;
			donationsRevenue = 45.0;
		} catch (err: any) {
			console.error('Error adding streaming session:', err);
			errorMessage = err.message || 'Error al guardar la sesión de streaming en Supabase.';
		} finally {
			isSaving = false;
		}
	}
</script>

<Modal
	{isOpen}
	title="Registrar Sesión de Transmisión en Vivo (Live)"
	maxWidth="2xl"
	{onClose}
>
	{#if errorMessage}
		<div class="mb-4 flex items-center gap-2 rounded-lg bg-rose-500/10 border border-rose-500/20 p-2.5 text-xs text-rose-400">
			<AlertCircle size={15} />
			<span>{errorMessage}</span>
		</div>
	{/if}

	<form onsubmit={handleSubmit} class="space-y-4">
		<!-- Selección de Creador y Plataforma -->
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
			<div>
				<label for="creator-select" class="block text-xs font-medium text-gray-300 mb-1">
					Creador / Talento <span class="text-rose-400">*</span>
				</label>
				<select
					id="creator-select"
					bind:value={selectedCreatorId}
					class="w-full rounded-lg bg-[#111827] border border-[#2D3748] px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
					required
				>
					{#each tenantStore.creators as creator}
						<option value={creator.id}>
							{creator.display_name} (@{creator.handle})
						</option>
					{/each}
				</select>
			</div>

			<Select
				label="Plataforma de Transmisión"
				options={[
					{ value: 'twitch', label: 'Twitch' },
					{ value: 'youtube', label: 'YouTube Gaming' },
					{ value: 'kick', label: 'Kick' },
					{ value: 'tiktok', label: 'TikTok Live' }
				]}
				bind:value={platform}
			/>
		</div>

		<!-- Título del Directo y Categoría -->
		<Input
			label="Título de la Sesión / Directo"
			placeholder="ej. SPEEDRUN DE MINECRAFT + CHARLA CON EL CHAT | DÍA 4"
			bind:value={sessionTitle}
			required
		/>

		<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
			<Input
				label="Juego o Categoría Principal"
				placeholder="ej. Just Chatting, Valorant, GTA V"
				bind:value={gameOrCategory}
			/>

			<Input
				label="Fecha y Hora de Emisión (UTC)"
				type="datetime-local"
				bind:value={streamedAt}
				required
			/>

			<Input
				label="Duración (Horas)"
				type="number"
				step="0.1"
				bind:value={durationHours}
				required
			/>
		</div>

		<!-- Métricas de Audiencia -->
		<div class="rounded-xl border border-[#1F2937] bg-[#0A0F1D] p-3.5 space-y-2.5">
			<div class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-400">
				<Users size={14} />
				<span>Métricas de Audiencia y Chat</span>
			</div>

			<div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
				<Input
					label="Avg CCV (Media)"
					type="number"
					bind:value={avgCcv}
					required
				/>

				<Input
					label="Peak Viewers (Pico)"
					type="number"
					bind:value={peakViewers}
					required
				/>

				<Input
					label="Mensajes de Chat"
					type="number"
					bind:value={chatMessagesCount}
				/>

				<Input
					label="Nuevos Followers"
					type="number"
					bind:value={newFollowers}
				/>
			</div>
		</div>

		<!-- Métricas Financieras / Ingresos -->
		<div class="rounded-xl border border-[#1F2937] bg-[#0A0F1D] p-3.5 space-y-2.5">
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-emerald-400">
					<DollarSign size={14} />
					<span>Ingresos & Desglose Financiero</span>
				</div>

				<div class="flex items-center gap-2 text-xs font-mono">
					<span class="text-gray-400">Total:</span>
					<span class="font-bold text-emerald-400">{formatCurrency(calculatedTotalEarnings)}</span>
					<span class="text-gray-500">•</span>
					<span class="text-cyan-400">{formatCurrency(calculatedEarningsPerHour)}/h</span>
				</div>
			</div>

			<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
				<Input
					label="Ingresos Ads / Anuncios ($)"
					type="number"
					step="0.01"
					bind:value={adRevenue}
				/>

				<Input
					label="Suscripciones ($)"
					type="number"
					step="0.01"
					bind:value={subsRevenue}
				/>

				<Input
					label="Donaciones / Bits ($)"
					type="number"
					step="0.01"
					bind:value={donationsRevenue}
				/>
			</div>
		</div>

		<!-- Footer -->
		<div class="pt-3 flex items-center justify-end gap-2 border-t border-[#1F2937]">
			<Button type="button" variant="ghost" size="sm" onclick={onClose} disabled={isSaving}>
				Cancelar
			</Button>
			<Button
				type="submit"
				variant="primary"
				size="sm"
				isLoading={isSaving}
				disabled={!sessionTitle || !selectedCreatorId}
			>
				<Plus size={14} />
				Guardar Sesión en Vivo
			</Button>
		</div>
	</form>
</Modal>
