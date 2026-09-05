<script lang="ts">
	import { goto } from '$app/navigation';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import {
		Search,
		LayoutDashboard,
		Users,
		Radio,
		Video,
		UploadCloud,
		TriangleAlert,
		Building2,
		User,
		Sparkles,
		Database,
		Keyboard,
		ArrowRight
	} from 'lucide-svelte';

	interface Props {
		isOpen: boolean;
		onClose: () => void;
		onOpenHotkeys?: () => void;
	}

	let { isOpen = false, onClose, onOpenHotkeys }: Props = $props();

	let searchQuery = $state('');
	let selectedIndex = $state(0);

	interface PaletteItem {
		id: string;
		title: string;
		subtitle?: string;
		category: 'Navegación' | 'Creadores' | 'Acciones';
		icon: any;
		action: () => void;
	}

	const navigationItems: PaletteItem[] = [
		{
			id: 'nav-dashboard',
			title: 'Dashboard General',
			subtitle: 'Métricas agregadas del roster y canales',
			category: 'Navegación',
			icon: LayoutDashboard,
			action: () => {
				tenantStore.selectCreator(null);
				goto('/');
			}
		},
		{
			id: 'nav-roster',
			title: 'Roster de Creadores',
			subtitle: 'Gestión y perfiles de talentos representados',
			category: 'Navegación',
			icon: Users,
			action: () => goto('/roster')
		},
		{
			id: 'nav-lives',
			title: 'Sesiones en Vivo (Lives)',
			subtitle: 'Historial y métricas de transmisiones en directo',
			category: 'Navegación',
			icon: Radio,
			action: () => goto('/lives')
		},
		{
			id: 'nav-videos',
			title: 'Videos Publicados',
			subtitle: 'Métricas de videos subidos a YouTube, TikTok, Reels',
			category: 'Navegación',
			icon: Video,
			action: () => goto('/videos')
		},
		{
			id: 'nav-raw-data',
			title: 'Tablas de Datos Crudos',
			subtitle: 'Sesiones de streaming y catálogo completo',
			category: 'Navegación',
			icon: Database,
			action: () => goto('/raw-data')
		},
		{
			id: 'nav-import',
			title: 'Importador de Datos',
			subtitle: 'Ingesta de archivos CSV / Excel de plataformas',
			category: 'Navegación',
			icon: UploadCloud,
			action: () => goto('/import')
		},
		{
			id: 'nav-alerts',
			title: 'Centro de Alertas & Sanciones',
			subtitle: 'Strikes, advertencias y reportes de moderación',
			category: 'Navegación',
			icon: TriangleAlert,
			action: () => goto('/alerts')
		},
		{
			id: 'nav-tenants',
			title: 'Organizaciones / Tenants',
			subtitle: 'Configuración multi-tenant y miembros del equipo',
			category: 'Navegación',
			icon: Building2,
			action: () => goto('/tenants')
		},
		{
			id: 'nav-profile',
			title: 'Mi Perfil & Seguridad',
			subtitle: 'Configuración de cuenta y contraseña',
			category: 'Navegación',
			icon: User,
			action: () => goto('/profile')
		}
	];

	const creatorItems: PaletteItem[] = $derived(
		tenantStore.creators.map((c) => ({
			id: `creator-${c.id}`,
			title: c.display_name,
			subtitle: `@${c.handle} • ${c.primary_platform}`,
			category: 'Creadores',
			icon: User,
			action: () => {
				tenantStore.selectCreator(c.id);
				goto(`/roster/${c.id}`);
			}
		}))
	);

	const actionItems: PaletteItem[] = [
		{
			id: 'action-shortcuts',
			title: 'Ver Atajos de Teclado',
			subtitle: 'Consulta todos los comandos y atajos rápidos',
			category: 'Acciones',
			icon: Keyboard,
			action: () => {
				onOpenHotkeys?.();
			}
		}
	];

	const allItems = $derived([...navigationItems, ...creatorItems, ...actionItems]);

	const filteredItems = $derived.by(() => {
		const query = searchQuery.toLowerCase().trim();
		if (!query) return allItems;

		return allItems.filter(
			(item) =>
				item.title.toLowerCase().includes(query) ||
				(item.subtitle && item.subtitle.toLowerCase().includes(query)) ||
				item.category.toLowerCase().includes(query)
		);
	});

	// Reset index when search changes
	$effect(() => {
		searchQuery;
		selectedIndex = 0;
	});

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			selectedIndex = (selectedIndex + 1) % (filteredItems.length || 1);
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			selectedIndex = (selectedIndex - 1 + (filteredItems.length || 1)) % (filteredItems.length || 1);
		} else if (e.key === 'Enter') {
			e.preventDefault();
			if (filteredItems[selectedIndex]) {
				executeItem(filteredItems[selectedIndex]);
			}
		} else if (e.key === 'Escape') {
			onClose();
		}
	}

	function executeItem(item: PaletteItem) {
		onClose();
		item.action();
	}

	function focusInput(node: HTMLInputElement) {
		node.focus();
	}
