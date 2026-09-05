<script lang="ts">
	import { page } from '$app/state';
	import {
		LayoutDashboard,
		Users,
		Video,
		Database,
		FileSpreadsheet,
		LineChart,
		AlertTriangle,
		Radio,
		Building2,
		User,
		Zap,
		ChevronDown,
		Table,
		Trophy,
		Activity,
		Eye,
		Calendar,
		Sparkles
	} from 'lucide-svelte';

	let isViewsDropdownOpen = $state(true);

	const navItems = [
		{ href: '/', label: 'Resumen Ejecutivo', icon: LayoutDashboard },
		{ href: '/roster', label: 'Roster de Creadores', icon: Users },
		{ href: '/lives', label: 'Sesiones en Vivo (Lives)', icon: Radio },
		{ href: '/videos', label: 'Videos Subidos', icon: Video },
		{ href: '/analytics', label: 'Analítica Global', icon: LineChart }
	];

	const viewSubItems = [
		{
			tab: 'mv_creator_performance',
			label: 'Rendimiento Creadores',
			badge: 'MV',
			icon: Zap
		},
		{
			tab: 'mv_platform_performance',
			label: 'Rendimiento Plataformas',
			badge: 'MV',
			icon: Zap
		},
		{
			tab: 'mv_platform_category',
			label: 'Estadísticas Categorías',
			badge: 'MV',
			icon: Zap
		},
		{
			tab: 'mv_monthly_revenue',
			label: 'Resumen Mensual Ingresos',
			badge: 'MV',
			icon: Calendar
		},
		{
			tab: 'mv_content_type',
			label: 'Métricas por Formato',
			badge: 'MV',
			icon: Video
		},
		{
			tab: 'v_creator_rankings',
			label: 'Leaderboard & Rankings',
			badge: 'SQL',
			icon: Trophy
		},
		{
			tab: 'v_daily_stream',
			label: 'Analítica Diaria Streams',
			badge: 'SQL',
			icon: Activity
		},
		{
			tab: 'v_video_details',
			label: 'Videos & Retorno ROI',
			badge: 'SQL',
			icon: Eye
		},
		{
			tab: 'v_recent_activity',
			label: 'Timeline de Actividad',
			badge: 'SQL',
			icon: Sparkles
		}
	];

	const bottomNavItems = [
		{ href: '/raw-data', label: 'Datos Crudos (Tablas)', icon: Database },
		{ href: '/import', label: 'Importador CSV / Excel', icon: FileSpreadsheet, badge: 'Smart' },
		{ href: '/alerts', label: 'Alertas & Sanciones', icon: AlertTriangle, count: 2 }
	];

	const managementItems = [
		{ href: '/tenants', label: 'Organizaciones (Tenants)', icon: Building2 },
		{ href: '/profile', label: 'Mi Perfil & Cuenta', icon: User }
	];

	let isViewsPage = $derived(page.url.pathname === '/views');
	let currentViewTab = $derived(page.url.searchParams.get('tab') || 'mv_creator_performance');
</script>

