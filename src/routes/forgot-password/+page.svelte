<script lang="ts">
	import { authStore } from '$lib/stores/authStore.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { Radio, ArrowLeft, Mail, CheckCircle2, AlertCircle } from 'lucide-svelte';

	let email = $state('');
	let isSubmitted = $state(false);
	let errorMessage = $state<string | null>(null);
	let isLoading = $state(false);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!email) return;

		errorMessage = null;
		isLoading = true;
		try {
			await authStore.resetPassword(email);
			isSubmitted = true;
		} catch (err: any) {
			errorMessage = err.message || 'Error al enviar el correo de recuperación.';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Recuperar Contraseña | RRSS Creators Analyzer</title>
</svelte:head>

<div class="w-full max-w-md space-y-6">
	<div class="text-center space-y-2">
		<div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#6366F1] to-[#06B6D4] text-white shadow-xl shadow-indigo-500/25 mb-2">
			<Radio size={26} class="stroke-[2.5]" />
		</div>
		<h1 class="text-2xl font-bold tracking-tight text-white">
			Recuperar Contraseña
		</h1>
		<p class="text-xs text-gray-400">
			Te enviaremos un enlace seguro para restablecer tu clave de acceso
		</p>
	</div>

	<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-7 shadow-2xl space-y-5">
		{#if isSubmitted}
			<div class="text-center space-y-3 py-2">
				<div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
					<CheckCircle2 size={24} />
				</div>
				<h3 class="text-base font-bold text-white">Enlace Enviado</h3>
				<p class="text-xs text-gray-400">
					Hemos enviado las instrucciones a <b class="text-gray-200">{email}</b>. Revisa tu bandeja de entrada o spam.
				</p>
				<div class="pt-3">
					<a href="/login">
						<Button variant="primary" size="sm" class="w-full">
							Volver a Iniciar Sesión
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

			<form onsubmit={handleSubmit} class="space-y-4">
				<Input
					label="Correo Electrónico Registrado"
					type="email"
					placeholder="tu@agencia.com"
					bind:value={email}
					required
				/>

				<Button
					type="submit"
					variant="primary"
					size="md"
					class="w-full mt-2"
					{isLoading}
				>
					<Mail size={15} />
					<span>Enviar Enlace de Recuperación</span>
				</Button>
			</form>

			<div class="text-center pt-2">
				<a href="/login" class="inline-flex items-center gap-1.5 text-xs text-gray-400 hover:text-white transition-colors">
					<ArrowLeft size={14} />
					<span>Volver a Iniciar Sesión</span>
				</a>
			</div>
		{/if}
	</div>
</div>
