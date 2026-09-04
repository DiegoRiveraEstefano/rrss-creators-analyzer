<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { Radio, Lock, CheckCircle2, AlertCircle } from 'lucide-svelte';

	let password = $state('');
	let confirmPassword = $state('');
	let errorMessage = $state<string | null>(null);
	let isSuccess = $state(false);
	let isLoading = $state(false);

	async function handleUpdate(e: SubmitEvent) {
		e.preventDefault();
		if (!password || password.length < 6) {
			errorMessage = 'La contraseña debe tener al menos 6 caracteres.';
			return;
		}

		if (password !== confirmPassword) {
			errorMessage = 'Las contraseñas no coinciden.';
			return;
		}

		errorMessage = null;
		isLoading = true;
		try {
			await authStore.updatePassword(password);
			isSuccess = true;
		} catch (err: any) {
			errorMessage = err.message || 'Error al actualizar la contraseña.';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Nueva Contraseña | RRSS Creators Analyzer</title>
</svelte:head>

<div class="w-full max-w-md space-y-6">
	<div class="text-center space-y-2">
		<div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#6366F1] to-[#06B6D4] text-white shadow-xl shadow-indigo-500/25 mb-2">
			<Radio size={26} class="stroke-[2.5]" />
		</div>
		<h1 class="text-2xl font-bold tracking-tight text-white">
			Establecer Nueva Contraseña
		</h1>
		<p class="text-xs text-gray-400">
			Crea una contraseña segura para tu cuenta de agencia
		</p>
	</div>

	<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-7 shadow-2xl space-y-5">
		{#if isSuccess}
			<div class="text-center space-y-3 py-2">
				<div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
					<CheckCircle2 size={24} />
				</div>
				<h3 class="text-base font-bold text-white">Contraseña Actualizada</h3>
				<p class="text-xs text-gray-400">
					Tu clave ha sido modificada con éxito. Ya puedes ingresar al panel.
				</p>
				<div class="pt-3">
					<a href="/login">
						<Button variant="primary" size="sm" class="w-full">
							Iniciar Sesión
						</Button>
					</a>
				</div>
			</div>
		{:else}
			{#if errorMessage}
				<div class="flex items-center gap-2 rounded-lg bg-rose-500/10 border border-rose-500/20 px-3.5 py-2.5 text-xs text-rose-400">
					<AlertCircle size={16} class="shrink-0" />
					<span>{errorMessage}</span>
				</div>
			{/if}

			<form onsubmit={handleUpdate} class="space-y-4">
				<Input
					label="Nueva Contraseña"
					type="password"
					placeholder="••••••••"
					bind:value={password}
					required
				/>

				<Input
					label="Confirmar Nueva Contraseña"
					type="password"
					placeholder="••••••••"
					bind:value={confirmPassword}
					required
				/>

				<Button
					type="submit"
					variant="primary"
					size="md"
					class="w-full mt-2"
					{isLoading}
				>
					<Lock size={15} />
					<span>Guardar Nueva Contraseña</span>
				</Button>
			</form>
		{/if}
	</div>
</div>
