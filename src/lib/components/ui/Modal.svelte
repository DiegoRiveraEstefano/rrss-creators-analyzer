<script lang="ts">
	import type { Snippet } from 'svelte';
	import { X } from 'lucide-svelte';

	interface Props {
		isOpen: boolean;
		title?: string;
		onClose: () => void;
		children?: Snippet;
		footer?: Snippet;
		maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
	}

	let {
		isOpen = $bindable(false),
		title,
		onClose,
		children,
		footer,
		maxWidth = 'lg'
	}: Props = $props();

	const widthMap = {
		sm: 'max-w-sm',
		md: 'max-w-md',
		lg: 'max-w-lg',
		xl: 'max-w-xl',
		'2xl': 'max-w-2xl'
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
		class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200"
		onclick={handleBackdropClick}
		onkeydown={(e) => e.key === 'Escape' && onClose()}
		role="presentation"
		tabindex="-1"
	>
		<div
			class="relative w-full {widthMap[maxWidth]} overflow-hidden rounded-2xl bg-[#111827] border border-[#2D3748] shadow-2xl animate-in zoom-in-95 duration-150"
			role="dialog"
			aria-modal="true"
		>
			{#if title}
				<div class="flex items-center justify-between border-b border-[#1F2937] px-6 py-4">
					<h3 class="text-base font-semibold text-white">{title}</h3>
					<button
						type="button"
						onclick={onClose}
						class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
						aria-label="Cerrar modal"
					>
						<X size={18} />
					</button>
				</div>
			{/if}

			<div class="p-6">
				{#if children}
					{@render children()}
				{/if}
			</div>

			{#if footer}
				<div class="flex items-center justify-end gap-3 border-t border-[#1F2937] bg-[#161F30]/50 px-6 py-3.5">
					{@render footer()}
				</div>
			{/if}
		</div>
	</div>
{/if}
