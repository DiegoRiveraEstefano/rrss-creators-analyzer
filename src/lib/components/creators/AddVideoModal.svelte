<script lang="ts">
	import { videoService } from '$lib/services/videoService';
	import { analyticsService, type StreamingSession } from '$lib/services/analyticsService';
	import { creatorService, type CreatorWithChannels } from '$lib/services/creatorService';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import type { PlatformType } from '$lib/supabase/database.types';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import { Video, Plus, AlertCircle, Radio, Link2, Film, Sparkles, User } from 'lucide-svelte';

	interface Props {
		isOpen: boolean;
		organizationId: string;
		creatorId?: string | null;
		channelId?: string | null;
		onClose: () => void;
		onAdded: () => void;
	}

	let {
		isOpen = $bindable(false),
		organizationId,
		creatorId,
		channelId,
		onClose,
		onAdded
	}: Props = $props();

	// Tab activa del formulario
	let activeTab = $state<'video' | 'publication' | 'relation'>('video');

	// Creador seleccionado
	let selectedCreatorId = $state('');
	let availableCreators = $state<CreatorWithChannels[]>([]);

	// 1. Entidad Video (Master)
	let title = $state('');
	let internalName = $state('');
	let description = $state('');
	let tagsString = $state('highlights, stream, gaming');
	let category = $state('Gaming');
	let durationMinutes = $state(18);
	let productionCost = $state(0);

	// 2. Entidad Publicación Inicial
	let platform = $state<PlatformType>('youtube');
	let publicationType = $state('standard');
	let postUrl = $state('');
	let thumbnailUrl = $state('');
	let publishedAt = $state(new Date().toISOString().substring(0, 16));
	let viewsCount = $state(125000);
	let likesCount = $state(8400);
	let commentsCount = $state(620);
	let sharesCount = $state(210);
	let estimatedRevenue = $state(320);

	// 3. Entidad Relación / Trazabilidad
	let hasRelation = $state(false);
	let relationType = $state('derived_from_live');
	let selectedSessionId = $state<string>('');
	let relationNotes = $state('');

	// Lista de directos del creador para vincular
	let creatorSessions = $state<StreamingSession[]>([]);
	let isSaving = $state(false);
	let errorMessage = $state<string | null>(null);

	// Carga reactiva de creadores y selección inicial
	$effect(() => {
		if (isOpen && organizationId) {
			loadCreators();
		}
	});

	async function loadCreators() {
		try {
			if (tenantStore.creators.length > 0) {
				availableCreators = tenantStore.creators;
			} else {
				availableCreators = await creatorService.getCreators(organizationId);
			}

			if (creatorId) {
				selectedCreatorId = creatorId;
			} else if (!selectedCreatorId && availableCreators.length > 0) {
				selectedCreatorId = tenantStore.selectedCreatorId || availableCreators[0].id;
			}
		} catch (err) {
			console.error('Error loading creators for AddVideoModal:', err);
		}
	}

	$effect(() => {
		if (isOpen && organizationId && selectedCreatorId) {
			loadCreatorSessions(selectedCreatorId);
		}
	});

	async function loadCreatorSessions(cId: string) {
		try {
			creatorSessions = await analyticsService.getSessions(organizationId, cId);
		} catch (err) {
			console.error('Error loading creator sessions for relation select:', err);
		}
	}

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		const effectiveCreatorId = selectedCreatorId || creatorId || availableCreators[0]?.id;

		if (!title.trim()) {
			errorMessage = 'Por favor ingresa un título para el video.';
			activeTab = 'video';
			return;
		}

		if (!organizationId || !effectiveCreatorId) {
			errorMessage = 'Por favor selecciona un creador para asociar el video.';
			activeTab = 'video';
			return;
		}

		isSaving = true;
		errorMessage = null;

		const durationSeconds = Math.round((Number(durationMinutes) || 0) * 60);
		const tags = tagsString
			.split(',')
			.map((t) => t.trim())
			.filter(Boolean);

		try {
			await videoService.createVideoWithDetails({
				video: {
					organization_id: organizationId,
					creator_id: effectiveCreatorId,
					title: title.trim(),
					internal_name: internalName.trim() || null,
					description: description.trim() || null,
					tags,
					category: category.trim() || null,
					duration_seconds: durationSeconds,
					production_cost: Number(productionCost) || 0,
					status: 'published'
				},
				publication: {
					platform,
					publication_type: publicationType,
					post_url: postUrl.trim() || null,
					thumbnail_url: thumbnailUrl.trim() || null,
					published_at: new Date(publishedAt).toISOString(),
					views_count: Number(viewsCount) || 0,
					likes_count: Number(likesCount) || 0,
					comments_count: Number(commentsCount) || 0,
					shares_count: Number(sharesCount) || 0,
					estimated_revenue: Number(estimatedRevenue) || 0
				},
				relation:
					hasRelation && selectedSessionId
						? {
								target_session_id: selectedSessionId,
								relation_type: relationType,
								description: relationNotes.trim() || null
							}
						: undefined
			});

			onAdded();
			onClose();

			// Reset
			title = '';
			internalName = '';
			description = '';
			postUrl = '';
			thumbnailUrl = '';
			hasRelation = false;
			selectedSessionId = '';
			relationNotes = '';
			activeTab = 'video';
		} catch (err: any) {
			console.error('Error saving video:', err);
			errorMessage = err.message || 'Error al guardar el video en la base de datos.';
		} finally {
			isSaving = false;
		}
	}
