import { tenantService, type Organization, type OrganizationWithStats } from '$lib/services/tenantService';
import { creatorService, type CreatorWithChannels } from '$lib/services/creatorService';

class TenantStore {
	organizations = $state<OrganizationWithStats[]>([]);
	currentOrg = $state<OrganizationWithStats | null>(null);
	creators = $state<CreatorWithChannels[]>([]);
	selectedCreatorId = $state<string | null>(null);
	isLoading = $state<boolean>(false);

	selectedCreator = $derived(
		this.selectedCreatorId
			? this.creators.find((c) => c.id === this.selectedCreatorId) ?? null
			: null
	);

	async init() {
		await this.loadOrganizations();
	}

	async loadOrganizations() {
		this.isLoading = true;
		try {
			this.organizations = await tenantService.getOrganizations();
			if (this.organizations.length > 0) {
				if (!this.currentOrg || !this.organizations.some((o) => o.id === this.currentOrg?.id)) {
					this.currentOrg = this.organizations[0];
				}
				await this.loadCreators();
			} else {
				this.currentOrg = null;
				this.creators = [];
			}
		} catch (error) {
			console.warn('Error loading organizations:', error);
			this.organizations = [];
			this.currentOrg = null;
			this.creators = [];
		} finally {
			this.isLoading = false;
		}
	}

	async loadCreators() {
		if (!this.currentOrg) {
			this.creators = [];
			return;
		}
		try {
			this.creators = await creatorService.getCreators(this.currentOrg.id);
		} catch (error) {
			console.error('Error loading creators:', error);
			this.creators = [];
		}
	}

	async selectOrganization(orgId: string) {
		const found = this.organizations.find((o) => o.id === orgId);
		if (found) {
			this.currentOrg = found;
			this.selectedCreatorId = null;
			await this.loadCreators();
		}
	}

	async createOrganization(payload: { name: string; slug: string; plan?: string; logo_url?: string }) {
		const newOrg = await tenantService.createOrganization(payload);
		await this.loadOrganizations();
		this.selectOrganization(newOrg.id);
		return newOrg;
	}

	async updateOrganization(id: string, payload: { name?: string; plan?: string; logo_url?: string | null }) {
		const updated = await tenantService.updateOrganization(id, payload);
		await this.loadOrganizations();
		if (this.currentOrg?.id === id) {
			this.currentOrg = { ...this.currentOrg, ...updated };
		}
		return updated;
	}

	selectCreator(creatorId: string | null) {
		this.selectedCreatorId = creatorId;
	}

	reset() {
		this.organizations = [];
		this.currentOrg = null;
		this.creators = [];
		this.selectedCreatorId = null;
		this.isLoading = false;
	}
}

export const tenantStore = new TenantStore();
