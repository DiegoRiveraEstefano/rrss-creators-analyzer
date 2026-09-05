<script lang="ts">
	import type { Snippet } from 'svelte';
	import { X, RotateCcw, Check } from 'lucide-svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		isOpen: boolean;
		title?: string;
		position?: 'left' | 'right';
		width?: 'sm' | 'md' | 'lg';
		activeCount?: number;
		onClose: () => void;
		onReset?: () => void;
		onApply?: () => void;
		children?: Snippet;
	}

	let {
		isOpen = false,
		title = 'Filtros',
		position = 'right',
		width = 'md',
		activeCount = 0,
		onClose,
		onReset,
		onApply,
		children
	}: Props = $props();

	const widthClasses = {
		sm: 'max-w-xs',
		md: 'max-w-sm',
		lg: 'max-w-md'
	};

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			onClose();
		}
	}

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Escape' && isOpen) {
			onClose();
		}
	}
</script>

<svelte:window onkeydown={handleKeyDown} />

{#if isOpen}
	<div
		class="fixed inset-0 z-50 flex overflow-hidden bg-black/60 backdrop-blur-xs transition-opacity duration-300 {position === 'left' ? 'justify-start' : 'justify-end'}"
		onclick={handleBackdropClick}
		role="presentation"
	>
		<!-- Drawer Panel -->
		<div
			class="flex h-full w-full {widthClasses[width]} flex-col border-[#2D3748] bg-[#0D131F] shadow-2xl transition-all duration-300 {position === 'left'
				? 'border-r animate-in slide-in-from-left'
				: 'border-l animate-in slide-in-from-right'}"
			role="dialog"
			aria-modal="true"
			aria-label={title}
		>
			<!-- Header -->
			<div class="flex items-center justify-between border-b border-[#1F2937] px-5 py-4 bg-[#111827]/90">
				<div class="flex items-center gap-2.5">
					<h3 class="text-sm font-bold text-white tracking-wide">{title}</h3>
					{#if activeCount > 0}
						<span class="flex h-5 items-center justify-center rounded-full bg-indigo-500/20 border border-indigo-500/40 px-2 text-[10px] font-bold text-indigo-300 font-mono">
							{activeCount} activo{activeCount === 1 ? '' : 's'}
						</span>
					{/if}
				</div>

				<div class="flex items-center gap-1.5">
					{#if onReset && activeCount > 0}
						<button
							type="button"
							onclick={onReset}
							class="flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] font-medium text-gray-400 hover:text-indigo-400 hover:bg-gray-800 transition-colors"
							title="Restablecer filtros a valores por defecto"
						>
							<RotateCcw size={12} />
							<span>Limpiar</span>
						</button>
					{/if}

					<button
						type="button"
						onclick={onClose}
						class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
						aria-label="Cerrar panel de filtros"
					>
						<X size={16} />
					</button>
				</div>
			</div>

			<!-- Body: Scrollable filters -->
			<div class="flex-1 overflow-y-auto px-5 py-2 divide-y divide-[#1F2937]/50">
				{#if children}
					{@render children()}
				{/if}
			</div>

			<!-- Footer -->
			<div class="flex items-center justify-between border-t border-[#1F2937] bg-[#111827]/90 px-5 py-3.5">
				{#if onReset}
					<Button
						type="button"
						variant="ghost"
						size="sm"
						onclick={onReset}
						disabled={activeCount === 0}
					>
						Restablecer
					</Button>
				{:else}
					<div></div>
				{/if}

				<div class="flex items-center gap-2">
					<Button
						type="button"
						variant="primary"
						size="sm"
						onclick={() => {
							onApply?.();
							onClose();
						}}
					>
						<Check size={14} />
						Aplicar
					</Button>
				</div>
			</div>
		</div>
	</div>
{/if}
