<script setup lang="ts">
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useCustomizerStore } from '@/stores/customizer';
import { useI18n } from '@/i18n/composables';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const customizer = useCustomizerStore();

// Define tabs based on TwoPixel screenshot
const tabs = [
  { key: 'core.navigation.chat', to: '/chat', icon: 'mdi-message-outline', mode: 'chat' },
  { key: 'core.navigation.chatV3', to: '/chat-v3', icon: 'mdi-message-text-outline', mode: 'chat' }, // Placeholder
  { key: 'core.navigation.sessions', to: '/sessions', icon: 'mdi-database-outline', mode: 'chat' }, // Placeholder
  { key: 'core.navigation.logs', to: '/logs', icon: 'mdi-file-document-outline', mode: 'bot' },
  { key: 'core.navigation.usage', to: '/usage', icon: 'mdi-chart-line', mode: 'bot' },
  { key: 'core.navigation.skills', to: '/extension#installed', icon: 'mdi-puzzle-outline', mode: 'bot' },
  { key: 'core.navigation.templates', to: '/persona', icon: 'mdi-view-dashboard-outline', mode: 'bot' },
  { key: 'core.navigation.cron', to: '/cron', icon: 'mdi-clock-outline', mode: 'bot' },
  { key: 'core.navigation.settings', to: '/config#normal', icon: 'mdi-cog-outline', mode: 'bot' },
];

const currentTab = computed(() => {
  // Simple matching logic
  const path = route.path;
  const hash = route.hash;
  
  if (path.startsWith('/chat') && path !== '/chat-v3') return '/chat';
  
  // Find matching tab
  const match = tabs.find(tab => {
    const [tPath, tHash] = tab.to.split('#');
    if (path !== tPath) return false;
    if (tHash && hash !== `#${tHash}`) return false;
    return true;
  });
  
  return match?.to || '';
});

const handleTabClick = (tab: any) => {
  // Switch view mode if needed
  if (tab.mode === 'chat') {
    customizer.SET_VIEW_MODE('chat');
  } else {
    customizer.SET_VIEW_MODE('bot');
  }
  
  router.push(tab.to);
};
</script>

<template>
  <div class="tp-content-tabs">
    <div 
      v-for="tab in tabs" 
      :key="tab.to"
      class="tp-tab-item"
      :class="{ active: currentTab === tab.to }"
      @click="handleTabClick(tab)"
    >
      <v-icon size="16" class="mr-2 tab-icon">{{ tab.icon }}</v-icon>
      <span class="tab-text">{{ t(tab.key) || tab.key.split('.').pop()?.toUpperCase() }}</span>
    </div>
  </div>
</template>

<style scoped>
.tp-content-tabs {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background-color: rgb(var(--v-theme-background));
  border-bottom: 1px solid rgba(var(--v-theme-border), 0.5);
  overflow-x: auto;
  flex-shrink: 0;
}

.tp-tab-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  color: rgb(var(--v-theme-textSecondary));
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tp-tab-item:hover {
  background-color: rgba(var(--v-theme-surface), 0.5);
  color: rgb(var(--v-theme-primary));
}

.tp-tab-item.active {
  background-color: rgb(var(--v-theme-textPrimary));
  color: rgb(var(--v-theme-background));
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.tp-tab-item.active .tab-icon {
  color: rgb(var(--v-theme-background));
}

.tab-text {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tab-icon {
  opacity: 0.8;
}

/* Hide scrollbar */
.tp-content-tabs::-webkit-scrollbar {
  height: 0;
  width: 0;
}
</style>
