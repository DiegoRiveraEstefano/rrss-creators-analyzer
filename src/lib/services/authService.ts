import { supabase } from '$lib/supabase/client';
import type { Database } from '$lib/supabase/database.types';

export interface UserProfile {
	id: string;
	email: string;
	full_name: string | null;
	avatar_url: string | null;
}

export const authService = {
	async getSession() {
		const { data, error } = await supabase.auth.getSession();
		if (error) throw error;
		return { user: data.session?.user ?? null, session: data.session };
	},

	async getCurrentProfile(): Promise<UserProfile | null> {
		const { data: userData } = await supabase.auth.getUser();
		if (!userData.user) return null;

		const { data, error } = await supabase
			.from('profiles')
			.select('*')
			.eq('id', userData.user.id)
			.maybeSingle();

		if (error || !data) {
			return {
				id: userData.user.id,
				email: userData.user.email || '',
				full_name: userData.user.user_metadata?.full_name || 'Usuario',
				avatar_url: userData.user.user_metadata?.avatar_url || null
			};
		}
		return data;
	},

	async signIn(credentials: { email: string; password?: string }) {
		const { data, error } = await supabase.auth.signInWithPassword({
			email: credentials.email,
			password: credentials.password || ''
		});

		if (error) throw error;
		return data;
	},

	async signUp(credentials: { email: string; password?: string; fullName?: string }) {
		const { data, error } = await supabase.auth.signUp({
			email: credentials.email,
			password: credentials.password || '',
			options: {
				data: {
					full_name: credentials.fullName
				}
			}
		});

		if (error) throw error;
		return data;
	},

	async resetPassword(email: string) {
		const { error } = await supabase.auth.resetPasswordForEmail(email, {
			redirectTo: `${window.location.origin}/update-password`
		});

		if (error) throw error;
		return { success: true };
	},

	async updatePassword(newPassword: string) {
		const { error } = await supabase.auth.updateUser({
			password: newPassword
		});

		if (error) throw error;
		return { success: true };
	},

	async updateProfile(updates: { full_name?: string; avatar_url?: string }): Promise<UserProfile> {
		const { data: userData } = await supabase.auth.getUser();
		if (!userData.user) throw new Error('No user logged in');

		const { data, error } = await supabase
			.from('profiles')
			.update({
				full_name: updates.full_name,
				avatar_url: updates.avatar_url,
				updated_at: new Date().toISOString()
			})
			.eq('id', userData.user.id)
			.select()
			.single();

		if (error) throw error;
		return data;
	},

	async signOut() {
		await supabase.auth.signOut();
	}
};
