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

        const payload = res?.data ?? {};
        if (payload?.status === 'error') {
          return Promise.reject(payload?.message || '登录失败，请稍后重试');
        }

        const data = payload?.data ?? {};
        const token = String(data?.token || '').trim();
        if (!token) {
          return Promise.reject(payload?.message || '登录失败：服务端未返回有效令牌');
        }

        this.username = String(data?.username || username).trim();
        localStorage.setItem('user', this.username);
        localStorage.setItem('token', token);
        localStorage.setItem('change_pwd_hint', String(Boolean(data?.change_pwd_hint)));
        localStorage.setItem('supabase-access-token', String(data?.supabase_access_token || ''));
        localStorage.setItem('supabase-refresh-token', String(data?.supabase_refresh_token || ''));
        localStorage.setItem('supabase-user', JSON.stringify(data?.supabase_user || {}));
        router.push(this.returnUrl || '/dashboard/default');
      } catch (error) {
        const message = (error as any)?.response?.data?.message
          || (error as any)?.message
          || '登录失败，请检查账号或网络';
        return Promise.reject(message);
      }
    },
    async signup(email: string, password: string): Promise<void> {
      try {
        const res = await axios.post('/api/auth/signup', { email, password });
        const payload = res?.data ?? {};
        if (payload?.status === 'error') {
          return Promise.reject(payload?.message || '注册失败，请稍后重试');
        }
        const data = payload?.data || {};
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
        const message = (error as any)?.response?.data?.message
          || (error as any)?.message
          || '注册失败，请稍后重试';
        return Promise.reject(message);
      }
    },
    async forgotPassword(email: string): Promise<string> {
      try {
        const normalizedEmail = String(email || '').trim().toLowerCase();
        const res = await axios.post('/api/auth/forgot-password', { email: normalizedEmail });
        const payload = res?.data ?? {};
        if (payload?.status === 'error') {
          return Promise.reject(payload?.message || '发送重置邮件失败');
        }
        return Promise.resolve(payload?.message || '已发送重置邮件，请检查收件箱');
      } catch (error) {
        const message = (error as any)?.response?.data?.message
          || (error as any)?.message
          || '发送重置邮件失败，请稍后重试';
        return Promise.reject(message);
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
