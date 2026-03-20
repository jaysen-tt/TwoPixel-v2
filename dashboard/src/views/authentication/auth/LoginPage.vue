<script setup lang="ts">
import AuthLogin from '../authForms/AuthLogin.vue';
import LanguageSwitcher from '@/components/shared/LanguageSwitcher.vue';
import { onMounted, ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { useCustomizerStore } from "@/stores/customizer";
import { useModuleI18n } from '@/i18n/composables';
import { useTheme } from 'vuetify';

const cardVisible = ref(false);
const router = useRouter();
const authStore = useAuthStore();
const customizer = useCustomizerStore();
const { tm: t } = useModuleI18n('features/auth');
const theme = useTheme();

// 主题切换函数
function toggleTheme() {
  const newTheme = customizer.uiTheme === 'PurpleThemeDark' ? 'PurpleTheme' : 'PurpleThemeDark';
  customizer.SET_UI_THEME(newTheme);
  theme.global.name.value = newTheme;
}

onMounted(() => {
  // 检查用户是否已登录，如果已登录则重定向
  if (authStore.has_token()) {
    router.push(authStore.returnUrl || '/');
    return;
  }

  // 添加一个小延迟以获得更好的动画效果
  setTimeout(() => {
    cardVisible.value = true;
  }, 100);
});
</script>

<template>
  <div class="login-page-container">
    <v-card class="login-card" elevation="2" rounded="xl">
      <v-card-title class="pt-6 px-6">
        <div class="d-flex justify-space-between align-center w-100 mb-6">
          <img width="64" src="@/assets/images/astrbot_logo_mini.webp" alt="TwoPixel Logo" style="border-radius: 16px;">
          <div class="d-flex align-center gap-2">
            <LanguageSwitcher />
            <v-divider vertical class="mx-1"
              style="height: 16px !important; opacity: 0.3 !important; align-self: center !important;"></v-divider>
            <v-btn @click="toggleTheme" class="theme-toggle-btn" icon variant="text" size="small" color="default">
              <v-icon size="20">
                mdi-white-balance-sunny
              </v-icon>
              <v-tooltip activator="parent" location="top">
                {{ t('theme.switchToLight') }}
              </v-tooltip>
            </v-btn>
          </div>
        </div>
        <div class="text-h5 font-weight-medium mb-1" style="color: rgb(var(--v-theme-on-surface)); letter-spacing: -0.5px !important;">{{ t('logo.title') }}</div>
        <div class="text-body-2" style="color: rgb(var(--v-theme-on-surface-variant));">{{ t('logo.subtitle') }}</div>
      </v-card-title>
      <v-card-text class="px-6 pb-8">
        <AuthLogin />
      </v-card-text>
    </v-card>
  </div>
</template>

<style lang="scss">
.login-page-container {
  background-color: rgb(var(--v-theme-background));
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08) !important;
}
</style>
