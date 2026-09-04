import { authService, type UserProfile } from '$lib/services/authService';

class AuthStore {
	user = $state<unknown | null>(null);
	profile = $state<UserProfile | null>(null);
	isLoading = $state<boolean>(true);
	isAuthenticated = $derived(Boolean(this.user || this.profile));

	async init() {
		this.isLoading = true;
		try {
			const sessionData = await authService.getSession();
			this.user = sessionData.user;
			this.profile = await authService.getCurrentProfile();
		} catch (error) {
			console.error('Error initializing auth:', error);
		} finally {
			this.isLoading = false;
		}
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
		await authService.signOut();
		this.user = null;
		this.profile = null;
	}
}

export const authStore = new AuthStore();
