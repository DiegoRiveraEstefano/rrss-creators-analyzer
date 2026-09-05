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
		User
	} from 'lucide-svelte';

	const navItems = [
		{ href: '/', label: 'Resumen Ejecutivo', icon: LayoutDashboard },
		{ href: '/roster', label: 'Roster de Creadores', icon: Users },
		{ href: '/lives', label: 'Sesiones en Vivo (Lives)', icon: Radio },
		{ href: '/videos', label: 'Videos Subidos', icon: Video },
		{ href: '/raw-data', label: 'Datos Crudos (Tablas)', icon: Database },
		{ href: '/import', label: 'Importador CSV / Excel', icon: FileSpreadsheet, badge: 'Smart' },
		{ href: '/analytics', label: 'Analítica Global', icon: LineChart },
		{ href: '/alerts', label: 'Alertas & Sanciones', icon: AlertTriangle, count: 2 }
	];

	const managementItems = [
		{ href: '/tenants', label: 'Organizaciones (Tenants)', icon: Building2 },
		{ href: '/profile', label: 'Mi Perfil & Cuenta', icon: User }
	];
</script>

<aside class="flex w-64 flex-col justify-between border-r border-[#1F2937] bg-[#090D16] p-4 min-h-screen select-none">
	<div class="space-y-6">
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
			<div class="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
				Módulos Analíticos
			</div>

			{#each navItems as item}
				{@const isActive = page.url.pathname === item.href}
				<a
					href={item.href}
					class="group flex items-center justify-between rounded-xl px-3.5 py-2.5 text-xs font-medium transition-all duration-150 {isActive
						? 'bg-gradient-to-r from-indigo-600/20 to-indigo-600/5 text-white border border-indigo-500/30 shadow-sm shadow-indigo-500/10'
						: 'text-gray-400 hover:bg-[#111827] hover:text-gray-200'}"
				>
					<div class="flex items-center gap-3">
						<item.icon
							size={17}
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
		<div class="space-y-1 pt-2">
			<div class="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
				Gestión & Configuración
			</div>

			{#each managementItems as item}
				{@const isActive = page.url.pathname === item.href}
				<a
					href={item.href}
					class="group flex items-center justify-between rounded-xl px-3.5 py-2.5 text-xs font-medium transition-all duration-150 {isActive
						? 'bg-gradient-to-r from-indigo-600/20 to-indigo-600/5 text-white border border-indigo-500/30 shadow-sm shadow-indigo-500/10'
						: 'text-gray-400 hover:bg-[#111827] hover:text-gray-200'}"
				>
					<div class="flex items-center gap-3">
						<item.icon
							size={17}
							class="transition-colors {isActive ? 'text-indigo-400' : 'text-gray-400 group-hover:text-gray-300'}"
						/>
						<span>{item.label}</span>
					</div>
				</a>
			{/each}
		</div>
	</div>

	<!-- Bottom System Information -->
	<div class="pt-4 border-t border-[#1F2937]">
		<div class="px-2 text-center text-[10px] text-gray-400 font-mono">
			Cloudflare Pages SPA • v0.2.0
		</div>
	</div>
</aside>
