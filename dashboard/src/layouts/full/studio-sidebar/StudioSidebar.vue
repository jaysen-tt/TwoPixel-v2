<script setup lang="ts">
import { useI18n } from '@/i18n/composables';
import { useRouter, useRoute } from 'vue-router';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();

const botModules = [
  { key: 'core.navigation.config', to: '/config#normal', icon: 'mdi-cog' },
  { key: 'core.navigation.providers', to: '/providers', icon: 'mdi-creation' },
  { key: 'core.navigation.platforms', to: '/platforms', icon: 'mdi-robot' },
  { key: 'core.navigation.extension', to: '/extension#installed', icon: 'mdi-puzzle' },
  { key: 'core.navigation.persona', to: '/persona', icon: 'mdi-account-circle' },
  { key: 'core.navigation.knowledgeBase', to: '/knowledge-base', icon: 'mdi-book-open-variant' },
  { key: 'core.navigation.cron', to: '/cron', icon: 'mdi-clock-outline' },
  { key: 'core.navigation.console', to: '/console', icon: 'mdi-console' },
];

const isModuleActive = (to: string) => {
  const [path, hash] = to.split('#');
  if (route.path !== path) return false;
  if (!hash) return true;
  return route.hash === `#${hash}`;
};

const go = (to: string) => {
  router.push(to);
};
</script>

<template>
  <div class="studio-sidebar">
    <div class="sidebar-header">
      <h3>SETTINGS</h3>
    </div>
    
    <div class="sidebar-menu">
      <div 
        v-for="item in botModules" 
        :key="item.to"
        class="menu-item"
        :class="{ active: isModuleActive(item.to) }"
        @click="go(item.to)"
      >
        <v-icon size="18" class="mr-3 icon-module">{{ item.icon }}</v-icon>
        <span class="menu-text">{{ t(item.key) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.studio-sidebar {
  width: 260px;
  height: 100vh;
  border-right: 1px solid rgba(var(--v-theme-border), 0.5);
  display: flex;
  flex-direction: column;
  background: transparent;
  padding: 24px 16px;
  flex-shrink: 0;
}

.sidebar-header {
  margin-bottom: 24px;
  padding-left: 12px;
}

.sidebar-header h3 {
  font-size: 12px;
  font-weight: 700;
  color: rgb(var(--v-theme-textTertiary));
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: rgb(var(--v-theme-textSecondary));
  transition: all 0.2s ease;
  min-height: 44px;
}

.menu-text {
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.02em;
}

.icon-module {
  color: rgb(var(--v-theme-textTertiary));
  transition: color 0.2s ease;
}

.menu-item:hover {
  background: rgba(var(--v-theme-surface), 0.5);
  color: rgb(var(--v-theme-primary));
}

.menu-item:hover .icon-module {
  color: rgb(var(--v-theme-primary));
}

.menu-item.active {
  background-color: rgb(var(--v-theme-textPrimary)) !important;
  color: rgb(var(--v-theme-surface)) !important;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.menu-item.active .icon-module {
  color: rgb(var(--v-theme-surface)) !important;
}
</style>
