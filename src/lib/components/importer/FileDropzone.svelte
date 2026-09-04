<script lang="ts">
	import { UploadCloud, FileSpreadsheet, Download, AlertCircle } from 'lucide-svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		onFileSelected: (file: File) => void;
		isProcessing?: boolean;
	}

	let { onFileSelected, isProcessing = false }: Props = $props();

	let isDragging = $state(false);
	let fileInput: HTMLInputElement | null = $state(null);
	let errorMessage = $state<string | null>(null);

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		isDragging = true;
	}

	function handleDragLeave(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
		errorMessage = null;

		if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
			const file = e.dataTransfer.files[0];
			validateAndEmit(file);
		}
	}

	function handleFileInputChange(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files && target.files.length > 0) {
			const file = target.files[0];
			validateAndEmit(file);
		}
	}

	function validateAndEmit(file: File) {
		const name = file.name.toLowerCase();
		if (!name.endsWith('.csv') && !name.endsWith('.xlsx') && !name.endsWith('.txt')) {
			errorMessage = 'Formato no soportado. Por favor sube un archivo .csv o .xlsx';
			return;
		}
		onFileSelected(file);
	}

	function downloadSampleCsv() {
		const sampleCsv = `session_title,game_or_category,platform,streamed_at,duration_seconds,peak_viewers,avg_ccv,chat_messages_count,new_followers,ad_revenue,donations_revenue,subs_revenue,total_earnings
"Reroll y sorteo especial","Just Chatting","twitch","2026-09-01T18:00:00Z",14400,65000,42000,120000,2800,850.00,420.00,1950.00,3220.00
"Torneo de streamers día 1","Minecraft","twitch","2026-09-02T16:30:00Z",18000,92000,74000,280000,5400,1400.00,890.00,3200.00,5490.00
"Prueba nueva temporada","VALORANT","twitch","2026-09-03T20:00:00Z",10800,48000,31000,95000,1600,600.00,280.00,1400.00,2280.00`;

		const blob = new Blob([sampleCsv], { type: 'text/csv;charset=utf-8;' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = 'plantilla_streaming_metrics.csv';
		a.click();
		URL.revokeObjectURL(url);
	}
</script>

<div class="space-y-4">
	<div
		ondragover={handleDragOver}
		ondragleave={handleDragLeave}
		ondrop={handleDrop}
		role="region"
		aria-label="Zona para arrastrar y soltar reportes CSV y Excel"
		class="relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-200 {isDragging
			? 'border-indigo-500 bg-indigo-500/10 scale-[0.99]'
			: 'border-[#2D3748] bg-[#111827] hover:border-indigo-500/50 hover:bg-[#161F30]'}"
	>
		<input
			bind:this={fileInput}
			type="file"
			accept=".csv,.xlsx,.txt"
			class="hidden"
			onchange={handleFileInputChange}
		/>

		<div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-4 shadow-lg shadow-indigo-500/10">
			{#if isProcessing}
				<div class="h-6 w-6 animate-spin rounded-full border-2 border-indigo-400 border-t-transparent"></div>
			{:else}
				<UploadCloud size={28} />
			{/if}
		</div>

		<h4 class="text-base font-semibold text-white mb-1">
			Arrastra y suelta tu reporte de streaming aquí
		</h4>
		<p class="text-xs text-gray-400 max-w-sm mb-4">
			Archivos <span class="text-gray-200 font-mono font-semibold">.CSV</span> o <span class="text-gray-200 font-mono font-semibold">.XLSX</span> exportados desde Twitch Analytics, YouTube Studio o Kick Dashboard.
		</p>

		<div class="flex items-center gap-3">
			<Button
				variant="primary"
				size="sm"
				isLoading={isProcessing}
				onclick={() => fileInput?.click()}
			>
				<FileSpreadsheet size={15} />
				Seleccionar archivo
			</Button>

			<Button
				variant="outline"
				size="sm"
				onclick={downloadSampleCsv}
			>
				<Download size={15} />
				Descargar Plantilla CSV
			</Button>
		</div>

		{#if errorMessage}
			<div class="mt-4 flex items-center gap-2 rounded-lg bg-rose-500/10 border border-rose-500/20 px-3 py-2 text-xs text-rose-400">
				<AlertCircle size={15} />
				<span>{errorMessage}</span>
			</div>
		{/if}
	</div>
</div>
