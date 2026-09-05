<script lang="ts">
	import { analyticsService, type StreamingSession } from '$lib/services/analyticsService';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import type { PlatformType } from '$lib/supabase/database.types';
	import { formatCurrency } from '$lib/utils/formatters';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import { Radio, Save, AlertCircle, DollarSign, Users, Trash2 } from 'lucide-svelte';

	interface Props {
		isOpen: boolean;
		session: StreamingSession | null;
		onClose: () => void;
		onUpdated: () => void;
		onDeleted?: () => void;
	}

	let {
		isOpen = $bindable(false),
		session,
		onClose,
		onUpdated,
		onDeleted
	}: Props = $props();

	let sessionTitle = $state('');
	let gameOrCategory = $state('');
	let platform = $state<PlatformType>('twitch');
	let streamedAt = $state('');
	let durationHours = $state(0);

	// Métricas de Audiencia
	let avgCcv = $state(0);
	let peakViewers = $state(0);
	let chatMessagesCount = $state(0);
	let newFollowers = $state(0);

	// Métricas de Monetización
	let adRevenue = $state(0);
	let subsRevenue = $state(0);
	let donationsRevenue = $state(0);

	let isSaving = $state(false);
	let isDeleting = $state(false);
	let errorMessage = $state<string | null>(null);

	$effect(() => {
		if (session) {
			sessionTitle = session.session_title;
			gameOrCategory = session.game_or_category || '';
			platform = session.platform;
			streamedAt = session.streamed_at
				? new Date(session.streamed_at).toISOString().substring(0, 16)
				: new Date().toISOString().substring(0, 16);
			durationHours = Number((session.duration_seconds / 3600).toFixed(2));
			avgCcv = session.avg_ccv || 0;
			peakViewers = session.peak_viewers || 0;
			chatMessagesCount = session.chat_messages_count || 0;
			newFollowers = session.new_followers || 0;
			adRevenue = Number(session.ad_revenue || 0);
			subsRevenue = Number(session.subs_revenue || 0);
			donationsRevenue = Number(session.donations_revenue || 0);
			errorMessage = null;
		}
	});

	// Cálculos en tiempo real
	let calculatedTotalEarnings = $derived(
		Number((Number(adRevenue || 0) + Number(subsRevenue || 0) + Number(donationsRevenue || 0)).toFixed(2))
	);
	let calculatedEarningsPerHour = $derived(
		durationHours > 0 ? Number((calculatedTotalEarnings / Number(durationHours)).toFixed(2)) : 0
	);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!session) return;
		if (!sessionTitle.trim()) {
			errorMessage = 'Por favor ingresa un título para la sesión.';
			return;
		}

		isSaving = true;
		errorMessage = null;

		const durationSeconds = Math.round(Number(durationHours || 0) * 3600);

		try {
			await analyticsService.updateSession(session.id, {
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

			onUpdated();
			onClose();
		} catch (err: any) {
			console.error('Error updating streaming session:', err);
			errorMessage = err.message || 'Error al actualizar la sesión de streaming.';
		} finally {
			isSaving = false;
		}
	}

	async function handleDelete() {
		if (!session) return;
		if (!confirm(`¿Estás seguro de eliminar la sesión "${session.session_title}"?`)) return;

		isDeleting = true;
		errorMessage = null;

		try {
			await analyticsService.deleteSession(session.id);
			if (onDeleted) onDeleted();
			else onUpdated();
			onClose();
		} catch (err: any) {
			console.error('Error deleting session:', err);
			errorMessage = err.message || 'Error al eliminar la sesión.';
		} finally {
			isDeleting = false;
		}
	}
</script>

<Modal
	{isOpen}
	title="Editar Sesión de Transmisión en Vivo"
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
		<!-- Título del Directo y Plataforma -->
		<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
			<div class="sm:col-span-2">
				<Input
					label="Título de la Sesión / Directo"
					placeholder="ej. SPEEDRUN DE MINECRAFT | DÍA 4"
					bind:value={sessionTitle}
					required
				/>
			</div>

			<Select
				label="Plataforma"
				options={[
					{ value: 'twitch', label: 'Twitch' },
					{ value: 'youtube', label: 'YouTube Gaming' },
					{ value: 'kick', label: 'Kick' },
					{ value: 'tiktok', label: 'TikTok Live' }
				]}
				bind:value={platform}
			/>
		</div>

		<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
			<Input
				label="Juego / Categoría"
				placeholder="ej. Just Chatting, Valorant"
				bind:value={gameOrCategory}
			/>

			<Input
				label="Fecha y Hora de Emisión"
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
					label="Ingresos Ads ($)"
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
					label="Donaciones ($)"
					type="number"
					step="0.01"
					bind:value={donationsRevenue}
				/>
			</div>
		</div>

		<!-- Footer -->
		<div class="pt-3 flex items-center justify-between border-t border-[#1F2937]">
			<Button
				type="button"
				variant="danger"
				size="sm"
				onclick={handleDelete}
				isLoading={isDeleting}
				disabled={isSaving}
			>
				<Trash2 size={14} />
				Eliminar
			</Button>

			<div class="flex items-center gap-2">
				<Button type="button" variant="ghost" size="sm" onclick={onClose} disabled={isSaving || isDeleting}>
					Cancelar
				</Button>
				<Button
					type="submit"
					variant="primary"
					size="sm"
					isLoading={isSaving}
					disabled={!sessionTitle.trim() || isDeleting}
				>
					<Save size={14} />
					Guardar Cambios
				</Button>
			</div>
		</div>
	</form>
</Modal>
