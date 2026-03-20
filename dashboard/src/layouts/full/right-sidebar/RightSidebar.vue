<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useCustomizerStore } from '@/stores/customizer';
import { useI18n } from '@/i18n/composables';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const customizer = useCustomizerStore();

const isCollapsed = ref(true);

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

// Define navigation items for the right sidebar
// These are the same items that were in the top tabs
const navItems = [
  { key: 'core.navigation.chat', to: '/chat', icon: 'mdi-message-outline', mode: 'chat' },
  { key: 'core.navigation.settings', to: '/config#normal', icon: 'mdi-cog-outline', mode: 'bot' },
  { key: 'core.navigation.console', to: '/console', icon: 'mdi-file-document-outline', mode: 'bot' },
  { key: 'core.navigation.dashboard', to: '/dashboard/default', icon: 'mdi-chart-line', mode: 'bot' },
  { key: 'core.navigation.extension', to: '/extension#installed', icon: 'mdi-puzzle-outline', mode: 'bot' },
  { key: 'core.navigation.persona', to: '/persona', icon: 'mdi-view-dashboard-outline', mode: 'bot' },
  { key: 'core.navigation.cron', to: '/cron', icon: 'mdi-clock-outline', mode: 'bot' },
];

const isActive = (to: string) => {
  const [path, hash] = to.split('#');
  if (route.path !== path) return false;
  
  // Special case for chat: match any chat route
  if (path.startsWith('/chat')) {
    return route.path.startsWith('/chat');
  }
  
  if (hash && route.hash !== `#${hash}`) return false;
  return true;
};

const handleNavClick = (item: any) => {
  // Switch mode based on item type
  if (item.mode === 'chat') {
    customizer.SET_VIEW_MODE('chat');
  } else {
    customizer.SET_VIEW_MODE('bot');
  }
  router.push(item.to);
};
</script>

<template>
  <div class="right-sidebar" :class="{ 'sidebar-expanded': !isCollapsed }">
    <div class="sidebar-header">
      <div class="header-toggle" @click="toggleSidebar">
        <v-icon size="16">{{ isCollapsed ? 'mdi-chevron-left' : 'mdi-chevron-right' }}</v-icon>
      </div>
      <h3 v-if="!isCollapsed">TOOLS</h3>
    </div>
    
    <div class="sidebar-menu">
      <div 
        v-for="item in navItems" 
        :key="item.to"
        class="menu-item"
        :class="{ active: isActive(item.to) }"
        @click="handleNavClick(item)"
      >
        <v-tooltip :text="t(item.key)" location="left" :disabled="!isCollapsed">
          <template v-slot:activator="{ props }">
            <div class="menu-item-content" v-bind="props">
              <div class="icon-container">
                <v-icon size="20">{{ item.icon }}</v-icon>
              </div>
              <span v-if="!isCollapsed" class="menu-label">{{ t(item.key) }}</span>
            </div>
          </template>
        </v-tooltip>
      </div>
    </div>
    
    <div class="sidebar-footer">
      <div class="menu-item">
        <v-tooltip text="Help" location="left" :disabled="!isCollapsed">
          <template v-slot:activator="{ props }">
            <div class="menu-item-content" v-bind="props">
              <div class="icon-container">
                <v-icon size="20">mdi-help-circle-outline</v-icon>
              </div>
              <span v-if="!isCollapsed" class="menu-label">HELP</span>
            </div>
          </template>
        </v-tooltip>
      </div>
    </div>
  </div>
</template>

<style scoped>
.right-sidebar {
  width: 64px;
  height: 100vh;
  border-left: 1px solid rgba(var(--v-theme-border), 0.5);
  display: flex;
  flex-direction: column;
  background-color: rgb(var(--v-theme-background));
  padding: 16px 0;
  flex-shrink: 0;
  z-index: 50;
  transition: width 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
  overflow: hidden;
}

.sidebar-expanded {
  width: 200px;
}

.sidebar-header {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  position: relative;
}

.header-toggle {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgb(var(--v-theme-secondaryText));
  transition: all 0.2s ease;
}

.header-toggle:hover {
  background: rgba(var(--v-theme-surface), 0.5);
  color: rgb(var(--v-theme-primary));
}

.sidebar-header h3 {
  font-size: 12px;
  font-weight: 700;
  color: rgb(var(--v-theme-secondaryText));
  text-transform: uppercase;
  letter-spacing: 0.1em;
  white-space: nowrap;
  position: absolute;
  left: 56px;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  padding: 0 12px;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
  padding: 16px 12px 0;
  border-top: 1px solid rgba(var(--v-theme-border), 0.3);
}

.menu-item {
  cursor: pointer;
}

.menu-item-content {
  display: flex;
  align-items: center;
  height: 40px;
  border-radius: 12px;
  padding: 0;
  transition: all 0.2s ease;
  overflow: hidden;
}

.sidebar-expanded .menu-item-content {
  padding-right: 12px;
}

.icon-container {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgb(var(--v-theme-secondaryText));
  transition: color 0.2s ease;
  flex-shrink: 0;
}

.menu-label {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  color: rgb(var(--v-theme-secondaryText));
  opacity: 0;
  animation: fadeIn 0.2s forwards 0.1s;
}

@keyframes fadeIn {
  to { opacity: 1; }
}

.menu-item:hover .menu-item-content {
  background: rgba(var(--v-theme-surface), 0.5);
}

.menu-item:hover .icon-container,
.menu-item:hover .menu-label {
  color: rgb(var(--v-theme-primary));
}

.menu-item.active .menu-item-content {
  background-color: rgb(var(--v-theme-primaryText));
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.menu-item.active .icon-container,
.menu-item.active .menu-label {
  color: rgb(var(--v-theme-background));
}
</style>
