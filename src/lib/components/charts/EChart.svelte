<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import * as echarts from 'echarts';
	import type { ECharts, EChartsOption } from 'echarts';

	interface Props {
		options: EChartsOption;
		height?: string;
		class?: string;
	}

	let { options, height = '320px', class: className = '' }: Props = $props();

	let container: HTMLDivElement | null = $state(null);
	let chartInstance: ECharts | null = null;
	let resizeObserver: ResizeObserver | null = null;

	onMount(() => {
		if (!container) return;

		chartInstance = echarts.init(container, 'dark', {
			renderer: 'canvas'
		});

		chartInstance.setOption({
			backgroundColor: 'transparent',
			...options
		});

		// Configurar ResizeObserver para adaptarse fluidamente a la grilla
		resizeObserver = new ResizeObserver(() => {
			chartInstance?.resize();
		});
		resizeObserver.observe(container);

		const handleWindowResize = () => chartInstance?.resize();
		window.addEventListener('resize', handleWindowResize);

		return () => {
			window.removeEventListener('resize', handleWindowResize);
		};
	});

	$effect(() => {
		if (chartInstance && options) {
			chartInstance.setOption({
				backgroundColor: 'transparent',
				...options
			}, true);
		}
	});

	onDestroy(() => {
		resizeObserver?.disconnect();
		chartInstance?.dispose();
		chartInstance = null;
	});
</script>

<div bind:this={container} style="height: {height};" class="w-full {className}"></div>