</script>

{#if isOpen}
	<div
		class="fixed inset-0 z-50 flex items-start justify-center pt-20 sm:pt-28 px-4"
		role="dialog"
		aria-modal="true"
	>
		<!-- Backdrop -->
		<button
			class="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity"
			onclick={onClose}
			aria-label="Cerrar paleta"
		></button>

		<!-- Palette Window -->
		<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
		<div
			class="relative w-full max-w-xl overflow-hidden rounded-2xl border border-[#2D3748] bg-[#0F172A] shadow-2xl z-10 animate-in fade-in zoom-in-95 duration-150"
			onkeydown={handleKeyDown}
			tabindex="-1"
			role="region"
			aria-label="Paleta de Comandos"
		>
			<!-- Input Header -->
			<div class="flex items-center gap-3 border-b border-[#1F2937] px-4 py-3.5 bg-[#111827]">
				<Search class="h-5 w-5 text-indigo-400 shrink-0" />
				<input
					use:focusInput
					type="text"
					bind:value={searchQuery}
					placeholder="Escribe un comando o busca creadores y vistas..."
					class="w-full bg-transparent text-sm text-white placeholder-gray-400 focus:outline-none"
				/>
				<kbd class="px-2 py-0.5 text-[10px] font-mono font-semibold text-gray-400 bg-gray-800 border border-gray-700 rounded">
					ESC
				</kbd>
			</div>

			<!-- Results List -->
			<div class="max-h-96 overflow-y-auto p-2 divide-y divide-[#1E293B]/40">
				{#if filteredItems.length === 0}
					<div class="px-4 py-8 text-center text-xs text-gray-400">
						No se encontraron comandos o creadores para "<span class="text-indigo-400 font-semibold">{searchQuery}</span>"
					</div>
				{:else}
					<div class="space-y-1">
						{#each filteredItems as item, idx}
							{@const isSelected = idx === selectedIndex}
							{@const Icon = item.icon}
							<button
								type="button"
								onclick={() => executeItem(item)}
								onmouseenter={() => (selectedIndex = idx)}
								class="flex w-full items-center justify-between gap-3 rounded-xl px-3 py-2.5 text-left text-xs transition-colors {isSelected
									? 'bg-indigo-600/20 text-white border border-indigo-500/30'
									: 'text-gray-300 hover:bg-[#1E293B]/60 border border-transparent'}"
							>
								<div class="flex items-center gap-3 min-w-0">
									<div
										class="flex h-7 w-7 items-center justify-center rounded-lg {isSelected
											? 'bg-indigo-600 text-white'
											: 'bg-gray-800 text-gray-400'}"
									>
										<Icon size={15} />
									</div>
									<div class="truncate">
										<div class="font-medium text-white truncate flex items-center gap-2">
											<span>{item.title}</span>
											<span class="text-[10px] px-1.5 py-0.2 rounded bg-gray-800 text-gray-400 font-mono">
												{item.category}
											</span>
										</div>
										{#if item.subtitle}
											<div class="text-[11px] text-gray-400 truncate">{item.subtitle}</div>
										{/if}
									</div>
								</div>

								{#if isSelected}
									<ArrowRight size={14} class="text-indigo-400 shrink-0" />
								{/if}
							</button>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Footer -->
			<div class="flex items-center justify-between border-t border-[#1F2937] bg-[#0A0F1D] px-4 py-2 text-[10px] text-gray-400 font-mono">
				<div class="flex items-center gap-3">
					<span><kbd class="text-gray-300">↑↓</kbd> Navegar</span>
					<span><kbd class="text-gray-300">↵</kbd> Seleccionar</span>
					<span><kbd class="text-gray-300">ESC</kbd> Cerrar</span>
				</div>
				<span class="text-indigo-400 font-semibold">TanStack Hotkeys</span>
			</div>
		</div>
	</div>
{/if}
