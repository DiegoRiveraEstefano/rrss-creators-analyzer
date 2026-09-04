import { queryOptions } from '@tanstack/svelte-query';
import { tenantService, type OrganizationWithStats, type TenantMemberDetail } from '$lib/services/tenantService';

export const tenantsQueryKeys = {
	all: ['tenants'] as const,
	list: () => [...tenantsQueryKeys.all, 'list'] as const,
	detail: (id: string | undefined) => [...tenantsQueryKeys.all, 'detail', id] as const,
	members: (orgId: string | undefined) => [...tenantsQueryKeys.all, 'members', orgId] as const
};

export function organizationsQueryOptions() {
	return queryOptions({
		queryKey: tenantsQueryKeys.list(),
		queryFn: async (): Promise<OrganizationWithStats[]> => {
			return tenantService.getOrganizations();
		}
	});
}

export function organizationMembersQueryOptions(orgId: string | undefined) {
	return queryOptions({
		queryKey: tenantsQueryKeys.members(orgId),
		queryFn: async (): Promise<TenantMemberDetail[]> => {
			if (!orgId) return [];
			return tenantService.getMembers(orgId);
		},
		enabled: !!orgId
	});
}
