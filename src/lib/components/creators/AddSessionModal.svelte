<script lang="ts">
	import { analyticsService } from '$lib/services/analyticsService';
	import type { PlatformType } from '$lib/supabase/database.types';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import { Radio, Plus, AlertCircle } from 'lucide-svelte';

	interface Props {
		isOpen: boolean;
		organizationId: string;
		creatorId: string;
		channelId?: string | null;
		onClose: () => void;
		onAdded: () => void;
	}

	let { isOpen = $bindable(false), organizationId, creatorId, channelId, onClose, onAdded }: Props = $props();

	let sessionTitle = $state('');
	let gameOrCategory = $state('Just Chatting');
	let platform = $state<PlatformType>('twitch');
	let streamedAt = $state(new Date().toISOString().substring(0, 16));
	let durationHours = $state(3.5);
	let peakViewers = $state(25000);
	let avgCcv = $state(18000);
	let chatMessagesCount = $state(45000);
	let newFollowers = $state(1200);
	let adRevenue = $state(350);
	let subsRevenue = $state(800);
	let donationsRevenue = $state(150);

	let isSaving = $state(false);
	let errorMessage = $state<string | null>(null);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!sessionTitle || !organizationId || !creatorId) return;

		isSaving = true;
		errorMessage = null;

		const durationSeconds = Math.round((Number(durationHours) || 0) * 3600);
		const totalEarnings = Number(adRevenue || 0) + Number(subsRevenue || 0) + Number(donationsRevenue || 0);
		const earningsPerHour = durationHours > 0 ? Number((totalEarnings / Number(durationHours)).toFixed(2)) : 0;

		try {
			await analyticsService.addSession({
				organization_id: organizationId,
				creator_id: creatorId,
				channel_id: channelId || null,
				session_title: sessionTitle,
				game_or_category: gameOrCategory,
				platform,
				streamed_at: new Date(streamedAt).toISOString(),
				duration_seconds: durationSeconds,
				peak_viewers: Number(peakViewers) || 0,
				avg_ccv: Number(avgCcv) || 0,
				chat_messages_count: Number(chatMessagesCount) || 0,
				new_followers: Number(newFollowers) || 0,
				ad_revenue: Number(adRevenue) || 0,
				subs_revenue: Number(subsRevenue) || 0,
				donations_revenue: Number(donationsRevenue) || 0,
				total_earnings: totalEarnings,
				earnings_per_hour: earningsPerHour
			});

			onAdded();
			onClose();
			// Reset
			sessionTitle = '';
		} catch (err: any) {
			errorMessage = err.message || 'Error al registrar la sesión de streaming.';
		} finally {
			isSaving = false;
		}
	}
</script>

<Modal
	{isOpen}
	title="Ingestar Sesión de Streaming en Directo"
	maxWidth="xl"
	{onClose}
>
	{#if errorMessage}
		<div class="mb-4 flex items-center gap-2 rounded-lg bg-rose-500/10 border border-rose-500/20 p-2.5 text-xs text-rose-400">
			<AlertCircle size={15} />
			<span>{errorMessage}</span>
		</div>
	{/if}

	<form onsubmit={handleSubmit} class="space-y-4">
		<Input
			label="Título de la Transmisión"
			placeholder="ej. ESPECIAL 1M SEGUIDORES + TORNEO"
			bind:value={sessionTitle}
			required
		/>

		<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
			<Input
				label="Juego / Categoría"
				placeholder="Just Chatting, VALORANT..."
				bind:value={gameOrCategory}
			/>

			<Select
				label="Plataforma"
				options={[
					{ value: 'twitch', label: 'Twitch' },
					{ value: 'youtube', label: 'YouTube' },
					{ value: 'kick', label: 'Kick' },
					{ value: 'tiktok', label: 'TikTok' }
				]}
				bind:value={platform}
			/>

			<Input
				label="Fecha y Hora de Emisión"
				type="datetime-local"
				bind:value={streamedAt}
				required
			/>
		</div>

		<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
			<Input
				label="Duración (Horas)"
				type="number"
				step="0.1"
				bind:value={durationHours}
				required
			/>

			<Input
				label="Media Concurrencia (CCV)"
				type="number"
				bind:value={avgCcv}
				required
			/>

			<Input
				label="Pico Máximo de Viewers"
				type="number"
				bind:value={peakViewers}
				required
			/>
		</div>

		<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
			<Input
				label="Ingresos Ads ($)"
				type="number"
				step="0.01"
				bind:value={adRevenue}
			/>

			<Input
				label="Ingresos Subs ($)"
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

		<div class="pt-2 flex items-center justify-end gap-3 border-t border-[#1F2937]">
			<Button variant="ghost" size="sm" onclick={onClose} disabled={isSaving}>
				Cancelar
			</Button>
			<Button
				type="submit"
				variant="primary"
				size="sm"
				isLoading={isSaving}
				disabled={!sessionTitle}
			>
				<Plus size={14} />
				Guardar Sesión en Supabase
			</Button>
		</div>
	</form>
</Modal>
