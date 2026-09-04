<script lang="ts">
	import Modal from '$lib/components/ui/Modal.svelte';
	import { Keyboard } from 'lucide-svelte';

	interface Props {
		isOpen: boolean;
		onClose: () => void;
	}

	let { isOpen = false, onClose }: Props = $props();

	const shortcuts = [
		{
			category: 'Navegación Global',
			items: [
				{ keys: ['⌘', 'K'], desc: 'Abrir Paleta de Comandos y Búsqueda' },
				{ keys: ['G', 'D'], desc: 'Ir a Dashboard General' },
				{ keys: ['G', 'R'], desc: 'Ir al Roster de Creadores' },
				{ keys: ['G', 'V'], desc: 'Ir al Catálogo de Videos' },
				{ keys: ['G', 'I'], desc: 'Ir al Importador de Datos CSV' },
				{ keys: ['G', 'A'], desc: 'Ir al Centro de Alertas' },
				{ keys: ['G', 'T'], desc: 'Ir a Gestión de Organizaciones' }
			]
		},
		{
			category: 'Acciones y Datos',
			items: [
				{ keys: ['⇧', 'R'], desc: 'Refrescar datos y caché de la vista activa' },
				{ keys: ['?'], desc: 'Abrir esta guía de atajos de teclado' },
				{ keys: ['Esc'], desc: 'Cerrar modales o paleta activa' }
			]
		}
	];
</script>

<Modal {isOpen} {onClose} title="Atajos de Teclado" maxWidth="md">
	<div class="space-y-6">
		<div class="flex items-center gap-3 p-3 rounded-xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-300 text-xs">
			<Keyboard size={18} class="text-indigo-400 shrink-0" />
			<span>
				Navega velozmente por la plataforma utilizando las combinaciones de teclas impulsadas por <strong class="text-white">@tanstack/svelte-hotkeys</strong>.
			</span>
		</div>

		<div class="space-y-5">
			{#each shortcuts as group}
				<div>
					<h4 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2.5">
						{group.category}
					</h4>
					<div class="space-y-1.5">
						{#each group.items as item}
							<div class="flex items-center justify-between p-2 rounded-lg bg-[#111827] border border-[#1F2937] text-xs">
								<span class="text-gray-300">{item.desc}</span>
								<div class="flex items-center gap-1">
									{#each item.keys as key}
										<kbd class="min-w-[20px] px-1.5 py-0.5 text-center font-mono text-[11px] font-semibold text-gray-200 bg-[#1E293B] border border-[#334155] rounded shadow">
											{key}
										</kbd>
									{/each}
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	</div>
</Modal>
