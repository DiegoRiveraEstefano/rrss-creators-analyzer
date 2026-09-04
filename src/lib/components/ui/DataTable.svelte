<script lang="ts" generics="T extends Record<string, any>">
	import type { Column } from '$lib/types/ui';
	import {
		createTable,
		tableFeatures,
		stockFeatures,
		createSortedRowModel,
		createFilteredRowModel,
		createPaginatedRowModel,
		type SortingState,
		type PaginationState
	} from '@tanstack/svelte-table';
	import {
		ArrowUpDown,
		ArrowUp,
		ArrowDown,
		Search,
		ChevronLeft,
		ChevronRight,
		ChevronsLeft,
		ChevronsRight
	} from 'lucide-svelte';

	interface Props {
		data: T[];
		columns: Column<T>[];
		searchable?: boolean;
		searchPlaceholder?: string;
		searchKeys?: (keyof T & string)[];
		emptyMessage?: string;
		pageSize?: number;
		showPagination?: boolean;
		class?: string;
	}

	let {
		data,
		columns,
		searchable = true,
		searchPlaceholder = 'Buscar en tabla...',
		searchKeys = [],
		emptyMessage = 'No se encontraron registros',
		pageSize = 25,
		showPagination = true,
		class: className = ''
	}: Props = $props();

	let globalFilter = $state('');
	let sorting = $state<SortingState>([]);
	let pagination = $state<PaginationState>({
		pageIndex: 0,
		pageSize: 25
	});

	// Actualizar pageSize si la prop cambia
	$effect(() => {
		pagination.pageSize = pageSize;
	});

	// Mapear columnas
	const tableColumns = $derived(
		columns.map((col) => ({
			id: col.key,
			accessorKey: col.key,
			header: col.label,
			enableSorting: col.sortable !== false,
			meta: {
				align: col.align || 'left',
				isMono: !!col.isMono,
				render: col.render
			}
		}))
	);

	// Instancia reactiva de TanStack Table v9
	const table = createTable({
		features: tableFeatures({
			...stockFeatures,
			sortedRowModel: createSortedRowModel(),
			filteredRowModel: createFilteredRowModel(),
			paginatedRowModel: createPaginatedRowModel()
		}),
		get data() {
			return data;
		},
		get columns() {
			return tableColumns as any;
		},
		state: {
			get sorting() {
				return sorting;
			},
			get globalFilter() {
				return globalFilter;
			},
			get pagination() {
				return pagination;
			}
		},
		onSortingChange: (updater) => {
			sorting = typeof updater === 'function' ? updater(sorting) : updater;
		},
		onGlobalFilterChange: (updater) => {
			globalFilter = typeof updater === 'function' ? updater(globalFilter) : updater;
		},
		onPaginationChange: (updater) => {
			pagination = typeof updater === 'function' ? updater(pagination) : updater;
		},
		globalFilterFn: (row: any, columnId: string, filterValue: string) => {
			const query = String(filterValue || '').toLowerCase().trim();
			if (!query) return true;

			const keysToSearch =
				searchKeys.length > 0 ? searchKeys : (columns.map((c) => c.key) as (keyof T & string)[]);

			return keysToSearch.some((k) => {
				const val = row.original?.[k];
				return val !== undefined && val !== null && String(val).toLowerCase().includes(query);
			});
		}
	});

	const rows = $derived(table.getRowModel().rows);
	const totalFilteredRows = $derived(table.getFilteredRowModel().rows.length);
	const pageCount = $derived(table.getPageCount());
	const canPreviousPage = $derived(table.getCanPreviousPage());
	const canNextPage = $derived(table.getCanNextPage());
</script>

