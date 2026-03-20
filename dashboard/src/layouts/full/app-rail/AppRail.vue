<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useCustomizerStore } from '@/stores/customizer';
import { useI18n } from '@/i18n/composables';

const router = useRouter();
const customizer = useCustomizerStore();
const { t } = useI18n();

const mode = computed({
  get: () => customizer.viewMode,
  set: (val: 'bot' | 'chat') => {
    customizer.SET_VIEW_MODE(val);
    if (val === 'chat') {
      router.push('/chat');
      return;
    }
    router.push('/config#normal');
  },
});

</script>

<template>
  <div class="app-rail">
    <!-- Top: Brand -->
    <div class="rail-brand">
      <div class="rail-logo">TP</div>
    </div>

    <!-- Middle: Navigation -->
    <div class="rail-nav">
      <v-tooltip text="Chat" location="right">
        <template v-slot:activator="{ props }">
          <div 
            class="rail-item" 
            :class="{ active: mode === 'chat' }"
            @click="mode = 'chat'"
            v-bind="props"
          >
            <v-icon size="24" :color="mode === 'chat' ? 'white' : 'grey-lighten-1'">mdi-message-text-outline</v-icon>
          </div>
        </template>
      </v-tooltip>

      <v-tooltip text="Studio" location="right">
        <template v-slot:activator="{ props }">
          <div 
            class="rail-item" 
            :class="{ active: mode === 'bot' }"
            @click="mode = 'bot'"
            v-bind="props"
          >
            <v-icon size="24" :color="mode === 'bot' ? 'white' : 'grey-lighten-1'">mdi-view-grid-outline</v-icon>
          </div>
        </template>
      </v-tooltip>
    </div>

    <!-- Bottom: User / Settings -->
    <div class="rail-footer">
      <div class="rail-item" @click="router.push('/settings')">
        <v-icon size="24" color="grey-lighten-1">mdi-cog-outline</v-icon>
      </div>
      <div class="rail-avatar">
        <v-avatar size="32" color="grey-darken-3">
          <span class="text-caption">U</span>
        </v-avatar>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-rail {
  width: 72px;
  height: 100vh;
  background: #1A1A1A;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  z-index: 100;
  flex-shrink: 0;
}

.rail-brand {
  margin-bottom: 40px;
}

.rail-logo {
  width: 40px;
  height: 40px;
  background: #FFFFFF;
  color: #1A1A1A;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
}

.rail-nav {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
  width: 100%;
  align-items: center;
}

.rail-item {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.rail-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.rail-item.active {
  background: #22c55e; /* Green accent for active state */
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.rail-footer {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

/* Dark theme overrides if needed, but Rail is always dark by design in TwoPixel */
</style>
