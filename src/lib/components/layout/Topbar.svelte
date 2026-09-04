<script lang="ts">
	import { goto } from '$app/navigation';
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import { authStore } from '$lib/stores/authStore.svelte';
	import {
		Building2,
		Bell,
		Search,
		User,
		ChevronDown,
		Check,
		Sparkles,
		Plus,
		Settings,
		LogOut,
		Keyboard
	} from 'lucide-svelte';
	import Badge from '$lib/components/ui/Badge.svelte';

	interface Props {
		onOpenCommandPalette?: () => void;
		onOpenHotkeys?: () => void;
	}

	let { onOpenCommandPalette, onOpenHotkeys }: Props = $props();

	let isOrgDropdownOpen = $state(false);
	let isCreatorDropdownOpen = $state(false);
	let isProfileDropdownOpen = $state(false);

	function toggleOrgDropdown() {
		isOrgDropdownOpen = !isOrgDropdownOpen;
		if (isOrgDropdownOpen) {
			isCreatorDropdownOpen = false;
			isProfileDropdownOpen = false;
		}
	}

	function toggleCreatorDropdown() {
		isCreatorDropdownOpen = !isCreatorDropdownOpen;
		if (isCreatorDropdownOpen) {
			isOrgDropdownOpen = false;
			isProfileDropdownOpen = false;
		}
	}

	function toggleProfileDropdown() {
		isProfileDropdownOpen = !isProfileDropdownOpen;
		if (isProfileDropdownOpen) {
			isOrgDropdownOpen = false;
			isCreatorDropdownOpen = false;
		}
	}

	function handleSelectCreator(id: string | null) {
		tenantStore.selectCreator(id);
		isCreatorDropdownOpen = false;
	}

	function handleSelectOrg(id: string) {
		tenantStore.selectOrganization(id);
		isOrgDropdownOpen = false;
	}

	async function handleLogout() {
		await authStore.signOut();
		goto('/login');
	}
</script>

