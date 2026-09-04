<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore.svelte';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import {
		User,
		Mail,
		ShieldCheck,
		Lock,
		Building2,
		CheckCircle2,
		AlertCircle,
		LogOut,
		Save
	} from 'lucide-svelte';

	let fullName = $state(authStore.profile?.full_name || '');
	let avatarUrl = $state(authStore.profile?.avatar_url || '');
	let currentPassword = $state('');
	let newPassword = $state('');
	let confirmNewPassword = $state('');

	let profileSuccess = $state(false);
	let profileError = $state<string | null>(null);
	let isSavingProfile = $state(false);

	let passwordSuccess = $state(false);
	let passwordError = $state<string | null>(null);
	let isSavingPassword = $state(false);

	$effect(() => {
		if (authStore.profile) {
			if (!fullName) fullName = authStore.profile.full_name || '';
			if (!avatarUrl) avatarUrl = authStore.profile.avatar_url || '';
		}
	});

	async function handleSaveProfile(e: SubmitEvent) {
		e.preventDefault();
		profileSuccess = false;
		profileError = null;
		isSavingProfile = true;
		try {
			await authStore.updateProfile({
				full_name: fullName,
				avatar_url: avatarUrl || undefined
			});
			profileSuccess = true;
			setTimeout(() => (profileSuccess = false), 3500);
		} catch (err: any) {
			profileError = err.message || 'Error al actualizar el perfil.';
		} finally {
			isSavingProfile = false;
		}
	}

	async function handleSavePassword(e: SubmitEvent) {
		e.preventDefault();
		passwordSuccess = false;
		passwordError = null;

		if (!newPassword || newPassword.length < 6) {
			passwordError = 'La nueva contraseña debe tener al menos 6 caracteres.';
			return;
		}

		if (newPassword !== confirmNewPassword) {
			passwordError = 'Las contraseñas no coinciden.';
			return;
		}

		isSavingPassword = true;
		try {
			await authStore.updatePassword(newPassword);
			passwordSuccess = true;
			newPassword = '';
			confirmNewPassword = '';
			currentPassword = '';
			setTimeout(() => (passwordSuccess = false), 3500);
		} catch (err: any) {
			passwordError = err.message || 'Error al actualizar la contraseña.';
		} finally {
			isSavingPassword = false;
		}
	}

	async function handleLogout() {
		await authStore.signOut();
		goto('/login');
	}
</script>

<svelte:head>
	<title>Perfil de Usuario | RRSS Creators Analyzer</title>
</svelte:head>