</script>

<Modal
	{isOpen}
	title="Registrar Nuevo Video de Contenido"
	maxWidth="2xl"
	{onClose}
>
	{#if errorMessage}
		<div class="mb-4 flex items-center gap-2 rounded-lg bg-rose-500/10 border border-rose-500/20 p-2.5 text-xs text-rose-400">
			<AlertCircle size={15} />
			<span>{errorMessage}</span>
		</div>
	{/if}

	<!-- Tabs del Formulario -->
	<div class="flex items-center gap-2 border-b border-[#1F2937] mb-4 pb-2 text-xs">
		<button
			type="button"
			onclick={() => (activeTab = 'video')}
			class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-colors {activeTab === 'video'
				? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-semibold'
				: 'text-gray-400 hover:text-white'}"
		>
			<Film size={14} />
			<span>1. Activo de Video</span>
		</button>

		<button
			type="button"
			onclick={() => (activeTab = 'publication')}
			class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-colors {activeTab === 'publication'
				? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-semibold'
				: 'text-gray-400 hover:text-white'}"
		>
			<Sparkles size={14} />
			<span>2. Publicación & Stats</span>
		</button>

		<button
			type="button"
			onclick={() => (activeTab = 'relation')}
			class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-colors {activeTab === 'relation'
				? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-semibold'
				: 'text-gray-400 hover:text-white'}"
		>
			<Link2 size={14} />
			<span>3. Relación / Live ({hasRelation ? 'Activo' : 'Opcional'})</span>
		</button>
	</div>

	<form onsubmit={handleSubmit} class="space-y-4">
		<!-- TAB 1: Master Video Info -->
		{#if activeTab === 'video'}
			<div class="space-y-3 animate-in fade-in duration-100">
				<div>
					<label for="creator-picker" class="block text-xs font-medium text-gray-300 mb-1">
						Creador / Talento Representado <span class="text-rose-400">*</span>
					</label>
					<select
						id="creator-picker"
						bind:value={selectedCreatorId}
						class="w-full rounded-lg bg-[#111827] border border-[#2D3748] px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
						required
					>
						<option value="" disabled>-- Selecciona un Creador del Roster --</option>
						{#each availableCreators as c}
							<option value={c.id}>
								{c.display_name} (@{c.handle}) - {c.primary_platform}
							</option>
						{/each}
					</select>
				</div>

				<Input
					label="Título Principal del Video"
					placeholder="ej. CLIPS TOP DE LA SEMANA - FINAL DEL TORNEO"
					bind:value={title}
					required
				/>

				<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
					<Input
						label="Nombre Interno / ID de Proyecto"
						placeholder="ej. PROJ-2026-Q3-EP04"
						bind:value={internalName}
					/>

					<Input
						label="Categoría / Temática"
						placeholder="ej. Gaming, Reaction, Vlog, Tutorial"
						bind:value={category}
					/>
				</div>

				<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
					<Input
						label="Duración Estimada (Minutos)"
						type="number"
						step="0.1"
						bind:value={durationMinutes}
						required
					/>

					<Input
						label="Costo de Producción ($)"
						type="number"
						step="0.01"
						placeholder="0.00"
						bind:value={productionCost}
					/>
				</div>

				<Input
					label="Etiquetas / Tags (separados por coma)"
					placeholder="gaming, twitch, reaction, highlight"
					bind:value={tagsString}
				/>
			</div>
		{/if}

		<!-- TAB 2: Publication & Metrics -->
		{#if activeTab === 'publication'}
			<div class="space-y-3 animate-in fade-in duration-100">
				<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
					<Select
						label="Plataforma de Publicación"
						options={[
							{ value: 'youtube', label: 'YouTube' },
							{ value: 'tiktok', label: 'TikTok' },
							{ value: 'twitch', label: 'Twitch (VOD / Clip)' },
							{ value: 'kick', label: 'Kick (VOD)' }
						]}
						bind:value={platform}
					/>

					<Select
						label="Formato / Tipo"
						options={[
							{ value: 'standard', label: 'Video Estándar (Horizontal)' },
							{ value: 'short/reel', label: 'Short / Reel (Vertical)' },
							{ value: 'vod', label: 'VOD Completo' },
							{ value: 'clip', label: 'Clip Corto' }
						]}
						bind:value={publicationType}
					/>

					<Input
						label="Fecha y Hora de Publicación"
						type="datetime-local"
						bind:value={publishedAt}
						required
					/>
				</div>

				<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
					<Input
						label="URL Pública del Video / Post"
						placeholder="https://youtube.com/watch?v=..."
						bind:value={postUrl}
					/>

					<Input
						label="URL de Miniatura (Thumbnail)"
						placeholder="https://..."
						bind:value={thumbnailUrl}
					/>
				</div>

				<div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
					<Input
						label="Vistas (Views)"
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
						label="Ingresos ($)"
						type="number"
						step="0.01"
						bind:value={estimatedRevenue}
					/>
				</div>
			</div>
		{/if}

		<!-- TAB 3: Relation / Live Provenance -->
		{#if activeTab === 'relation'}
			<div class="space-y-4 animate-in fade-in duration-100">
				<div class="flex items-center gap-3 p-3 rounded-xl bg-indigo-600/10 border border-indigo-500/20">
					<input
						type="checkbox"
						id="has-rel"
						bind:checked={hasRelation}
						class="h-4 w-4 rounded border-gray-700 bg-gray-900 text-indigo-600 focus:ring-indigo-500"
					/>
					<label for="has-rel" class="text-xs text-gray-200 cursor-pointer">
						Este video proviene de una transmisión en directo o se relaciona con otro contenido
					</label>
				</div>

				{#if hasRelation}
					<div class="space-y-3 pl-2 border-l-2 border-indigo-500/40">
						<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
							<Select
								label="Tipo de Relación"
								options={[
									{ value: 'derived_from_live', label: 'Derivado / Extraído de un Live' },
									{ value: 'highlight_clip', label: 'Clip Destacado de Live' },
									{ value: 'continuation', label: 'Continuación / Parte 2' },
									{ value: 'sequel', label: 'Secuela' },
									{ value: 'reference', label: 'Referencia Cruzada' }
								]}
								bind:value={relationType}
							/>

							<div>
								<label for="session-origin-select" class="block text-xs font-medium text-gray-300 mb-1">
									Sesión de Streaming de Origen
								</label>
								<select
									id="session-origin-select"
									bind:value={selectedSessionId}
									class="w-full rounded-lg bg-[#111827] border border-[#2D3748] px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
								>
									<option value="">-- Seleccionar Sesión de Streaming --</option>
									{#each creatorSessions as session}
										<option value={session.id}>
											{session.session_title} ({new Date(session.streamed_at).toLocaleDateString()}) - {session.platform}
										</option>
									{/each}
								</select>
							</div>
						</div>

						<Input
							label="Notas de la Relación / Marcador de Tiempo"
							placeholder="ej. Extraído del minuto 45:10 durante la batalla final"
							bind:value={relationNotes}
						/>
					</div>
				{/if}
			</div>
		{/if}

		<div class="pt-3 flex items-center justify-between border-t border-[#1F2937]">
			<div class="flex items-center gap-2">
				{#if activeTab !== 'video'}
					<Button
						type="button"
						variant="secondary"
						size="sm"
						onclick={() => (activeTab = activeTab === 'relation' ? 'publication' : 'video')}
					>
						Anterior
					</Button>
				{/if}
				{#if activeTab !== 'relation'}
					<Button
						type="button"
						variant="secondary"
						size="sm"
						onclick={() => (activeTab = activeTab === 'video' ? 'publication' : 'relation')}
					>
						Siguiente Paso
					</Button>
				{/if}
			</div>

			<div class="flex items-center gap-2">
				<Button type="button" variant="ghost" size="sm" onclick={onClose} disabled={isSaving}>
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
					Guardar Video Completo
				</Button>
			</div>
		</div>
	</form>
</Modal>
