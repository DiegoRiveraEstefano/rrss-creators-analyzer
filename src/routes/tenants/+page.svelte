<script lang="ts">
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import { tenantService, type OrganizationWithStats, type TenantMemberDetail } from '$lib/services/tenantService';
	import type { MemberRole } from '$lib/supabase/database.types';
	import { formatDate } from '$lib/utils/formatters';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import {
		Building2,
		Plus,
		Settings,
		Users,
		ShieldCheck,
		Radio,
		CheckCircle2,
		ExternalLink,
		UserPlus,
		Trash2,
		Sparkles
	} from 'lucide-svelte';

	let isCreateModalOpen = $state(false);
	let isEditModalOpen = $state(false);
	let isMembersModalOpen = $state(false);

	// Create Tenant Form State
	let newOrgName = $state('');
	let newOrgSlug = $state('');
	let newOrgPlan = $state('pro');
	let isCreatingOrg = $state(false);

	// Edit Tenant Form State
	let editOrgId = $state('');
	let editOrgName = $state('');
	let editOrgPlan = $state('');
	let editOrgLogoUrl = $state('');
	let isEditingOrg = $state(false);

	// Members Modal State
	let selectedOrgForMembers = $state<OrganizationWithStats | null>(null);
	let membersList = $state<TenantMemberDetail[]>([]);
	let isLoadingMembers = $state(false);
	let newMemberEmail = $state('');
	let newMemberRole = $state<MemberRole>('manager');
	let isAddingMember = $state(false);

	function autoGenerateSlug(name: string) {
		return name
			.toLowerCase()
			.trim()
			.replace(/[\s_]+/g, '-')
			.replace(/[^a-z0-9-]/g, '');
	}

	function handleNameInput(e: Event) {
		const target = e.target as HTMLInputElement;
		newOrgName = target.value;
		newOrgSlug = autoGenerateSlug(newOrgName);
	}

	async function handleCreateOrganization() {
		if (!newOrgName || !newOrgSlug) return;
		isCreatingOrg = true;
		try {
			await tenantStore.createOrganization({
				name: newOrgName,
				slug: newOrgSlug,
				plan: newOrgPlan
			});
			isCreateModalOpen = false;
			newOrgName = '';
			newOrgSlug = '';
			newOrgPlan = 'pro';
		} catch (error) {
			console.error('Error creating organization:', error);
		} finally {
			isCreatingOrg = false;
		}
	}

	function openEditModal(org: OrganizationWithStats) {
		editOrgId = org.id;
		editOrgName = org.name;
		editOrgPlan = org.plan;
		editOrgLogoUrl = org.logo_url || '';
		isEditModalOpen = true;
	}

	async function handleSaveEditOrganization() {
		if (!editOrgId || !editOrgName) return;
		isEditingOrg = true;
		try {
			await tenantStore.updateOrganization(editOrgId, {
				name: editOrgName,
				plan: editOrgPlan,
				logo_url: editOrgLogoUrl || null
			});
			isEditModalOpen = false;
		} catch (error) {
			console.error('Error updating organization:', error);
		} finally {
			isEditingOrg = false;
		}
	}

	async function openMembersModal(org: OrganizationWithStats) {
		selectedOrgForMembers = org;
		isMembersModalOpen = true;
		isLoadingMembers = true;
		try {
			membersList = await tenantService.getMembers(org.id);
		} catch (error) {
			console.error('Error loading members:', error);
		} finally {
			isLoadingMembers = false;
		}
	}

	async function handleAddMember() {
		if (!selectedOrgForMembers || !newMemberEmail) return;
		isAddingMember = true;
		try {
			await tenantService.addMember(selectedOrgForMembers.id, {
				email: newMemberEmail,
				role: newMemberRole
			});
			membersList = await tenantService.getMembers(selectedOrgForMembers.id);
			newMemberEmail = '';
		} catch (error) {
			console.error('Error adding member:', error);
		} finally {
			isAddingMember = false;
		}
	}

	async function handleRemoveMember(memberId: string) {
		if (!selectedOrgForMembers) return;
		await tenantService.removeMember(memberId);
		membersList = await tenantService.getMembers(selectedOrgForMembers.id);
	}
</script>

<svelte:head>
	<title>Gestión de Organizaciones | RRSS Creators Analyzer</title>
</svelte:head>

