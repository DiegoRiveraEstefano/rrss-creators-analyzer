import { authService, type UserProfile } from '$lib/services/authService';
import { supabase } from '$lib/supabase/client';
import { tenantStore } from '$lib/stores/tenantStore.svelte';
import { queryClient } from '$lib/query/queryClient';
import type { User } from '@supabase/supabase-js';

class AuthStore {
	user = $state<User | null>(null);
	profile = $state<UserProfile | null>(null);
	isLoading = $state<boolean>(true);
	isInitialized = $state<boolean>(false);
	isAuthenticated = $derived(Boolean(this.user));

	private initialized = false;

	/**
	 * Limpia el estado reactivo, la caché de consultas, almacenes dependientes y almacenamiento local/cookies.
	 */
	async clearSession(clearStorage = true) {
		this.user = null;
		this.profile = null;
		tenantStore.reset();
		try {
			queryClient.clear();
		} catch (e) {
			console.warn('Error clearing queryClient cache:', e);
		}

		if (clearStorage) {
			await authService.clearAllAuthData();
		}
	}

	async init() {
		if (this.initialized) return;
		this.initialized = true;
		this.isLoading = true;

		try {
			const sessionData = await authService.getSession();
			if (sessionData.user) {
				this.user = sessionData.user;
				try {
					this.profile = await authService.getCurrentProfile();
				} catch (err) {
					console.warn('Could not fetch profile on init:', err);
				}
				// Cargar organizaciones si hay un usuario autenticado
				await tenantStore.loadOrganizations();
			} else {
				this.user = null;
				this.profile = null;
			}
		} catch (error) {
			console.warn('Error checking session on init:', error);
			this.user = null;
			this.profile = null;
		} finally {
			this.isLoading = false;
			this.isInitialized = true;
		}

		// Escuchar cambios de sesión en tiempo real (login, logout, refresh de token)
		supabase.auth.onAuthStateChange(async (event, session) => {
			if (event === 'SIGNED_OUT' || !session || !session.user) {
				this.user = null;
				this.profile = null;
				tenantStore.reset();
				try {
					queryClient.clear();
				} catch (e) {
					console.warn('Error clearing queryClient cache:', e);
				}
				this.isLoading = false;
				return;
			}

			if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED' || event === 'USER_UPDATED') {
				this.user = session.user;
				try {
					this.profile = await authService.getCurrentProfile();
				} catch (err) {
					console.warn('Error fetching profile on auth change:', err);
				}
				await tenantStore.loadOrganizations();
				this.isLoading = false;
			}
		});
	}

	async signIn(email: string, password?: string) {
		this.isLoading = true;
		try {
			const res = await authService.signIn({ email, password });
			this.user = res.user;
			this.profile = await authService.getCurrentProfile();
			await tenantStore.loadOrganizations();
			return res;
		} catch (error) {
			this.user = null;
			this.profile = null;
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async signUp(email: string, password?: string, fullName?: string) {
		this.isLoading = true;
		try {
			const res = await authService.signUp({ email, password, fullName });
			this.user = res.user;
			this.profile = await authService.getCurrentProfile();
			await tenantStore.loadOrganizations();
			return res;
		} catch (error) {
			this.user = null;
			this.profile = null;
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async resetPassword(email: string) {
		return authService.resetPassword(email);
	}

	async updatePassword(newPassword: string) {
		return authService.updatePassword(newPassword);
	}

	async updateProfile(updates: { full_name?: string; avatar_url?: string }) {
		const updated = await authService.updateProfile(updates);
		this.profile = updated;
		return updated;
	}

	async signOut() {
		this.isLoading = true;
		try {
			await this.clearSession(true);
		} finally {
			this.isLoading = false;
		}
	}
}

export const authStore = new AuthStore();
