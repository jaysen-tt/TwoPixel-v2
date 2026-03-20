<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router';
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import RightSidebar from './right-sidebar/RightSidebar.vue';
import MigrationDialog from '@/components/shared/MigrationDialog.vue';
import ReadmeDialog from '@/components/shared/ReadmeDialog.vue';
import Chat from '@/components/chat/Chat.vue';
import { useCustomizerStore } from '@/stores/customizer';
import { useRouterLoadingStore } from '@/stores/routerLoading';
import { useI18n } from '@/i18n/composables';

const FIRST_NOTICE_SEEN_KEY = 'astrbot:first_notice_seen:v1';

const customizer = useCustomizerStore();
const { locale } = useI18n();
const route = useRoute();
const routerLoadingStore = useRouterLoadingStore();

const isChatPage = computed(() => {
  return route.path.startsWith('/chat');
});

const showChatPage = computed(() => {
  return customizer.viewMode === 'chat';
});

const migrationDialog = ref<InstanceType<typeof MigrationDialog> | null>(null);
const showFirstNoticeDialog = ref(false);

const checkMigration = async (): Promise<boolean> => {
  try {
    const response = await axios.get('/api/stat/version');
    if (response.data.status === 'ok' && response.data.data.need_migration) {
      if (migrationDialog.value && typeof migrationDialog.value.open === 'function') {
        const result = await migrationDialog.value.open();
        if (result.success) {
          console.log('Migration completed successfully:', result.message);
          window.location.reload();
        }
      }
      return true;
    }
  } catch (error) {
    console.error('Failed to check migration status:', error);
  }
  return false;
};

const maybeShowFirstNotice = async () => {
  if (localStorage.getItem(FIRST_NOTICE_SEEN_KEY) === '1') {
    return;
  }

  try {
    const response = await axios.get('/api/stat/first-notice', {
      params: { locale: locale.value },
    });
    if (response.data.status !== 'ok') {
      return;
    }

    const content = response.data?.data?.content;
    if (typeof content === 'string' && content.trim().length > 0) {
      showFirstNoticeDialog.value = true;
      return;
    }

    localStorage.setItem(FIRST_NOTICE_SEEN_KEY, '1');
  } catch (error) {
    console.error('Failed to load first notice:', error);
  }
};

const onFirstNoticeDialogUpdate = (visible: boolean) => {
  showFirstNoticeDialog.value = visible;
  if (!visible) {
    localStorage.setItem(FIRST_NOTICE_SEEN_KEY, '1');
  }
};

onMounted(() => {
  setTimeout(async () => {
    const migrationPending = await checkMigration();
    if (!migrationPending) {
      await maybeShowFirstNotice();
    }
  }, 1000);
});
</script>

<template>
  <v-locale-provider>
    <v-app :theme="useCustomizerStore().uiTheme"
      :class="[customizer.fontTheme, customizer.mini_sidebar ? 'mini-sidebar' : '', customizer.inputBg ? 'inputWithbg' : '']"
    >
      <v-progress-linear
        v-if="routerLoadingStore.isLoading"
        :model-value="routerLoadingStore.progress"
        color="primary"
        height="2"
        fixed
        top
        style="z-index: 9999; position: absolute; opacity: 0.3; "
      />
      
      <!-- New Layout Structure: Single Sidebar -> Content -->
      <div class="tp-main-layout">
        <!-- 2. Main Content Area -->
        <v-main class="tp-content-area" :style="{
          background: 'rgb(var(--v-theme-background))',
          '--v-layout-left': '0px',
          '--v-layout-top': '0px'
        }">
          <v-container
            fluid
            class="page-wrapper"
            :class="{ 'chat-mode-container': showChatPage, 'tp-app-container': !showChatPage }"
            :style="{
              height: '100%',
              padding: (isChatPage || showChatPage) ? '0' : undefined,
              maxWidth: showChatPage ? 'none' : undefined
            }">
            <div :style="{ height: '100%', width: '100%', overflow: showChatPage ? 'hidden' : undefined }">
              <div v-if="showChatPage" style="height: 100%; width: 100%; overflow: hidden;">
                <Chat />
              </div>
              <RouterView v-else />
            </div>
          </v-container>
        </v-main>

        <!-- 3. Right Sidebar (Tools & Settings) -->
        <RightSidebar />
      </div>

      <MigrationDialog ref="migrationDialog" />
      <ReadmeDialog
        :show="showFirstNoticeDialog"
        mode="first-notice"
        @update:show="onFirstNoticeDialogUpdate"
      />
    </v-app>
  </v-locale-provider>
</template>

<style scoped>
.tp-main-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.tp-content-area {
  flex: 1;
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.chat-mode-container {
  min-height: unset !important;
  height: 100% !important;
  overflow: hidden !important;
  max-width: none !important;
}

.tp-app-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px 32px !important;
  flex: 1;
}

@media (max-width: 768px) {
  .tp-app-container {
    padding: 16px !important;
  }
}
</style>
