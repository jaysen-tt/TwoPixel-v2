import { defineStore } from 'pinia';
import { router } from '@/router';
import axios from 'axios';

const BYPASS_LOGIN = false;

export const useAuthStore = defineStore({
  id: 'auth',
  state: () => ({
    // @ts-ignore
    username: '',
    returnUrl: null
  }),
  actions: {
    async login(username: string, password: string): Promise<void> {
      try {
        const res = await axios.post('/api/auth/login', {
          username: username,
          password: password
        });
    
        if (res.data.status === 'error') {
          return Promise.reject(res.data.message);
        }
    
        this.username = res.data.data.username
        localStorage.setItem('user', this.username);
        localStorage.setItem('token', res.data.data.token);
        localStorage.setItem('change_pwd_hint', res.data.data?.change_pwd_hint);
        localStorage.setItem('supabase-access-token', res.data.data?.supabase_access_token || '');
        localStorage.setItem('supabase-refresh-token', res.data.data?.supabase_refresh_token || '');
        localStorage.setItem('supabase-user', JSON.stringify(res.data.data?.supabase_user || {}));
        router.push(this.returnUrl || '/dashboard/default');
      } catch (error) {
        return Promise.reject(error);
      }
    },
    async signup(email: string, password: string): Promise<void> {
      try {
        const res = await axios.post('/api/auth/signup', { email, password });
        if (res.data.status === 'error') {
          return Promise.reject(res.data.message);
        }
        const data = res.data.data || {};
        const dashboardToken = String(data.token || '').trim();
        if (!dashboardToken) {
          return Promise.reject('注册成功，请先去邮箱完成验证，再返回登录。');
        }
        this.username = String(data.username || email).trim();
        localStorage.setItem('user', this.username);
        localStorage.setItem('token', dashboardToken);
        localStorage.setItem('supabase-access-token', data.supabase_access_token || '');
        localStorage.setItem('supabase-refresh-token', data.supabase_refresh_token || '');
        localStorage.setItem('supabase-user', JSON.stringify(data.supabase_user || {}));
        router.push(this.returnUrl || '/dashboard/default');
      } catch (error) {
        return Promise.reject(error);
      }
    },
    logout() {
      this.username = '';
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      localStorage.removeItem('supabase-access-token');
      localStorage.removeItem('supabase-refresh-token');
      localStorage.removeItem('supabase-user');
      router.push('/auth/login');
    },
    has_token(): boolean {
      if (BYPASS_LOGIN) return true;
      return !!localStorage.getItem('token');
    }
  }
});
