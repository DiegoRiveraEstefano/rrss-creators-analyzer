<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore.svelte';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { Radio, ArrowRight, AlertCircle, Building2 } from 'lucide-svelte';

	let fullName = $state('');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let agencyName = $state('');
	let errorMessage = $state<string | null>(null);
	let isLoading = $state(false);

	async function handleRegister(e: SubmitEvent) {
		e.preventDefault();
		if (!fullName || !email || !password) {
			errorMessage = 'Por favor completa todos los campos requeridos.';
			return;
		}

		if (password !== confirmPassword) {
			errorMessage = 'Las contraseñas no coinciden.';
			return;
		}

		if (password.length < 6) {
			errorMessage = 'La contraseña debe tener al menos 6 caracteres.';
			return;
		}

		errorMessage = null;
		isLoading = true;
		try {
			await authStore.signUp(email, password, fullName);
			if (agencyName.trim()) {
				await tenantStore.createOrganization({
					name: agencyName,
					slug: agencyName.toLowerCase().replace(/[^a-z0-9]/g, '-')
				});
			}
			goto('/');
		} catch (err: any) {
			errorMessage = err.message || 'Error al crear la cuenta.';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Registro de Agencia | RRSS Creators Analyzer</title>
</svelte:head>

<div class="w-full max-w-md space-y-6">
	<!-- Branding Header -->
	<div class="text-center space-y-2">
		<div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#6366F1] to-[#06B6D4] text-white shadow-xl shadow-indigo-500/25 mb-2">
			<Radio size={26} class="stroke-[2.5]" />
		</div>
		<h1 class="text-2xl font-bold tracking-tight text-white">
			Crear Cuenta de Agencia
		</h1>
		<p class="text-xs text-gray-400">
			Comienza a gestionar tu roster de streaming y centralizar métricas
		</p>
	</div>

	<!-- Register Card -->
	<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-7 shadow-2xl space-y-5">
		{#if errorMessage}
			<div class="flex items-center gap-2 rounded-lg bg-rose-500/10 border border-rose-500/20 px-3.5 py-2.5 text-xs text-rose-400 animate-in fade-in duration-150">
				<AlertCircle size={16} class="shrink-0" />
				<span>{errorMessage}</span>
			</div>
		{/if}

		<form onsubmit={handleRegister} class="space-y-3.5">
			<Input
				label="Nombre Completo"
				placeholder="ej. Alex Moreno"
				bind:value={fullName}
				required
			/>

			<Input
				label="Correo Electrónico Corporativo"
				type="email"
				placeholder="alex@tuagencia.com"
				bind:value={email}
				required
			/>

			<Input
				label="Nombre de tu Agencia / Organización"
				placeholder="ej. Koa Talent Management"
				bind:value={agencyName}
				hint="Se creará tu espacio multi-tenant de trabajo"
			/>

			<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
				<div class="space-y-1.5">
					<label for="reg-password" class="block text-xs font-semibold text-gray-300">Contraseña</label>
					<input
						id="reg-password"
						type="password"
						placeholder="••••••••"
						bind:value={password}
						class="w-full rounded-lg bg-[#111827] border border-[#2D3748] px-3.5 py-2 text-xs text-white placeholder-gray-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
						required
					/>
				</div>

				<div class="space-y-1.5">
					<label for="reg-confirm" class="block text-xs font-semibold text-gray-300">Confirmar</label>
					<input
						id="reg-confirm"
						type="password"
						placeholder="••••••••"
						bind:value={confirmPassword}
						class="w-full rounded-lg bg-[#111827] border border-[#2D3748] px-3.5 py-2 text-xs text-white placeholder-gray-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
						required
					/>
				</div>
			</div>

			<Button
				type="submit"
				variant="primary"
				size="md"
				class="w-full mt-3"
				{isLoading}
			>
				<span>Crear Cuenta y Espacio</span>
				<ArrowRight size={15} />
			</Button>
		</form>
	</div>

	<!-- Login link footer -->
	<div class="text-center text-xs text-gray-400">
		¿Ya tienes una cuenta registrada?
		<a href="/login" class="text-indigo-400 font-semibold hover:text-indigo-300 ml-1 transition-colors">
			Iniciar Sesión
		</a>
	</div>
</div>
