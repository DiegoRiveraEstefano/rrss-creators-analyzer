<script lang="ts">
	import { creatorService, type CreatorWithChannels } from '$lib/services/creatorService';
	import type { PlatformType, CreatorStatus } from '$lib/supabase/database.types';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import { Save, AlertCircle } from 'lucide-svelte';

	interface Props {
		isOpen: boolean;
		creator: CreatorWithChannels | null;
		onClose: () => void;
		onUpdated: () => void;
	}

	let { isOpen = $bindable(false), creator, onClose, onUpdated }: Props = $props();

	let displayName = $state('');
	let handle = $state('');
	let avatarUrl = $state('');
	let bio = $state('');
	let primaryPlatform = $state<PlatformType>('twitch');
	let status = $state<CreatorStatus>('active');

	let isSaving = $state(false);
	let errorMessage = $state<string | null>(null);

	$effect(() => {
		if (creator) {
			displayName = creator.display_name;
			handle = creator.handle;
			avatarUrl = creator.avatar_url || '';
			bio = creator.bio || '';
			primaryPlatform = creator.primary_platform;
			status = creator.status;
			errorMessage = null;
		}
	});

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!creator) return;

		isSaving = true;
		errorMessage = null;
		try {
			await creatorService.updateCreator(creator.id, {
				display_name: displayName,
				handle: handle.replace('@', ''),
				avatar_url: avatarUrl || null,
				bio: bio || null,
				primary_platform: primaryPlatform,
				status
			});
			onUpdated();
			onClose();
		} catch (err: any) {
			errorMessage = err.message || 'Error al actualizar el creador.';
		} finally {
			isSaving = false;
		}
	}
</script>

<Modal
	{isOpen}
	title="Editar Perfil de Creador"
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
			label="Nombre de Creador / Marca"
			placeholder="ej. Ibai Llanos"
			bind:value={displayName}
			required
		/>

		<Input
			label="Usuario / Handle"
			placeholder="ej. ibai"
			bind:value={handle}
			hint="Sin el símbolo @"
			required
		/>

		<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
			<Select
				label="Plataforma Principal"
				options={[
					{ value: 'twitch', label: 'Twitch' },
					{ value: 'youtube', label: 'YouTube Gaming' },
					{ value: 'kick', label: 'Kick' },
					{ value: 'tiktok', label: 'TikTok Live' }
				]}
				bind:value={primaryPlatform}
			/>

			<Select
				label="Estado del Creador"
				options={[
					{ value: 'active', label: 'Activo' },
					{ value: 'inactive', label: 'Inactivo' },
					{ value: 'suspended', label: 'Suspendido' }
				]}
				bind:value={status}
			/>
		</div>

		<Input
			label="URL del Avatar / Foto"
			placeholder="https://..."
			bind:value={avatarUrl}
		/>

		<Input
			label="Biografía / Descripción"
			placeholder="Descripción del talento y categorías principales..."
			bind:value={bio}
		/>

		<div class="pt-2 flex items-center justify-end gap-3 border-t border-[#1F2937]">
			<Button variant="ghost" size="sm" onclick={onClose} disabled={isSaving}>
				Cancelar
			</Button>
			<Button
				type="submit"
				variant="primary"
				size="sm"
				isLoading={isSaving}
				disabled={!displayName || !handle}
			>
				<Save size={14} />
				Guardar Cambios
			</Button>
		</div>
	</form>
</Modal>