<div class="space-y-6">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<Building2 class="text-indigo-400" size={24} />
				<span>Organizaciones y Espacios de Trabajo (Tenants)</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				Aislamiento multi-tenant con seguridad RLS. Cambia de espacio de trabajo o administra miembros y suscripciones.
			</p>
		</div>

		<Button variant="primary" size="md" onclick={() => (isCreateModalOpen = true)}>
			<Plus size={16} />
			Nueva Organización / Agencia
		</Button>
	</div>

	<!-- Grid de Tenants / Organizaciones -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
		{#each tenantStore.organizations as org}
			{@const isCurrent = tenantStore.currentOrg?.id === org.id}

			<div
				class="relative overflow-hidden rounded-2xl bg-[#111827] border p-6 shadow-xl flex flex-col justify-between transition-all duration-200 {isCurrent
					? 'border-indigo-500/60 shadow-indigo-500/10 ring-1 ring-indigo-500/30'
					: 'border-[#1F2937] hover:border-gray-700'}"
			>
				<div>
					<!-- Header con Logo / Avatar y Estado Activo -->
					<div class="flex items-start justify-between">
						<div class="flex items-center gap-3.5">
							<div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 text-indigo-300 border border-indigo-500/30 font-bold text-lg">
								{#if org.logo_url}
									<img src={org.logo_url} alt={org.name} class="h-full w-full object-cover rounded-2xl" />
								{:else}
									{org.name.substring(0, 2).toUpperCase()}
								{/if}
							</div>

							<div>
								<h3 class="text-base font-bold text-white flex items-center gap-1.5">
									{org.name}
								</h3>
								<div class="text-xs text-gray-400 font-mono">
									slug: {org.slug}
								</div>
							</div>
						</div>

						<Badge
							variant={org.plan === 'enterprise' ? 'purple' : org.plan === 'pro' ? 'indigo' : 'neutral'}
							size="sm"
							class="uppercase font-mono"
						>
							{org.plan}
						</Badge>
					</div>

					<!-- Métricas del Tenant -->
					<div class="mt-5 grid grid-cols-2 gap-2 rounded-xl bg-[#090D16] border border-[#1F2937] p-3 text-center">
						<div>
							<div class="text-[10px] uppercase tracking-wider text-gray-400 font-medium">Talentos Roster</div>
							<div class="text-sm font-bold text-white font-mono mt-0.5">
								{org.creatorsCount || 4} creadores
							</div>
						</div>
						<div>
							<div class="text-[10px] uppercase tracking-wider text-gray-400 font-medium">Equipo / Miembros</div>
							<div class="text-sm font-bold text-indigo-400 font-mono mt-0.5">
								{org.membersCount || 2} usuarios
							</div>
						</div>
					</div>

					<div class="mt-3 flex items-center justify-between text-[11px] text-gray-400 font-mono">
						<span>Rol: <b class="text-gray-200 capitalize">{org.role === 'agency_owner' ? 'Propietario' : 'Mánager'}</b></span>
						<span>Creado: {formatDate(org.created_at)}</span>
					</div>
				</div>

				<!-- Botones de Acción -->
				<div class="mt-6 flex items-center gap-2 pt-4 border-t border-[#1F2937]">
					{#if isCurrent}
						<Button variant="secondary" size="sm" class="flex-1 border-indigo-500/40 text-indigo-300" disabled>
							<CheckCircle2 size={14} class="text-indigo-400" />
							Espacio Activo
						</Button>
					{:else}
						<Button
							variant="primary"
							size="sm"
							class="flex-1"
							onclick={() => tenantStore.selectOrganization(org.id)}
						>
							Activar Espacio
						</Button>
					{/if}

					<Button
						variant="outline"
						size="sm"
						onclick={() => openMembersModal(org)}
						title="Gestionar Miembros"
					>
						<Users size={14} />
					</Button>

					<Button
						variant="outline"
						size="sm"
						onclick={() => openEditModal(org)}
						title="Configurar Organización"
					>
						<Settings size={14} />
					</Button>
				</div>
			</div>
		{/each}
	</div>
</div>

<!-- Modal para Crear Organización -->
<Modal
	isOpen={isCreateModalOpen}
	title="Crear Nueva Organización / Agencia"
	onClose={() => (isCreateModalOpen = false)}
>
	<div class="space-y-4">
		<Input
			label="Nombre de la Organización"
			placeholder="ej. Nexus Creators Agency"
			value={newOrgName}
			oninput={handleNameInput}
			required
		/>

		<Input
			label="Slug Identificador (URL & RLS Tenant Key)"
			placeholder="nexus-creators"
			bind:value={newOrgSlug}
			hint="Identificador único en minúsculas para la base de datos"
			required
		/>

		<Select
			label="Plan de Suscripción"
			options={[
				{ value: 'standard', label: 'Standard (Hasta 5 Creadores)' },
				{ value: 'pro', label: 'Pro (Hasta 20 Creadores + Smart Importer)' },
				{ value: 'enterprise', label: 'Enterprise (Creadores Ilimitados + RLS Avanzado)' }
			]}
			bind:value={newOrgPlan}
		/>
	</div>

	{#snippet footer()}
		<Button variant="ghost" size="sm" onclick={() => (isCreateModalOpen = false)}>
			Cancelar
		</Button>
		<Button
			variant="primary"
			size="sm"
			isLoading={isCreatingOrg}
			disabled={!newOrgName || !newOrgSlug}
			onclick={handleCreateOrganization}
		>
			<Plus size={15} />
			Crear Espacio de Trabajo
		</Button>
	{/snippet}
</Modal>

<!-- Modal para Editar Organización -->
<Modal
	isOpen={isEditModalOpen}
	title="Configuración de la Organización"
	onClose={() => (isEditModalOpen = false)}
>
	<div class="space-y-4">
		<Input
			label="Nombre de la Organización"
			placeholder="Nombre de la agencia"
			bind:value={editOrgName}
			required
		/>

		<Input
			label="URL del Logotipo"
			placeholder="https://..."
			bind:value={editOrgLogoUrl}
			hint="Enlace a imagen o logo institucional"
		/>

		<Select
			label="Plan de Suscripción"
			options={[
				{ value: 'standard', label: 'Standard' },
				{ value: 'pro', label: 'Pro' },
				{ value: 'enterprise', label: 'Enterprise' }
			]}
			bind:value={editOrgPlan}
		/>
	</div>

	{#snippet footer()}
		<Button variant="ghost" size="sm" onclick={() => (isEditModalOpen = false)}>
			Cancelar
		</Button>
		<Button
			variant="primary"
			size="sm"
			isLoading={isEditingOrg}
			disabled={!editOrgName}
			onclick={handleSaveEditOrganization}
		>
			Guardar Configuración
		</Button>
	{/snippet}
</Modal>

<!-- Modal para Gestionar Miembros -->
<Modal
	isOpen={isMembersModalOpen}
	title={`Miembros de ${selectedOrgForMembers?.name || 'la Organización'}`}
	maxWidth="xl"
	onClose={() => (isMembersModalOpen = false)}
>
	<div class="space-y-5">
		<!-- Formulario para invitar / añadir miembro -->
		<div class="rounded-xl bg-[#090D16] border border-[#1F2937] p-4 space-y-3">
			<h4 class="text-xs font-semibold uppercase tracking-wider text-gray-300 flex items-center gap-1.5">
				<UserPlus size={14} class="text-indigo-400" />
				Añadir Miembro al Equipo
			</h4>

			<div class="flex flex-col sm:flex-row items-center gap-3">
				<div class="flex-1 w-full">
					<Input
						placeholder="correo@agencia.com"
						type="email"
						bind:value={newMemberEmail}
					/>
				</div>

				<div class="w-full sm:w-44">
					<Select
						options={[
							{ value: 'manager', label: 'Mánager' },
							{ value: 'analyst', label: 'Analista' },
							{ value: 'creator', label: 'Creador' },
							{ value: 'agency_owner', label: 'Propietario' }
						]}
						bind:value={newMemberRole}
					/>
				</div>

				<Button
					variant="primary"
					size="md"
					isLoading={isAddingMember}
					disabled={!newMemberEmail}
					onclick={handleAddMember}
				>
					Añadir
				</Button>
			</div>
		</div>

		<!-- Lista de Miembros Actuales -->
		<div class="space-y-2">
			<div class="text-xs font-semibold uppercase tracking-wider text-gray-400">
				Miembros Activos ({membersList.length})
			</div>

			{#if isLoadingMembers}
				<div class="py-6 text-center text-xs text-gray-400">Cargando miembros...</div>
			{:else}
				<div class="divide-y divide-[#1F2937] rounded-xl border border-[#1F2937] bg-[#0E1420] overflow-hidden">
					{#each membersList as member}
						<div class="flex items-center justify-between p-3 text-xs">
							<div class="flex items-center gap-3">
								<div class="flex h-8 w-8 items-center justify-center rounded-full bg-gray-800 text-gray-300 font-bold">
									{member.full_name ? member.full_name[0] : member.email[0].toUpperCase()}
								</div>
								<div>
									<div class="font-semibold text-white">
										{member.full_name || member.email.split('@')[0]}
									</div>
									<div class="text-gray-400 font-mono text-[11px]">
										{member.email}
									</div>
								</div>
							</div>

							<div class="flex items-center gap-3">
								<Badge
									variant={member.role === 'agency_owner' ? 'purple' : member.role === 'manager' ? 'indigo' : 'neutral'}
									size="sm"
									class="capitalize"
								>
									{member.role.replace('_', ' ')}
								</Badge>

								{#if member.role !== 'agency_owner'}
									<button
										onclick={() => handleRemoveMember(member.id)}
										class="p-1 text-gray-400 hover:text-rose-400 transition-colors"
										title="Eliminar miembro"
									>
										<Trash2 size={14} />
									</button>
								{/if}
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>

	{#snippet footer()}
		<Button variant="secondary" size="sm" onclick={() => (isMembersModalOpen = false)}>
			Cerrar
		</Button>
	{/snippet}
</Modal>
