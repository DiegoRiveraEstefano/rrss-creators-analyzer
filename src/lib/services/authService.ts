import { supabase } from '$lib/supabase/client';
import type { Database } from '$lib/supabase/database.types';

export interface UserProfile {
	id: string;
	email: string;
	full_name: string | null;
	avatar_url: string | null;
}

/**
 * Limpia de forma exhaustiva LocalStorage, SessionStorage y todas las cookies del navegador.
 */
export function clearClientStorageAndCookies(): void {
	if (typeof window === 'undefined') return;

	// 1. Limpiar LocalStorage
	try {
		localStorage.clear();
	} catch (e) {
		console.warn('Error al limpiar localStorage:', e);
	}

	// 2. Limpiar SessionStorage
	try {
		sessionStorage.clear();
	} catch (e) {
		console.warn('Error al limpiar sessionStorage:', e);
	}

	// 3. Limpiar todas las cookies accesibles
	try {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i];
			const eqPos = cookie.indexOf('=');
			const name = (eqPos > -1 ? cookie.slice(0, eqPos) : cookie).trim();
			if (name) {
				const hostname = window.location.hostname;
				// Expirar en diferentes combinaciones de path y dominio
				document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;SameSite=Lax`;
				document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=${hostname};SameSite=Lax`;
				document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=.${hostname};SameSite=Lax`;
			}
		}
	} catch (e) {
		console.warn('Error al limpiar cookies:', e);
	}
}

export const authService = {
	/**
	 * Valida la sesión directamente contra el servidor de Supabase Auth con getUser().
	 * Si el token expiró, fue revocado o es inválido, retorna null.
	 */
	async validateServerSession() {
		try {
			const { data, error } = await supabase.auth.getUser();
			if (error || !data.user) {
				return { user: null, session: null };
			}
			const { data: sessionData } = await supabase.auth.getSession();
			return { user: data.user, session: sessionData.session };
		} catch (err) {
			console.warn('Error al validar sesión en servidor:', err);
			return { user: null, session: null };
		}
	},

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

	async clearAllAuthData() {
		try {
			await supabase.auth.signOut({ scope: 'local' });
		} catch (e) {
			console.warn('Error on local signOut:', e);
		}
		clearClientStorageAndCookies();
	},

	async signOut() {
		try {
			await supabase.auth.signOut();
		} catch (e) {
			console.warn('Error on supabase signOut:', e);
		}
		clearClientStorageAndCookies();
	}
};