<div class="max-w-4xl mx-auto space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
				<User class="text-indigo-400" size={24} />
				<span>Perfil de Usuario y Cuenta</span>
			</h1>
			<p class="text-xs text-gray-400 mt-1">
				Gestiona tus datos personales, credenciales de seguridad y organizaciones asignadas.
			</p>
		</div>

		<Button variant="danger" size="sm" onclick={handleLogout}>
			<LogOut size={15} />
			Cerrar Sesión
		</Button>
	</div>

	<!-- Tarjeta Resumen de Usuario -->
	<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-6 shadow-xl flex flex-col sm:flex-row items-center sm:items-start gap-5">
		<div class="relative">
			<img
				src={avatarUrl || authStore.profile?.avatar_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=120&auto=format&fit=crop&q=80'}
				alt="User avatar preview"
				class="h-20 w-20 rounded-2xl object-cover ring-2 ring-indigo-500/40 shadow-lg shadow-indigo-500/10"
			/>
		</div>

		<div class="space-y-1.5 text-center sm:text-left flex-1">
			<div class="flex flex-col sm:flex-row sm:items-center gap-2">
				<h2 class="text-lg font-bold text-white">
					{authStore.profile?.full_name || 'Alex Moreno'}
				</h2>
				<Badge variant="indigo" size="sm">
					{tenantStore.currentOrg?.role === 'agency_owner' ? 'Propietario de Agencia' : 'Mánager de Roster'}
				</Badge>
			</div>

			<p class="text-xs text-gray-400 font-mono flex items-center justify-center sm:justify-start gap-1.5">
				<Mail size={13} />
				{authStore.profile?.email || 'manager@koatalent.com'}
			</p>

			<div class="pt-2 flex flex-wrap items-center justify-center sm:justify-start gap-2">
				<Badge variant="cyan" size="sm">
					Organización Activa: {tenantStore.currentOrg?.name || 'Koa Talent'}
				</Badge>
				<Badge variant="success" size="sm" dot>
					Autenticado
				</Badge>
			</div>
		</div>
	</div>

	<!-- Grilla de Formularios: Información Personal & Seguridad -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
		<!-- Formulario 1: Datos Personales -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-6 shadow-xl space-y-4">
			<div class="flex items-center gap-2.5 pb-2 border-b border-[#1F2937]">
				<User size={18} class="text-indigo-400" />
				<h3 class="text-sm font-semibold text-white">Información Personal</h3>
			</div>

			{#if profileSuccess}
				<div class="flex items-center gap-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-2.5 text-xs text-emerald-400">
					<CheckCircle2 size={15} />
					<span>Perfil actualizado correctamente.</span>
				</div>
			{/if}

			{#if profileError}
				<div class="flex items-center gap-2 rounded-lg bg-rose-500/10 border border-rose-500/20 p-2.5 text-xs text-rose-400">
					<AlertCircle size={15} />
					<span>{profileError}</span>
				</div>
			{/if}

			<form onsubmit={handleSaveProfile} class="space-y-4">
				<Input
					label="Nombre Completo"
					placeholder="Tu nombre y apellido"
					bind:value={fullName}
					required
				/>

				<Input
					label="Correo Electrónico"
					type="email"
					value={authStore.profile?.email || ''}
					disabled
					hint="El correo electrónico está vinculado a tu cuenta principal"
				/>

				<Input
					label="URL de Foto de Perfil / Avatar"
					placeholder="https://..."
					bind:value={avatarUrl}
					hint="Enlace público a tu imagen de avatar"
				/>

				<div class="pt-2">
					<Button
						type="submit"
						variant="primary"
						size="sm"
						isLoading={isSavingProfile}
					>
						<Save size={14} />
						Guardar Cambios
					</Button>
				</div>
			</form>
		</div>

		<!-- Formulario 2: Seguridad y Contraseña -->
		<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-6 shadow-xl space-y-4">
			<div class="flex items-center gap-2.5 pb-2 border-b border-[#1F2937]">
				<Lock size={18} class="text-amber-400" />
				<h3 class="text-sm font-semibold text-white">Seguridad de la Cuenta</h3>
			</div>

			{#if passwordSuccess}
				<div class="flex items-center gap-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-2.5 text-xs text-emerald-400">
					<CheckCircle2 size={15} />
					<span>Contraseña actualizada con éxito.</span>
				</div>
			{/if}

			{#if passwordError}
				<div class="flex items-center gap-2 rounded-lg bg-rose-500/10 border border-rose-500/20 p-2.5 text-xs text-rose-400">
					<AlertCircle size={15} />
					<span>{passwordError}</span>
				</div>
			{/if}

			<form onsubmit={handleSavePassword} class="space-y-4">
				<Input
					label="Nueva Contraseña"
					type="password"
					placeholder="••••••••"
					bind:value={newPassword}
					hint="Mínimo 6 caracteres"
					required
				/>

				<Input
					label="Confirmar Nueva Contraseña"
					type="password"
					placeholder="••••••••"
					bind:value={confirmNewPassword}
					required
				/>

				<div class="pt-2">
					<Button
						type="submit"
						variant="secondary"
						size="sm"
						isLoading={isSavingPassword}
						disabled={!newPassword || !confirmNewPassword}
					>
						<Lock size={14} />
						Actualizar Contraseña
					</Button>
				</div>
			</form>
		</div>
	</div>

	<!-- Sección de Organizaciones del Usuario -->
	<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-6 shadow-xl space-y-4">
		<div class="flex items-center justify-between pb-2 border-b border-[#1F2937]">
			<div class="flex items-center gap-2.5">
				<Building2 size={18} class="text-cyan-400" />
				<h3 class="text-sm font-semibold text-white">Organizaciones y Permisos</h3>
			</div>
			<a href="/tenants">
				<Button variant="ghost" size="sm">
					Gestionar Organizaciones
				</Button>
			</a>
		</div>

		<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
			{#each tenantStore.organizations as org}
				<div
					class="rounded-xl border border-[#2D3748] bg-[#090D16] p-4 flex items-center justify-between {tenantStore.currentOrg?.id === org.id ? 'ring-1 ring-indigo-500/60' : ''}"
				>
					<div class="flex items-center gap-3">
						<div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
							<Building2 size={18} />
						</div>
						<div>
							<div class="text-xs font-bold text-white flex items-center gap-2">
								{org.name}
								{#if tenantStore.currentOrg?.id === org.id}
									<Badge variant="indigo" size="sm">Activa</Badge>
								{/if}
							</div>
							<div class="text-[11px] text-gray-400 font-mono">
								Plan: <span class="capitalize text-gray-300">{org.plan}</span>
							</div>
						</div>
					</div>

					{#if tenantStore.currentOrg?.id !== org.id}
						<Button
							variant="secondary"
							size="sm"
							onclick={() => tenantStore.selectOrganization(org.id)}
						>
							Cambiar
						</Button>
					{/if}
				</div>
			{/each}
		</div>
	</div>
</div>
