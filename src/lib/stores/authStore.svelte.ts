import { authService, type UserProfile } from '$lib/services/authService';
import { supabase } from '$lib/supabase/client';

class AuthStore {
	user = $state<unknown | null>(null);
	profile = $state<UserProfile | null>(null);
	isLoading = $state<boolean>(true);
	isInitialized = $state<boolean>(false);
	isAuthenticated = $derived(Boolean(this.user || this.profile));

	private initialized = false;

	async init() {
		if (this.initialized) return;
		this.initialized = true;
		this.isLoading = true;

		try {
			const sessionData = await authService.getSession();
			this.user = sessionData.user;
			if (sessionData.user) {
				this.profile = await authService.getCurrentProfile();
			} else {
				this.profile = null;
			}
		} catch (error) {
			console.error('Error initializing auth:', error);
		} finally {
			this.isLoading = false;
			this.isInitialized = true;
		}

		// Escuchar cambios de sesión en tiempo real (login, logout, refresh de token)
		supabase.auth.onAuthStateChange(async (_event, session) => {
			this.user = session?.user ?? null;
			if (session?.user) {
				try {
					this.profile = await authService.getCurrentProfile();
				} catch (err) {
					console.error('Error fetching profile on auth change:', err);
				}
			} else {
				this.profile = null;
			}
			this.isLoading = false;
		});
	}

	async signIn(email: string, password?: string) {
		this.isLoading = true;
		try {
			const res = await authService.signIn({ email, password });
			this.user = res.user;
			this.profile = await authService.getCurrentProfile();
			return res;
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
			return res;
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
			await authService.signOut();
			this.user = null;
			this.profile = null;
		} finally {
			this.isLoading = false;
		}
	}
}

export const authStore = new AuthStore();
