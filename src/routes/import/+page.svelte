<script lang="ts">
	import { tenantStore } from '$lib/stores/tenantStore.svelte';
	import { parseCsvFile, type ParseResult } from '$lib/utils/csvValidator';
	import { importService } from '$lib/services/importService';
	import FileDropzone from '$lib/components/importer/FileDropzone.svelte';
	import ImportPreview from '$lib/components/importer/ImportPreview.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import {
		FileSpreadsheet,
		CheckCircle2,
		Sparkles,
		ArrowRight,
		UploadCloud,
		UserCheck
	} from 'lucide-svelte';

	let parseResult = $state<ParseResult | null>(null);
	let isParsing = $state(false);
	let isUploading = $state(false);
	let isComplete = $state(false);
	let uploadedBatchCount = $state(0);
	let targetCreatorId = $state<string>('');

	// Asignar primer creador por defecto
	$effect(() => {
		if (tenantStore.creators.length > 0 && !targetCreatorId) {
			targetCreatorId = tenantStore.creators[0].id;
		}
	});

	async function handleFileSelected(file: File) {
		isParsing = true;
		try {
			const result = await parseCsvFile(file);
			parseResult = result;
		} catch (error) {
			console.error('Error parsing file:', error);
		} finally {
			isParsing = false;
		}
	}

	async function handleCommitImport() {
		if (!tenantStore.currentOrg || !parseResult || !targetCreatorId) return;

		isUploading = true;
		try {
			const res = await importService.uploadBatch(
				tenantStore.currentOrg.id,
				targetCreatorId,
				parseResult.filename,
				parseResult.validRows
			);

			if (res.success) {
				uploadedBatchCount = res.importedCount;
				isComplete = true;
			}
		} catch (error) {
			console.error('Error uploading batch:', error);
		} finally {
			isUploading = false;
		}
	}

	function resetImporter() {
		parseResult = null;
		isComplete = false;
		uploadedBatchCount = 0;
	}
</script>

<div class="max-w-4xl mx-auto space-y-6">
	<!-- Header -->
	<div class="text-center space-y-2">
		<Badge variant="indigo" size="sm" class="inline-flex">
			<Sparkles size={12} class="mr-1" />
			Motor de Ingestión en Cliente (Zero-Server-Load)
		</Badge>
		<h1 class="text-2xl font-bold tracking-tight text-white flex items-center justify-center gap-2">
			<FileSpreadsheet class="text-indigo-400" size={26} />
			<span>Smart CSV & Excel Importer</span>
		</h1>
		<p class="text-xs text-gray-400 max-w-lg mx-auto">
			Normaliza, valida y procesa reportes tabulares de streaming directamente en tu navegador antes de sincronizar con Supabase.
		</p>
	</div>

	<!-- Pasos del Wizard -->
	{#if isComplete}
		<!-- Estado Exitoso -->
		<div class="rounded-2xl border border-emerald-500/30 bg-[#111827] p-8 text-center shadow-2xl space-y-4 animate-in zoom-in-95 duration-200">
			<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-lg shadow-emerald-500/10">
				<CheckCircle2 size={32} />
			</div>

			<h3 class="text-lg font-bold text-white">¡Carga Masiva Completada con Éxito!</h3>
			<p class="text-xs text-gray-400 max-w-md mx-auto">
				Se han normalizado y registrado <span class="text-emerald-400 font-bold font-mono">{uploadedBatchCount} sesiones</span> de streaming protegidas bajo RLS en el tenant actual.
			</p>

			<div class="pt-4 flex items-center justify-center gap-3">
				<a href="/">
					<Button variant="primary" size="md">
						Ver en Dashboard Principal
						<ArrowRight size={16} />
					</Button>
				</a>

				<Button variant="outline" size="md" onclick={resetImporter}>
					Importar otro archivo
				</Button>
			</div>
		</div>
	{:else if !parseResult}
		<!-- Paso 1: Dropzone -->
		<FileDropzone onFileSelected={handleFileSelected} isProcessing={isParsing} />
	{:else}
		<!-- Paso 2: Configuración de Destino y Vista Previa -->
		<div class="space-y-6">
			<!-- Asignación de Creador -->
			<div class="rounded-xl border border-[#1F2937] bg-[#111827] p-5">
				<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
					<div class="flex items-center gap-3">
						<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
							<UserCheck size={20} />
						</div>
						<div>
							<h3 class="text-sm font-semibold text-white">Asignar Métricas a Creador</h3>
							<p class="text-xs text-gray-400">Selecciona el perfil de talento que corresponde a estos reportes</p>
						</div>
					</div>

					<div class="w-full sm:w-64">
						<Select
							options={tenantStore.creators.map((c) => ({
								value: c.id,
								label: `${c.display_name} (@${c.handle})`
							}))}
							bind:value={targetCreatorId}
						/>
					</div>
				</div>
			</div>

			<!-- Vista Previa y Validación -->
			<ImportPreview
				{parseResult}
				onCommit={handleCommitImport}
				onCancel={resetImporter}
				{isUploading}
			/>
		</div>
	{/if}
</div>
