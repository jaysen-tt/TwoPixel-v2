<script setup lang="ts">
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useCustomizerStore } from '@/stores/customizer';
import { useI18n } from '@/i18n/composables';

const router = useRouter();
const route = useRoute();
const customizer = useCustomizerStore();
const { t } = useI18n();

const botModules = [
  { key: 'core.navigation.config', to: '/config#normal' },
  { key: 'core.navigation.providers', to: '/providers' },
  { key: 'core.navigation.platforms', to: '/platforms' },
  { key: 'core.navigation.extension', to: '/extension#installed' },
  { key: 'core.navigation.persona', to: '/persona' },
  { key: 'core.navigation.knowledgeBase', to: '/knowledge-base' },
  { key: 'core.navigation.cron', to: '/cron' },
  { key: 'core.navigation.console', to: '/console' },
];

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
  <div class="tp-topnav">
    <div class="tp-topnav-head">
      <div class="tp-brand">
        <div class="tp-brand-mark">TP</div>
        <div class="tp-brand-copy">
          <h3>TwoPixel</h3>
          <p>Agent Console</p>
        </div>
      </div>
      <v-btn-toggle
        v-model="mode"
        mandatory
        density="comfortable"
        rounded="pill"
        color="primary"
      >
        <v-btn value="chat" rounded="pill" class="px-6">{{ t('core.navigation.chat') }}</v-btn>
        <v-btn value="bot" rounded="pill" class="px-6">Studio</v-btn>
      </v-btn-toggle>
      <div class="tp-status">
        <span class="tp-status-dot"></span>
        <span>Live</span>
      </div>
    </div>
    <div v-if="mode === 'bot'" class="tp-modules">
      <v-btn
        v-for="item in botModules"
        :key="item.to"
        variant="text"
        rounded="pill"
        :class="['tp-module-btn', { active: isModuleActive(item.to) }]"
        @click="go(item.to)"
      >
        {{ t(item.key) }}
      </v-btn>
    </div>
    <div v-else class="tp-chat-tip">
      <span>{{ t('core.navigation.chat') }} Mode · TwoPixel Runtime</span>
    </div>
  </div>
</template>

<style scoped>
.tp-topnav {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  background: rgb(var(--v-theme-surface));
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 16px 10px;
}

.tp-topnav-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.tp-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tp-brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: #fff;
  background: rgb(var(--v-theme-primary));
}

.tp-brand-copy {
  display: flex;
  flex-direction: column;
  line-height: 1.05;
}

.tp-brand-copy h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: rgb(var(--v-theme-on-surface));
}

.tp-brand-copy p {
  margin: 1px 0 0;
  font-size: 11px;
  opacity: 0.65;
  color: rgb(var(--v-theme-on-surface));
}

.tp-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  opacity: 0.72;
}

.tp-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.15);
}

.tp-modules {
  display: flex;
  align-items: center;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.tp-module-btn {
  opacity: 0.78;
  min-width: max-content;
  font-weight: 600;
}

.tp-module-btn.active {
  opacity: 1;
  background: rgba(0, 0, 0, 0.04);
  color: rgb(var(--v-theme-primary));
}

.tp-chat-tip {
  text-align: center;
  opacity: 0.7;
  font-size: 12px;
}

:deep(.v-theme--dark) .tp-topnav {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  background: rgb(var(--v-theme-surface));
}

:deep(.v-theme--dark) .tp-brand-copy h3 {
  color: rgb(var(--v-theme-on-surface));
}

:deep(.v-theme--dark) .tp-module-btn.active {
  background: rgba(255, 255, 255, 0.04);
}

@media (max-width: 860px) {
  .tp-topnav-head {
    flex-wrap: wrap;
  }

  .tp-status {
    display: none;
  }
}
</style>
