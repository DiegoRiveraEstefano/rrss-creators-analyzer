import { supabase } from '$lib/supabase/client';
import type { Database, MemberRole } from '$lib/supabase/database.types';

export type Organization = Database['public']['Tables']['organizations']['Row'];
export type OrganizationMember = Database['public']['Tables']['organization_members']['Row'];

export interface OrganizationWithStats extends Organization {
	membersCount?: number;
	creatorsCount?: number;
	role?: MemberRole;
}

export interface TenantMemberDetail {
	id: string;
	organization_id: string;
	user_id: string;
	role: MemberRole;
	email: string;
	full_name: string | null;
	avatar_url?: string | null;
	created_at: string;
}

export const tenantService = {
	async getOrganizations(): Promise<OrganizationWithStats[]> {
		const { data, error } = await supabase
			.from('organizations')
			.select('*, organization_members(role)')
			.order('name');

		if (error) throw error;
		if (!data) return [];

		return data.map((org: any) => ({
			id: org.id,
			name: org.name,
			slug: org.slug,
			logo_url: org.logo_url,
			plan: org.plan,
			created_at: org.created_at,
			updated_at: org.updated_at,
			role: org.organization_members?.[0]?.role || 'manager'
		}));
	},

	async getOrganizationById(id: string): Promise<Organization | null> {
		const { data, error } = await supabase
			.from('organizations')
			.select('*')
			.eq('id', id)
			.maybeSingle();

		if (error) throw error;
		return data;
	},

	async createOrganization(payload: {
		name: string;
		slug: string;
		plan?: string;
		logo_url?: string;
	}): Promise<Organization> {
		const cleanSlug = payload.slug.toLowerCase().replace(/[^a-z0-9-]/g, '-');

		// Usar la función RPC atómica SECURITY DEFINER para evitar violaciones de RLS
		const { data, error } = await supabase.rpc('create_organization_with_owner', {
			p_name: payload.name.trim(),
			p_slug: cleanSlug,
			p_plan: payload.plan || 'standard',
			p_logo_url: payload.logo_url || null
		});

		if (error) throw error;
		if (!data) throw new Error('No se pudo crear la organización');

		return data as unknown as Organization;
	},

	async updateOrganization(
		id: string,
		updates: { name?: string; logo_url?: string | null; plan?: string }
	): Promise<Organization> {
		const { data, error } = await supabase
			.from('organizations')
			.update({
				...updates,
				updated_at: new Date().toISOString()
			})
			.eq('id', id)
			.select()
			.single();

		if (error) throw error;
		return data;
	},

	async getMembers(organizationId: string): Promise<TenantMemberDetail[]> {
		const { data, error } = await supabase
			.from('organization_members')
			.select('id, organization_id, user_id, role, created_at, profiles(email, full_name, avatar_url)')
			.eq('organization_id', organizationId);

		if (error) throw error;
		if (!data) return [];

		return data.map((item: any) => ({
			id: item.id,
			organization_id: item.organization_id,
			user_id: item.user_id,
			role: item.role,
			email: item.profiles?.email || '',
			full_name: item.profiles?.full_name || null,
			avatar_url: item.profiles?.avatar_url || null,
			created_at: item.created_at
		}));
	},

	async addMember(
		organizationId: string,
		member: { email: string; role: MemberRole; fullName?: string }
	): Promise<boolean> {
		const { data: profile, error: profileError } = await supabase
			.from('profiles')
			.select('id')
			.eq('email', member.email)
			.single();

		if (profileError || !profile) {
			throw new Error('No se encontró un usuario registrado con este correo electrónico.');
		}

		const { error } = await supabase.from('organization_members').insert({
			organization_id: organizationId,
			user_id: profile.id,
			role: member.role
		});

		if (error) throw error;
		return true;
	},

	async removeMember(memberId: string): Promise<boolean> {
		const { error } = await supabase
			.from('organization_members')
			.delete()
			.eq('id', memberId);

		if (error) throw error;
		return true;
	}
};