<header class="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-[#1F2937] bg-[#090D16]/90 px-6 backdrop-blur-md">
	<!-- Izquierda: Selectores de Tenant / Roster Switcher -->
	<div class="flex items-center gap-3">
		<!-- Selector de Agencia / Organización -->
		<div class="relative">
			<button
				onclick={toggleOrgDropdown}
				class="flex items-center gap-2.5 rounded-lg border border-[#2D3748] bg-[#111827] px-3 py-1.5 text-xs font-medium text-white transition-colors hover:border-indigo-500/50 hover:bg-[#1F2937]"
			>
				<div class="flex h-5 w-5 items-center justify-center rounded bg-indigo-500/20 text-indigo-400">
					<Building2 size={13} />
				</div>
				<span class="max-w-[140px] truncate font-semibold">
					{tenantStore.currentOrg?.name || 'Koa Talent'}
				</span>
				<ChevronDown size={14} class="text-gray-400" />
			</button>

			{#if isOrgDropdownOpen}
				<div
					class="absolute left-0 mt-2 w-64 rounded-xl border border-[#2D3748] bg-[#111827] p-1.5 shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-100"
				>
					<div class="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
						Organizaciones / Agencias
					</div>
					{#each tenantStore.organizations as org}
						<button
							onclick={() => handleSelectOrg(org.id)}
							class="flex w-full items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs font-medium transition-colors {tenantStore.currentOrg?.id === org.id
								? 'bg-indigo-600/20 text-indigo-300'
								: 'text-gray-300 hover:bg-gray-800 hover:text-white'}"
						>
							<div class="truncate">
								<div class="font-medium text-white truncate">{org.name}</div>
								<div class="text-[10px] text-gray-400 font-mono capitalize">{org.plan}</div>
							</div>
							{#if tenantStore.currentOrg?.id === org.id}
								<Check size={14} class="text-indigo-400" />
							{/if}
						</button>
					{/each}

					<div class="my-1 border-t border-[#1F2937]"></div>
					<a
						href="/tenants"
						onclick={() => (isOrgDropdownOpen = false)}
						class="flex items-center gap-2 rounded-lg px-2.5 py-2 text-xs text-indigo-400 hover:bg-indigo-500/10 hover:text-indigo-300 transition-colors"
					>
						<Settings size={14} />
						<span>Gestionar Organizaciones</span>
					</a>
				</div>
			{/if}
		</div>

		<span class="text-gray-600">/</span>

		<!-- Switcher de Roster (Todos vs Creador Específico) -->
		<div class="relative">
			<button
				onclick={toggleCreatorDropdown}
				class="flex items-center gap-2 rounded-lg border border-[#2D3748] bg-[#111827] px-3 py-1.5 text-xs font-medium text-white transition-colors hover:border-cyan-500/50 hover:bg-[#1F2937]"
			>
				{#if tenantStore.selectedCreator}
					{#if tenantStore.selectedCreator.avatar_url}
						<img
							src={tenantStore.selectedCreator.avatar_url}
							alt={tenantStore.selectedCreator.display_name}
							class="h-4 w-4 rounded-full object-cover ring-1 ring-cyan-500/40"
						/>
					{:else}
						<User size={13} class="text-cyan-400" />
					{/if}
					<span class="max-w-[120px] truncate text-cyan-300 font-semibold">
						@{tenantStore.selectedCreator.handle}
					</span>
				{:else}
					<Sparkles size={13} class="text-indigo-400" />
					<span class="font-semibold text-gray-200">Todo el Roster</span>
				{/if}
				<ChevronDown size={14} class="text-gray-400" />
			</button>

			{#if isCreatorDropdownOpen}
				<div
					class="absolute left-0 mt-2 w-64 rounded-xl border border-[#2D3748] bg-[#111827] p-1.5 shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-100"
				>
					<div class="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
						Vista de Análisis
					</div>
					<button
						onclick={() => handleSelectCreator(null)}
						class="flex w-full items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs font-medium transition-colors {!tenantStore.selectedCreatorId
							? 'bg-indigo-600/20 text-indigo-300'
							: 'text-gray-300 hover:bg-gray-800 hover:text-white'}"
					>
						<span class="flex items-center gap-2">
							<Sparkles size={13} class="text-indigo-400" />
							Todo el Roster (Agencia)
						</span>
						{#if !tenantStore.selectedCreatorId}
							<Check size={14} class="text-indigo-400" />
						{/if}
					</button>

					<div class="my-1 border-t border-[#1F2937]"></div>
					<div class="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
						Creadores Individuales
					</div>

					{#each tenantStore.creators as creator}
						<button
							onclick={() => handleSelectCreator(creator.id)}
							class="flex w-full items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs font-medium transition-colors {tenantStore.selectedCreatorId === creator.id
								? 'bg-cyan-600/20 text-cyan-300'
								: 'text-gray-300 hover:bg-gray-800 hover:text-white'}"
						>
							<div class="flex items-center gap-2 truncate">
								{#if creator.avatar_url}
									<img src={creator.avatar_url} alt="" class="h-4 w-4 rounded-full object-cover" />
								{/if}
								<span class="truncate">{creator.display_name}</span>
								<span class="text-[10px] text-gray-400">@{creator.handle}</span>
							</div>
							{#if tenantStore.selectedCreatorId === creator.id}
								<Check size={14} class="text-cyan-400" />
							{/if}
						</button>
					{/each}
				</div>
			{/if}
		</div>
	</div>

	<!-- Centro / Derecha: Búsqueda, Atajos, Notificaciones y Perfil -->
	<div class="flex items-center gap-3">
		<!-- Quick Command Palette Search Trigger -->
		<button
			onclick={onOpenCommandPalette}
			class="hidden sm:flex items-center gap-2.5 rounded-lg border border-[#2D3748] bg-[#111827] px-3 py-1.5 text-xs text-gray-400 hover:border-indigo-500/50 hover:text-white transition-colors"
			title="Abrir paleta de comandos (⌘K / Ctrl+K)"
		>
			<Search size={14} class="text-indigo-400" />
			<span class="text-xs">Buscar o comando...</span>
			<kbd class="ml-1 rounded bg-[#1E293B] border border-[#334155] px-1.5 py-0.5 text-[10px] font-mono font-semibold text-gray-300">
				⌘K
			</kbd>
		</button>

		<!-- Keyboard Shortcuts Help button -->
		<button
			onclick={onOpenHotkeys}
			class="hidden md:flex h-8 w-8 items-center justify-center rounded-lg border border-[#2D3748] bg-[#111827] text-gray-400 hover:border-indigo-500/50 hover:text-indigo-300 transition-colors"
			title="Ver atajos de teclado (?)"
		>
			<Keyboard size={15} />
		</button>

		<!-- Live Streamers Indicator -->
		<Badge variant="cyan" dot pulse size="sm">
			2 en vivo
		</Badge>

		<!-- Alert Center link -->
		<a
			href="/alerts"
			class="relative flex h-8 w-8 items-center justify-center rounded-lg border border-[#2D3748] bg-[#111827] text-gray-300 transition-colors hover:border-amber-500/50 hover:text-amber-300"
			title="Centro de Alertas"
		>
			<Bell size={15} />
			<span class="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-amber-500 text-[10px] font-bold text-gray-950 font-mono">
				2
			</span>
		</a>

		<!-- User Avatar Profile Dropdown -->
		<div class="relative border-l border-[#1F2937] pl-4">
			<button
				onclick={toggleProfileDropdown}
				class="flex items-center gap-2.5 rounded-lg p-1 hover:bg-gray-800 transition-colors cursor-pointer"
			>
				<img
					src={authStore.profile?.avatar_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop&q=80'}
					alt="User avatar"
					class="h-7 w-7 rounded-full border border-indigo-500/30 object-cover"
				/>
				<div class="hidden md:block text-left">
					<div class="text-xs font-semibold text-gray-200">
						{authStore.profile?.full_name || 'Alex Moreno'}
					</div>
					<div class="text-[10px] text-gray-400">Mánager de Roster</div>
				</div>
				<ChevronDown size={13} class="text-gray-400 hidden sm:block" />
			</button>

			{#if isProfileDropdownOpen}
				<div
					class="absolute right-0 mt-2 w-52 rounded-xl border border-[#2D3748] bg-[#111827] p-1.5 shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-100"
				>
					<div class="px-3 py-2 border-b border-[#1F2937]">
						<div class="text-xs font-bold text-white truncate">
							{authStore.profile?.full_name || 'Alex Moreno'}
						</div>
						<div class="text-[10px] text-gray-400 font-mono truncate">
							{authStore.profile?.email || 'manager@koatalent.com'}
						</div>
					</div>

					<div class="py-1">
						<a
							href="/profile"
							onclick={() => (isProfileDropdownOpen = false)}
							class="flex items-center gap-2 rounded-lg px-2.5 py-2 text-xs text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
						>
							<User size={14} />
							<span>Mi Perfil & Seguridad</span>
						</a>

						<a
							href="/tenants"
							onclick={() => (isProfileDropdownOpen = false)}
							class="flex items-center gap-2 rounded-lg px-2.5 py-2 text-xs text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
						>
							<Building2 size={14} />
							<span>Organizaciones</span>
						</a>
					</div>

					<div class="border-t border-[#1F2937] pt-1">
						<button
							onclick={handleLogout}
							class="flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-xs text-rose-400 hover:bg-rose-500/10 transition-colors"
						>
							<LogOut size={14} />
							<span>Cerrar Sesión</span>
						</button>
					</div>
				</div>
			{/if}
		</div>
	</div>
</header>
