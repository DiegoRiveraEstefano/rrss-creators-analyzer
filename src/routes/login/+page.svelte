<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import { Radio, Lock, Mail, ArrowRight, Sparkles, AlertCircle } from 'lucide-svelte';

	let email = $state('');
	let password = $state('');
	let errorMessage = $state<string | null>(null);
	let isLoading = $state(false);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!email || !password) {
			errorMessage = 'Por favor ingresa tu correo y contraseña.';
			return;
		}

		errorMessage = null;
		isLoading = true;
		try {
			await authStore.signIn(email, password);
			goto('/');
		} catch (err: any) {
			errorMessage = err.message || 'Credenciales inválidas. Por favor verifica tus datos.';
		} finally {
			isLoading = false;
		}
	}

	async function handleDemoLogin() {
		email = 'manager@koatalent.com';
		password = 'demo-password-123';
		isLoading = true;
		try {
			await authStore.signIn(email, password);
			goto('/');
		} catch (err: any) {
			errorMessage = err.message;
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Iniciar Sesión | RRSS Creators Analyzer</title>
</svelte:head>

<div class="w-full max-w-md space-y-6">
	<!-- Branding Header -->
	<div class="text-center space-y-2">
		<div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#6366F1] to-[#06B6D4] text-white shadow-xl shadow-indigo-500/25 mb-2">
			<Radio size={26} class="stroke-[2.5]" />
		</div>
		<h1 class="text-2xl font-bold tracking-tight text-white">
			RRSS Creators Analyzer
		</h1>
		<p class="text-xs text-gray-400">
			Plataforma SaaS Multi-Tenant de Business Intelligence para Streaming
		</p>
	</div>

	<!-- Login Card -->
	<div class="rounded-2xl border border-[#1F2937] bg-[#111827] p-7 shadow-2xl space-y-5">
		<div class="space-y-1">
			<h2 class="text-base font-bold text-white">Iniciar Sesión</h2>
			<p class="text-xs text-gray-400">Ingresa tus credenciales para acceder a tus organizaciones</p>
		</div>

		{#if errorMessage}
			<div class="flex items-center gap-2 rounded-lg bg-rose-500/10 border border-rose-500/20 px-3.5 py-2.5 text-xs text-rose-400 animate-in fade-in duration-150">
				<AlertCircle size={16} class="shrink-0" />
				<span>{errorMessage}</span>
			</div>
		{/if}

		<form onsubmit={handleSubmit} class="space-y-4">
			<Input
				label="Correo Electrónico"
				type="email"
				placeholder="tu@agencia.com"
				bind:value={email}
				required
			/>

			<div class="space-y-1">
				<div class="flex items-center justify-between">
					<label for="password-input" class="block text-xs font-semibold text-gray-300">
						Contraseña
					</label>
					<a href="/forgot-password" class="text-[11px] text-indigo-400 hover:text-indigo-300 transition-colors">
						¿Olvidaste tu contraseña?
					</a>
				</div>
				<input
					id="password-input"
					type="password"
					placeholder="••••••••"
					bind:value={password}
					class="w-full rounded-lg bg-[#111827] border border-[#2D3748] px-3.5 py-2 text-xs text-white placeholder-gray-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
					required
				/>
			</div>

			<Button
				type="submit"
				variant="primary"
				size="md"
				class="w-full mt-2"
				{isLoading}
			>
				<span>Acceder al Panel</span>
				<ArrowRight size={15} />
			</Button>
		</form>

		<div class="relative flex items-center justify-center pt-2">
			<div class="absolute inset-0 flex items-center">
				<div class="w-full border-t border-[#1F2937]"></div>
			</div>
			<div class="relative bg-[#111827] px-3 text-[11px] uppercase tracking-wider text-gray-400">
				O prueba rápida
			</div>
		</div>

		<!-- One-Click Demo Mode -->
		<Button
			type="button"
			variant="outline"
			size="sm"
			class="w-full border-indigo-500/30 hover:border-indigo-500/60 text-indigo-300 hover:text-indigo-200"
			onclick={handleDemoLogin}
			disabled={isLoading}
		>
			<Sparkles size={14} class="text-indigo-400" />
			<span>Acceso Rápido como Mánager Demo</span>
		</Button>
	</div>

	<!-- Register link footer -->
	<div class="text-center text-xs text-gray-400">
		¿Aún no tienes una cuenta de agencia?
		<a href="/register" class="text-indigo-400 font-semibold hover:text-indigo-300 ml-1 transition-colors">
			Crear Organización
		</a>
	</div>
</div>