<aside class="flex w-64 flex-col justify-between border-r border-[#1F2937] bg-[#090D16] p-4 min-h-screen select-none">
	<div class="space-y-5">
		<!-- Brand & Logo -->
		<a href="/" class="flex items-center gap-3 px-2 py-1">
			<div class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-[#6366F1] to-[#06B6D4] text-white shadow-lg shadow-indigo-500/25">
				<Radio size={20} class="stroke-[2.5]" />
			</div>
			<div>
				<div class="text-sm font-bold tracking-tight text-white flex items-center gap-1.5">
					<span>RRSS</span>
					<span class="text-indigo-400">Creators</span>
				</div>
				<div class="text-[10px] font-medium uppercase tracking-wider text-gray-400">
					Streaming BI Suite
				</div>
			</div>
		</a>

		<!-- Main Analytics Navigation -->
		<nav class="space-y-1">
			<div class="px-3 pb-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
				Módulos Analíticos
			</div>

			{#each navItems as item}
				{@const isActive = page.url.pathname === item.href}
				<a
					href={item.href}
					class="group flex items-center justify-between rounded-xl px-3.5 py-2 text-xs font-medium transition-all duration-150 {isActive
						? 'bg-gradient-to-r from-indigo-600/20 to-indigo-600/5 text-white border border-indigo-500/30 shadow-sm shadow-indigo-500/10'
						: 'text-gray-400 hover:bg-[#111827] hover:text-gray-200'}"
				>
					<div class="flex items-center gap-3">
						<item.icon
							size={16}
							class="transition-colors {isActive ? 'text-indigo-400' : 'text-gray-400 group-hover:text-gray-300'}"
						/>
						<span>{item.label}</span>
					</div>
				</a>
			{/each}

			<!-- MÓDULO DESPLEGABLE: VISTAS MATERIALIZADAS & SQL -->
			<div class="pt-1">
				<div class="flex items-center justify-between rounded-xl transition-all duration-150 {isViewsPage
					? 'bg-gradient-to-r from-indigo-600/20 to-indigo-600/5 text-white border border-indigo-500/30 shadow-sm shadow-indigo-500/10'
					: 'text-gray-400 hover:bg-[#111827] hover:text-gray-200'}">
					<a
						href="/views"
						class="flex-1 flex items-center gap-3 px-3.5 py-2 text-xs font-medium"
					>
						<Zap size={16} class={isViewsPage ? 'text-indigo-400' : 'text-gray-400'} />
						<span>Vistas & Agregaciones</span>
					</a>

					<button
						type="button"
						onclick={() => (isViewsDropdownOpen = !isViewsDropdownOpen)}
						class="px-2.5 py-2 text-gray-400 hover:text-white transition-colors"
						aria-label="Alternar menú de vistas"
					>
						<ChevronDown
							size={14}
							class="transition-transform duration-200 {isViewsDropdownOpen ? 'rotate-180 text-indigo-400' : ''}"
						/>
					</button>
				</div>

				<!-- Sub-items del Dropdown -->
				{#if isViewsDropdownOpen}
					<div class="mt-1 ml-3 pl-2.5 border-l border-[#1F2937] space-y-0.5 animate-in fade-in duration-150">
						{#each viewSubItems as subItem}
							{@const isSubActive = isViewsPage && currentViewTab === subItem.tab}
							<a
								href="/views?tab={subItem.tab}"
								class="flex items-center justify-between rounded-lg px-2.5 py-1.5 text-[11px] transition-all {isSubActive
									? 'bg-indigo-600/25 text-white font-semibold border border-indigo-500/40 shadow-xs'
									: 'text-gray-400 hover:bg-[#141C2B] hover:text-gray-200'}"
							>
								<div class="flex items-center gap-2 truncate">
									<subItem.icon size={13} class={isSubActive ? 'text-indigo-400' : 'text-gray-500'} />
									<span class="truncate">{subItem.label}</span>
								</div>

								<span
									class="text-[9px] font-mono px-1 py-0.2 rounded shrink-0 {subItem.badge === 'MV'
										? 'bg-indigo-500/20 text-indigo-300'
										: 'bg-emerald-500/20 text-emerald-300'}"
								>
									{subItem.badge}
								</span>
							</a>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Resto de navegación -->
			{#each bottomNavItems as item}
				{@const isActive = page.url.pathname === item.href}
				<a
					href={item.href}
					class="group flex items-center justify-between rounded-xl px-3.5 py-2 text-xs font-medium transition-all duration-150 {isActive
						? 'bg-gradient-to-r from-indigo-600/20 to-indigo-600/5 text-white border border-indigo-500/30 shadow-sm shadow-indigo-500/10'
						: 'text-gray-400 hover:bg-[#111827] hover:text-gray-200'}"
				>
					<div class="flex items-center gap-3">
						<item.icon
							size={16}
							class="transition-colors {isActive ? 'text-indigo-400' : 'text-gray-400 group-hover:text-gray-300'}"
						/>
						<span>{item.label}</span>
					</div>

					{#if item.badge}
						<span class="rounded bg-indigo-500/20 px-1.5 py-0.5 text-[10px] font-semibold text-indigo-300 font-mono">
							{item.badge}
						</span>
					{:else if item.count}
						<span class="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-400 font-mono">
							{item.count}
						</span>
					{/if}
				</a>
			{/each}
		</nav>

		<!-- Administration & Tenant Management -->
		<div class="space-y-1 pt-1 border-t border-[#1F2937]/60">
			<div class="px-3 pb-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
				Gestión & Configuración
			</div>

			{#each managementItems as item}
				{@const isActive = page.url.pathname === item.href}
				<a
					href={item.href}
					class="group flex items-center justify-between rounded-xl px-3.5 py-2 text-xs font-medium transition-all duration-150 {isActive
						? 'bg-gradient-to-r from-indigo-600/20 to-indigo-600/5 text-white border border-indigo-500/30 shadow-sm shadow-indigo-500/10'
						: 'text-gray-400 hover:bg-[#111827] hover:text-gray-200'}"
				>
					<div class="flex items-center gap-3">
						<item.icon
							size={16}
							class="transition-colors {isActive ? 'text-indigo-400' : 'text-gray-400 group-hover:text-gray-300'}"
						/>
						<span>{item.label}</span>
					</div>
				</a>
			{/each}
		</div>
	</div>

	<!-- Bottom System Information -->
	<div class="pt-3 border-t border-[#1F2937]">
		<div class="px-2 text-center text-[10px] text-gray-400 font-mono">
			Cloudflare Pages SPA • v0.2.0
		</div>
	</div>
</aside>