<div class="space-y-3 {className}">
	<!-- Barra superior: Búsqueda y contador -->
	{#if searchable || showPagination}
		<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
			{#if searchable}
				<div class="relative flex-1 max-w-sm w-full">
					<Search class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={15} />
					<input
						type="text"
						bind:value={globalFilter}
						placeholder={searchPlaceholder}
						class="w-full rounded-lg bg-[#111827] border border-[#2D3748] py-1.5 pl-9 pr-4 text-xs text-white placeholder-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-colors"
					/>
				</div>
			{/if}

			<div class="flex items-center gap-3 self-end sm:self-auto text-xs text-gray-400 font-mono">
				<span>
					{totalFilteredRows} {totalFilteredRows === 1 ? 'registro' : 'registros'}
				</span>

				{#if showPagination && totalFilteredRows > 10}
					<div class="flex items-center gap-1.5">
						<span class="text-gray-500">Filas:</span>
						<select
							value={pagination.pageSize}
							onchange={(e) => {
								table.setPageSize(Number((e.target as HTMLSelectElement).value));
							}}
							class="rounded bg-[#111827] border border-[#2D3748] px-2 py-1 text-xs text-gray-300 focus:border-indigo-500 focus:outline-none"
						>
							<option value={10}>10</option>
							<option value={25}>25</option>
							<option value={50}>50</option>
							<option value={100}>100</option>
						</select>
					</div>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Tabla con TanStack Table Core -->
	<div class="overflow-hidden rounded-xl border border-[#1F2937] bg-[#111827] shadow-xl">
		<div class="overflow-x-auto max-h-[560px]">
			<table class="w-full text-left border-collapse text-xs">
				<thead
					class="sticky top-0 z-10 bg-[#161F30]/95 backdrop-blur-md border-b border-[#2D3748] text-gray-300 font-semibold tracking-wider"
				>
					{#each table.getHeaderGroups() as headerGroup}
						<tr>
							{#each headerGroup.headers as header}
								{@const colMeta = (header.column.columnDef.meta || {}) as any}
								{@const isSortable = header.column.getCanSort()}
								{@const sortDir = header.column.getIsSorted()}

								<th
									scope="col"
									class="px-4 py-3 select-none {colMeta.align === 'right'
										? 'text-right'
										: colMeta.align === 'center'
											? 'text-center'
											: 'text-left'} {isSortable
										? 'cursor-pointer hover:text-white transition-colors'
										: ''}"
									onclick={() => isSortable && header.column.toggleSorting()}
								>
									<div
										class="inline-flex items-center gap-1.5 {colMeta.align === 'right'
											? 'justify-end'
											: colMeta.align === 'center'
												? 'justify-center'
												: 'justify-start'}"
									>
										<span>{header.column.columnDef.header}</span>
										{#if isSortable}
											{#if sortDir === 'asc'}
												<ArrowUp size={14} class="text-indigo-400 stroke-[2.5]" />
											{:else if sortDir === 'desc'}
												<ArrowDown size={14} class="text-indigo-400 stroke-[2.5]" />
											{:else}
												<ArrowUpDown size={12} class="text-gray-500 opacity-60 hover:opacity-100" />
											{/if}
										{/if}
									</div>
								</th>
							{/each}
						</tr>
					{/each}
				</thead>

				<tbody class="divide-y divide-[#1F2937] text-gray-300">
					{#if rows.length === 0}
						<tr>
							<td colspan={columns.length} class="px-6 py-12 text-center text-gray-400">
								<div class="flex flex-col items-center justify-center space-y-2">
									<div
										class="h-10 w-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-400"
									>
										<Search size={20} />
									</div>
									<p class="text-sm font-medium">{emptyMessage}</p>
									{#if globalFilter}
										<p class="text-xs text-gray-400">Prueba con otro término de búsqueda.</p>
									{/if}
								</div>
							</td>
						</tr>
					{:else}
						{#each rows as row, i}
							<tr
								class="transition-colors duration-150 hover:bg-[#1E293B]/60 {i % 2 === 1
									? 'bg-[#111827]/40'
									: ''}"
							>
								{#each row.getVisibleCells() as cell}
									{@const colMeta = (cell.column.columnDef.meta || {}) as any}
									{@const value = cell.getValue()}

									<td
										class="px-4 py-3 whitespace-nowrap {colMeta.align === 'right'
											? 'text-right'
											: colMeta.align === 'center'
												? 'text-center'
												: 'text-left'} {colMeta.isMono ? 'font-mono text-gray-200' : ''}"
									>
										{#if colMeta.render}
											{@render colMeta.render({ row: row.original, value })}
										{:else}
											{value ?? '—'}
										{/if}
									</td>
								{/each}
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>

		<!-- Barra de paginación TanStack Table -->
		{#if showPagination && pageCount > 1}
			<div
				class="flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-[#1F2937] bg-[#141C2B]/80 px-4 py-3 text-xs text-gray-400"
			>
				<div class="font-mono">
					Página <span class="text-white font-semibold">{pagination.pageIndex + 1}</span> de{' '}
					<span class="text-white font-semibold">{pageCount}</span> ({totalFilteredRows} elementos)
				</div>

				<div class="flex items-center gap-1.5">
					<button
						onclick={() => table.setPageIndex(0)}
						disabled={!canPreviousPage}
						class="flex h-7 w-7 items-center justify-center rounded-lg border border-[#2D3748] bg-[#111827] text-gray-300 transition-colors hover:border-indigo-500 hover:text-white disabled:opacity-40 disabled:hover:border-[#2D3748] disabled:cursor-not-allowed"
						title="Primera página"
					>
						<ChevronsLeft size={14} />
					</button>

					<button
						onclick={() => table.previousPage()}
						disabled={!canPreviousPage}
						class="flex h-7 w-7 items-center justify-center rounded-lg border border-[#2D3748] bg-[#111827] text-gray-300 transition-colors hover:border-indigo-500 hover:text-white disabled:opacity-40 disabled:hover:border-[#2D3748] disabled:cursor-not-allowed"
						title="Página anterior"
					>
						<ChevronLeft size={14} />
					</button>

					<button
						onclick={() => table.nextPage()}
						disabled={!canNextPage}
						class="flex h-7 w-7 items-center justify-center rounded-lg border border-[#2D3748] bg-[#111827] text-gray-300 transition-colors hover:border-indigo-500 hover:text-white disabled:opacity-40 disabled:hover:border-[#2D3748] disabled:cursor-not-allowed"
						title="Página siguiente"
					>
						<ChevronRight size={14} />
					</button>

					<button
						onclick={() => table.setPageIndex(pageCount - 1)}
						disabled={!canNextPage}
						class="flex h-7 w-7 items-center justify-center rounded-lg border border-[#2D3748] bg-[#111827] text-gray-300 transition-colors hover:border-indigo-500 hover:text-white disabled:opacity-40 disabled:hover:border-[#2D3748] disabled:cursor-not-allowed"
						title="Última página"
					>
						<ChevronsRight size={14} />
					</button>
				</div>
			</div>
		{/if}
	</div>
</div>
