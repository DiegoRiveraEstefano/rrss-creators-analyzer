<script lang="ts">
	import { videoService } from '$lib/services/videoService';
	import type { PlatformType } from '$lib/supabase/database.types';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import { Video, Plus, AlertCircle } from 'lucide-svelte';

	interface Props {
		isOpen: boolean;
		organizationId: string;
		creatorId: string;
		channelId?: string | null;
		onClose: () => void;
		onAdded: () => void;
	}

	let { isOpen = $bindable(false), organizationId, creatorId, channelId, onClose, onAdded }: Props = $props();

	let title = $state('');
	let platform = $state<PlatformType>('youtube');
	let videoUrl = $state('');
	let thumbnailUrl = $state('');
	let publishedAt = $state(new Date().toISOString().substring(0, 16));
	let durationMinutes = $state(18);
	let viewsCount = $state(125000);
	let likesCount = $state(8400);
	let commentsCount = $state(620);
	let sharesCount = $state(210);
	let estimatedRevenue = $state(320);

	let isSaving = $state(false);
	let errorMessage = $state<string | null>(null);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!title || !organizationId || !creatorId) return;

		isSaving = true;
		errorMessage = null;

		const durationSeconds = Math.round((Number(durationMinutes) || 0) * 60);

		try {
			await videoService.createVideo({
				organization_id: organizationId,
				creator_id: creatorId,
				channel_id: channelId || null,
				title,
				platform,
				video_url: videoUrl || null,
				thumbnail_url: thumbnailUrl || null,
				published_at: new Date(publishedAt).toISOString(),
				duration_seconds: durationSeconds,
				views_count: Number(viewsCount) || 0,
				likes_count: Number(likesCount) || 0,
				comments_count: Number(commentsCount) || 0,
				shares_count: Number(sharesCount) || 0,
				estimated_revenue: Number(estimatedRevenue) || 0
			});

			onAdded();
			onClose();
			// Reset
			title = '';
			videoUrl = '';
		} catch (err: any) {
			errorMessage = err.message || 'Error al registrar el video subido.';
		} finally {
			isSaving = false;
		}
	}
</script>

<Modal
	{isOpen}
	title="Ingestar Video Subido (YouTube / TikTok / VOD)"
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
			label="Título del Video"
			placeholder="ej. REACCIONANDO A LOS MEJORES MOMENTOS DE LA SEMANA"
			bind:value={title}
			required
		/>

		<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
			<Select
				label="Plataforma"
				options={[
					{ value: 'youtube', label: 'YouTube' },
					{ value: 'tiktok', label: 'TikTok' },
					{ value: 'twitch', label: 'Twitch VOD / Clip' },
					{ value: 'kick', label: 'Kick VOD' }
				]}
				bind:value={platform}
			/>

			<Input
				label="Fecha de Publicación"
				type="datetime-local"
				bind:value={publishedAt}
				required
			/>

			<Input
				label="Duración (Minutos)"
				type="number"
				step="0.1"
				bind:value={durationMinutes}
				required
			/>
		</div>

		<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
			<Input
				label="URL del Video (Enlace público)"
				placeholder="https://youtube.com/watch?v=..."
				bind:value={videoUrl}
			/>

			<Input
				label="URL de Miniatura / Thumbnail"
				placeholder="https://..."
				bind:value={thumbnailUrl}
			/>
		</div>

		<div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
			<Input
				label="Visualizaciones (Views)"
				type="number"
				bind:value={viewsCount}
				required
			/>

			<Input
				label="Likes"
				type="number"
				bind:value={likesCount}
			/>

			<Input
				label="Comentarios"
				type="number"
				bind:value={commentsCount}
			/>

			<Input
				label="Ingresos Estimados ($)"
				type="number"
				step="0.01"
				bind:value={estimatedRevenue}
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
				disabled={!title}
			>
				<Plus size={14} />
				Guardar Video en Supabase
			</Button>
		</div>
	</form>
</Modal>
