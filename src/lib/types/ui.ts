import type { Snippet } from 'svelte';

export interface Column<T> {
	key: keyof T & string;
	label: string;
	sortable?: boolean;
	align?: 'left' | 'center' | 'right';
	isMono?: boolean;
	render?: Snippet<[{ row: T; value: any }]>;
}
