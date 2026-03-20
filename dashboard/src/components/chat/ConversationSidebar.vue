<template>
    <div class="sidebar-wrapper" :class="{ 'is-mobile': isMobile }">
        <div class="sidebar-panel" 
            :class="{ 
                'sidebar-collapsed': sidebarCollapsed && !isMobile,
                'mobile-sidebar-open': isMobile && mobileMenuOpen,
                'mobile-sidebar': isMobile
            }">

            <!-- Header: Logo + Collapse -->
            <div class="sidebar-header-row" v-if="!isMobile">
                <div class="logo-container" @click="handleLogoClick" style="cursor: pointer">
                    <img class="logo-box" :src="brandLogo" alt="TwoPixel Logo" />
                    <span class="logo-text">TWOPIXEL</span>
                </div>
                <v-btn icon size="small" variant="text" color="grey-darken-1" @click="toggleSidebar">
                    <v-icon>mdi-page-layout-sidebar-left</v-icon>
                </v-btn>
            </div>

        <!-- New Chat Button Row -->
        <div class="new-chat-section" v-if="!isMobile">
            <v-btn block class="tp-new-chat-btn" @click="$emit('newChat')" :disabled="!currSessionId && !selectedProjectId">
                <v-icon start icon="mdi-plus" size="small"></v-icon>
                {{ tm('actions.newChat') }}
            </v-btn>
            <v-btn icon class="tp-refresh-btn" variant="outlined" size="small">
                <v-icon>mdi-refresh</v-icon>
            </v-btn>
        </div>

        <!-- Search Box -->
        <div class="sidebar-search-container" v-if="!isMobile">
            <div class="tp-search-box">
                <v-icon size="16" color="grey-lighten-1" class="ml-3">mdi-magnify</v-icon>
                <input type="text" placeholder="SEARCH HISTORY..." class="tp-search-input" />
            </div>
        </div>

        <!-- Batch action bar -->
        <div v-if="batchMode && (!sidebarCollapsed || isMobile)" class="batch-action-bar">
            <v-btn size="x-small" variant="text" @click="toggleSelectAll">
                {{ isAllSelected ? tm('batch.deselectAll') : tm('batch.selectAll') }}
            </v-btn>
            <span class="batch-selected-count">{{ tm('batch.selected', { count: batchSelected.length }) }}</span>
            <v-spacer />
            <v-btn size="x-small" variant="text" color="error" :disabled="batchSelected.length === 0"
                @click="handleBatchDelete">
                {{ tm('batch.delete') }}
            </v-btn>
        </div>

        <!-- 项目列表组件 -->
        <ProjectList
            v-if="!sidebarCollapsed || isMobile"
            :projects="projects"
            @selectProject="$emit('selectProject', $event)"
            @createProject="$emit('createProject')"
            @editProject="$emit('editProject', $event)"
            @deleteProject="$emit('deleteProject', $event)"
        />

        <div style="overflow-y: auto; flex-grow: 1; overscroll-behavior-y: contain;"
            v-if="!sidebarCollapsed || isMobile">
            <div class="list-section-header">今天 / {{ sessions.length }}</div>
            <div v-if="sessions.length > 0">
                <v-list density="compact" nav class="conversation-list"
                    style="background-color: transparent;" :selected="batchMode ? [] : selectedSessions"
                    @update:selected="handleListSelect">
                    <v-list-item v-for="item in sessions" :key="item.session_id" :value="item.session_id"
                        rounded="lg" class="conversation-item-twopixel"
                        :class="{ 'item-active': currSessionId === item.session_id }"
                        @click="batchMode ? toggleBatchItem(item.session_id) : undefined"
                        :ripple="false"
                    >

                        <template v-slot:prepend>
                            <div class="batch-checkbox-slot" :class="{ 'batch-checkbox-slot--active': batchMode }">
                                <v-checkbox-btn
                                    :model-value="batchSelected.includes(item.session_id)"
                                    @update:model-value="toggleBatchItem(item.session_id)"
                                    @click.stop
                                    density="compact"
                                    hide-details
                                    class="batch-checkbox"
                                />
                            </div>
                            <v-icon v-if="!batchMode" size="small" class="mr-2 icon-message">mdi-message-outline</v-icon>
                        </template>

                        <div class="conversation-content">
                            <div class="conversation-title-row">
                                <span class="conversation-title-text">{{ item.display_name || tm('conversation.newConversation') }}</span>
                                <span class="token-badge">0 tk</span>
                            </div>
                            <div class="conversation-preview">
                                <span class="time-text">21:41</span>
                                {{ item.display_name || 'No message' }}
                            </div>
                        </div>

                        <template v-if="!batchMode && (!sidebarCollapsed || isMobile)" v-slot:append>
                            <div class="conversation-actions">
                                <v-btn icon="mdi-pencil" size="x-small" variant="text"
                                    class="edit-title-btn"
                                    @click.stop="$emit('editTitle', item.session_id, item.display_name ?? '')" />
                                <v-btn icon="mdi-delete" size="x-small" variant="text"
                                    class="delete-conversation-btn" color="error"
                                    @click.stop="handleDeleteConversation(item)" />
                            </div>
                        </template>
                    </v-list-item>
                </v-list>
            </div>

            <v-fade-transition>
                <div class="no-conversations" v-if="sessions.length === 0">
                    <v-icon icon="mdi-message-text-outline" size="large" color="grey-lighten-1"></v-icon>
                    <div class="no-conversations-text" v-if="!sidebarCollapsed || isMobile">
                        {{ tm('conversation.noHistory') }}
                    </div>
                </div>
            </v-fade-transition>
        </div>

        <!-- 收起时的占位元素 -->
        <div class="sidebar-spacer" v-if="sidebarCollapsed && !isMobile"></div>

        <div class="sidebar-user-footer" v-if="!isMobile">
            <button class="sidebar-user-card" type="button" @click="openUserProfileDialog">
                <v-avatar size="30" color="primary" class="sidebar-user-avatar">
                    <v-img v-if="userAvatarUrl" :src="userAvatarUrl" cover />
                    <span v-else class="sidebar-user-avatar-text">{{ userAvatarFallback }}</span>
                </v-avatar>
                <div class="sidebar-user-meta">
                    <div class="sidebar-user-name">{{ userDisplayName }}</div>
                    <div class="sidebar-user-subtitle">{{ userLoginName }}</div>
                </div>
                <v-icon size="18" class="sidebar-user-edit-icon">mdi-pencil-outline</v-icon>
            </button>
        </div>

        <!-- 底部设置按钮 -->
        <div class="sidebar-footer">
            <StyledMenu location="top" :close-on-content-click="false">
                <template v-slot:activator="{ props: menuProps }">
                    <v-btn 
                        v-bind="menuProps"
                        :icon="sidebarCollapsed && !isMobile"
                        :block="!sidebarCollapsed || isMobile"
                        variant="text" 
                        class="settings-btn"
                        :class="{ 'settings-btn-collapsed': sidebarCollapsed && !isMobile }"
                        :prepend-icon="(!sidebarCollapsed || isMobile) ? 'mdi-cog-outline' : undefined"
                    >
                        <v-icon v-if="sidebarCollapsed && !isMobile">mdi-cog-outline</v-icon>
                        <template v-if="!sidebarCollapsed || isMobile">{{ t('core.common.settings') }}</template>
                    </v-btn>
                </template>
                
                <!-- 语言切换（分组） -->
                <v-menu
                    :open-on-hover="!isMobile"
                    :open-on-click="isMobile"
                    :open-delay="!isMobile ? 60 : 0"
                    :close-delay="!isMobile ? 120 : 0"
                    :location="isMobile ? 'bottom' : 'end center'"
                    offset="8"
                    close-on-content-click
                >
                    <template v-slot:activator="{ props: languageMenuProps }">
                        <v-list-item
                            v-bind="languageMenuProps"
                            class="styled-menu-item chat-settings-group-trigger"
                            rounded="md"
                        >
                            <template v-slot:prepend>
                                <v-icon>mdi-translate</v-icon>
                            </template>
                            <v-list-item-title>{{ t('core.common.language') }}</v-list-item-title>
                            <template v-slot:append>
                                <span class="chat-settings-group-current">{{ currentLanguage?.flag }}</span>
                                <v-icon size="18" class="chat-settings-group-arrow">mdi-chevron-right</v-icon>
                            </template>
                        </v-list-item>
                    </template>

                    <v-card class="styled-menu-card" style="min-width: 180px;" elevation="8" rounded="lg">
                        <v-list density="compact" class="styled-menu-list pa-1">
                            <v-list-item
                                v-for="lang in languages"
                                :key="lang.code"
                                :value="lang.code"
                                @click="changeLanguage(lang.code)"
                                :class="{ 'styled-menu-item-active': currentLocale === lang.code }"
                                class="styled-menu-item"
                                rounded="md"
                            >
                                <template v-slot:prepend>
                                    <span class="language-flag">{{ lang.flag }}</span>
                                </template>
                                <v-list-item-title>{{ lang.name }}</v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-card>
                </v-menu>
                
                <!-- 主题切换 -->
                <v-list-item class="styled-menu-item" @click="$emit('toggleTheme')">
                    <template v-slot:prepend>
                        <v-icon>{{ isDark ? 'mdi-weather-night' : 'mdi-white-balance-sunny' }}</v-icon>
                    </template>
                    <v-list-item-title>{{ isDark ? tm('modes.lightMode') : tm('modes.darkMode') }}</v-list-item-title>
                </v-list-item>

                <!-- 通信传输模式（分组） -->
                <v-menu
                    :open-on-hover="!isMobile"
                    :open-on-click="isMobile"
                    :open-delay="!isMobile ? 60 : 0"
                    :close-delay="!isMobile ? 120 : 0"
                    :location="isMobile ? 'bottom' : 'end center'"
                    offset="8"
                    close-on-content-click
                >
                    <template v-slot:activator="{ props: transportMenuProps }">
                        <v-list-item
                            v-bind="transportMenuProps"
                            class="styled-menu-item chat-settings-group-trigger"
                            rounded="md"
                        >
                            <template v-slot:prepend>
                                <v-icon>mdi-lan-connect</v-icon>
                            </template>
                            <v-list-item-title>{{ tm('transport.title') }}</v-list-item-title>
                            <template v-slot:append>
                                <span class="chat-settings-group-current chat-settings-transport-current">{{ currentTransportLabel }}</span>
                                <v-icon size="18" class="chat-settings-group-arrow">mdi-chevron-right</v-icon>
                            </template>
                        </v-list-item>
                    </template>

                    <v-card class="styled-menu-card" style="min-width: 220px;" elevation="8" rounded="lg">
                        <v-list density="compact" class="styled-menu-list pa-1">
                            <v-list-item
                                v-for="opt in transportOptions"
                                :key="opt.value"
                                :value="opt.value"
                                @click="handleTransportModeChange(opt.value)"
                                :class="{ 'styled-menu-item-active': transportMode === opt.value }"
                                class="styled-menu-item"
                                rounded="md"
                            >
                                <v-list-item-title>{{ opt.label }}</v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-card>
                </v-menu>

                <!-- 发送快捷键（分组） -->
                <v-menu
                    :open-on-hover="!isMobile"
                    :open-on-click="isMobile"
                    :open-delay="!isMobile ? 60 : 0"
                    :close-delay="!isMobile ? 120 : 0"
                    :location="isMobile ? 'bottom' : 'end center'"
                    offset="8"
                    close-on-content-click
                >
                    <template v-slot:activator="{ props: sendShortcutMenuProps }">
                        <v-list-item
                            v-bind="sendShortcutMenuProps"
                            class="styled-menu-item chat-settings-group-trigger"
                            rounded="md"
                        >
                            <template v-slot:prepend>
                                <v-icon>mdi-keyboard-outline</v-icon>
                            </template>
                            <v-list-item-title>{{ tm('shortcuts.sendKey.title') }}</v-list-item-title>
                            <template v-slot:append>
                                <span class="chat-settings-group-current chat-settings-transport-current">{{ currentSendShortcutLabel }}</span>
                                <v-icon size="18" class="chat-settings-group-arrow">mdi-chevron-right</v-icon>
                            </template>
                        </v-list-item>
                    </template>

                    <v-card class="styled-menu-card" style="min-width: 220px;" elevation="8" rounded="lg">
                        <v-list density="compact" class="styled-menu-list pa-1">
                            <v-list-item
                                v-for="opt in sendShortcutOptions"
                                :key="opt.value"
                                :value="opt.value"
                                @click="handleSendShortcutChange(opt.value)"
                                :class="{ 'styled-menu-item-active': props.sendShortcut === opt.value }"
                                class="styled-menu-item"
                                rounded="md"
                            >
                                <v-list-item-title>{{ opt.label }}</v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-card>
                </v-menu>

                <!-- 全屏/退出全屏 -->
                <v-list-item class="styled-menu-item" @click="$emit('toggleFullscreen')">
                    <template v-slot:prepend>
                        <v-icon>{{ chatboxMode ? 'mdi-fullscreen-exit' : 'mdi-fullscreen' }}</v-icon>
                    </template>
                    <v-list-item-title>{{ chatboxMode ? tm('actions.exitFullscreen') : tm('actions.fullscreen') }}</v-list-item-title>
                </v-list-item>

                <!-- 提供商配置 -->
                <v-list-item class="styled-menu-item" @click="showProviderConfigDialog = true">
                    <template v-slot:prepend>
                        <v-icon>mdi-creation</v-icon>
                    </template>
                    <v-list-item-title>{{ tm('actions.providerConfig') }}</v-list-item-title>
                </v-list-item>
            </StyledMenu>
        </div>
        </div>

        <!-- 提供商配置对话框 -->
        <ProviderConfigDialog v-model="showProviderConfigDialog" />
        <v-dialog v-model="showUserProfileDialog" max-width="360" transition="dialog-bottom-transition">
            <v-card elevation="0" class="profile-dialog-card overflow-hidden" style="border-radius: 24px;">
                <!-- 顶部背景横幅 -->
                <div class="profile-banner d-flex justify-end pa-3">
                    <v-btn icon="mdi-close" variant="text" color="white" size="small" @click="showUserProfileDialog = false"></v-btn>
                </div>

                <v-card-text class="px-6 pb-6 pt-0 text-center" style="margin-top: -48px;">
                    <!-- 头像区域 -->
                    <div class="d-flex flex-column align-center justify-center mb-4">
                        <div class="position-relative cursor-pointer avatar-upload-wrapper mb-2" @click="triggerAvatarUpload">
                            <v-avatar size="96" color="primary">
                                <v-img v-if="profileFormAvatarUrl" :src="profileFormAvatarUrl" cover />
                                <span v-else class="text-h4 text-white font-weight-medium">{{ userAvatarFallback }}</span>
                            </v-avatar>
                            <div class="avatar-upload-overlay d-flex align-center justify-center">
                                <v-icon color="white" size="28">mdi-camera-outline</v-icon>
                            </div>
                        </div>
                        <div class="text-h6 font-weight-bold" style="color: rgb(var(--v-theme-on-surface)); letter-spacing: 0.5px;">{{ profileFormNickname || userDisplayName }}</div>
                        <div class="text-caption" style="color: rgb(var(--v-theme-on-surface-variant));">点击头像更换</div>
                    </div>
                    
                    <input ref="hiddenFileInput" type="file" accept="image/*" class="d-none" @change="handleHiddenFileChange" />

                    <!-- 表单区域 -->
                    <div class="text-left mt-2 mb-6">
                        <div class="text-subtitle-2 mb-2 ml-1 font-weight-bold" style="color: rgb(var(--v-theme-on-surface-variant));">展示昵称</div>
                        <v-text-field
                            v-model="profileFormNickname"
                            placeholder="输入您的昵称"
                            variant="solo"
                            flat
                            density="comfortable"
                            maxlength="32"
                            hide-details="auto"
                            class="custom-nickname-input"
                        />
                    </div>
                    
                    <!-- 操作按钮 -->
                    <v-btn 
                        block 
                        class="mb-3 font-weight-bold text-none custom-save-btn"
                        elevation="0"
                        :loading="savingUserProfile" 
                        @click="saveUserProfile"
                    >
                        保存修改
                    </v-btn>
                    
                    <v-btn 
                        block 
                        prepend-icon="mdi-logout-variant"
                        class="font-weight-bold text-none custom-logout-btn"
                        elevation="0"
                        @click="handleLogout"
                    >
                        切换账号 (退出登录)
                    </v-btn>
                </v-card-text>
            </v-card>
        </v-dialog>

        <!-- 侧边栏收起时的展开按钮 (悬浮) -->
        <div class="sidebar-expand-btn-container" v-if="sidebarCollapsed && !isMobile">
            <v-btn icon size="small" class="sidebar-expand-btn" @click="toggleSidebar" variant="text" color="grey-darken-1">
                <v-icon>mdi-page-layout-sidebar-right</v-icon>
            </v-btn>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useCustomizerStore } from '@/stores/customizer';
import { useI18n, useModuleI18n } from '@/i18n/composables';
import { useAuthStore } from '@/stores/auth';
import type { Session } from '@/composables/useSessions';
import { askForConfirmation, useConfirmDialog } from '@/utils/confirmDialog';
import StyledMenu from '@/components/shared/StyledMenu.vue';
import ProviderConfigDialog from '@/components/chat/ProviderConfigDialog.vue';
import ProjectList from '@/components/chat/ProjectList.vue';
import type { Project } from '@/components/chat/ProjectList.vue';
import { useLanguageSwitcher } from '@/i18n/composables';
import type { Locale } from '@/i18n/types';
import brandLogo from '@/assets/images/astrbot_logo_mini.webp';

interface Props {
    sessions: Session[];
    selectedSessions: string[];
    currSessionId: string;
    selectedProjectId?: string | null;
    transportMode: 'sse' | 'websocket';
    isDark: boolean;
    chatboxMode: boolean;
    isMobile: boolean;
    mobileMenuOpen: boolean;
    projects?: Project[];
    sendShortcut: 'enter' | 'shift_enter';
}

const props = withDefaults(defineProps<Props>(), {
    projects: () => []
});

const emit = defineEmits<{
    newChat: [];
    selectConversation: [sessionIds: string[]];
    editTitle: [sessionId: string, title: string];
    deleteConversation: [sessionId: string];
    batchDeleteConversations: [sessionIds: string[]];
    closeMobileSidebar: [];
    toggleTheme: [];
    toggleFullscreen: [];
    selectProject: [projectId: string];
    createProject: [];
    editProject: [project: Project];
    deleteProject: [projectId: string];
    updateTransportMode: [mode: 'sse' | 'websocket'];
    updateSendShortcut: [mode: 'enter' | 'shift_enter'];
}>();

const { t } = useI18n();
const { tm } = useModuleI18n('features/chat');
const router = useRouter();
const customizer = useCustomizerStore();

const handleLogoClick = () => {
    // Toggle between Chat and Bot mode
    if (customizer.viewMode === 'chat') {
        customizer.SET_VIEW_MODE('bot');
        router.push('/config#normal');
    } else {
        customizer.SET_VIEW_MODE('chat');
        router.push('/chat');
    }
};

const confirmDialog = useConfirmDialog();

const sidebarCollapsed = ref(true);
const showProviderConfigDialog = ref(false);
const authStore = useAuthStore();
const showUserProfileDialog = ref(false);
const savingUserProfile = ref(false);
const userLoginName = computed(() => String(localStorage.getItem('user') || '').trim() || 'user');
const profileFormNickname = ref('');
const profileFormAvatarUrl = ref('');
const hiddenFileInput = ref<HTMLInputElement | null>(null);

function handleLogout() {
    showUserProfileDialog.value = false;
    authStore.logout();
}

function triggerAvatarUpload() {
    if (hiddenFileInput.value) {
        hiddenFileInput.value.click();
    }
}

function handleHiddenFileChange(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
        onAvatarFileSelected(target.files[0]);
    }
    if (target) {
        target.value = '';
    }
}

const userDisplayName = computed(() => {
    const x = String(profileFormNickname.value || '').trim();
    return x || userLoginName.value;
});
const userAvatarUrl = computed(() => String(profileFormAvatarUrl.value || '').trim());
const userAvatarFallback = computed(() => {
    const text = userDisplayName.value.trim();
    if (!text) return 'U';
    return text.slice(0, 2).toUpperCase();
});

// Batch mode state
const batchMode = ref(false);
const batchSelected = ref<string[]>([]);

const isAllSelected = computed(() =>
    props.sessions.length > 0 && batchSelected.value.length === props.sessions.length
);

function toggleBatchMode() {
    batchMode.value = !batchMode.value;
    batchSelected.value = [];
}

function toggleBatchItem(sessionId: string) {
    const idx = batchSelected.value.indexOf(sessionId);
    if (idx >= 0) {
        batchSelected.value.splice(idx, 1);
    } else {
        batchSelected.value.push(sessionId);
    }
}

function toggleSelectAll() {
    if (isAllSelected.value) {
        batchSelected.value = [];
    } else {
        batchSelected.value = props.sessions.map(s => s.session_id);
    }
}

async function handleBatchDelete() {
    const count = batchSelected.value.length;
    if (count === 0) return;
    const message = tm('batch.confirmDelete', { count });
    if (await askForConfirmation(message, confirmDialog)) {
        emit('batchDeleteConversations', [...batchSelected.value]);
        batchSelected.value = [];
        batchMode.value = false;
    }
}

function handleListSelect(sessionIds: string[]) {
    if (!batchMode.value) {
        emit('selectConversation', sessionIds);
    }
}
const transportOptions = [
    { label: tm('transport.sse'), value: 'sse' as const },
    { label: tm('transport.websocket'), value: 'websocket' as const }
];
const sendShortcutOptions = [
    { label: tm('shortcuts.sendKey.enterToSend'), value: 'enter' as const },
    { label: tm('shortcuts.sendKey.shiftEnterToSend'), value: 'shift_enter' as const }
];

// Language switcher
const { languageOptions, currentLanguage, switchLanguage, locale } = useLanguageSwitcher();
const languages = computed(() =>
    languageOptions.value.map(lang => ({
        code: lang.value,
        name: lang.label,
        flag: lang.flag
    }))
);
const currentLocale = computed(() => locale.value);
const changeLanguage = async (langCode: string) => {
    await switchLanguage(langCode as Locale);
};

const currentTransportLabel = computed(() => {
    const found = transportOptions.find(opt => opt.value === props.transportMode);
    return found?.label ?? '';
});
const currentSendShortcutLabel = computed(() => {
    const found = sendShortcutOptions.find(opt => opt.value === props.sendShortcut);
    return found?.label ?? '';
});

// 从 localStorage 读取侧边栏折叠状态
const savedCollapsedState = localStorage.getItem('sidebarCollapsed');
if (savedCollapsedState !== null) {
    sidebarCollapsed.value = JSON.parse(savedCollapsedState);
} else {
    sidebarCollapsed.value = false;
}

function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value;
    localStorage.setItem('sidebarCollapsed', JSON.stringify(sidebarCollapsed.value));
}

async function handleDeleteConversation(session: Session) {
    const sessionTitle = session.display_name || tm('conversation.newConversation');
    const message = tm('conversation.confirmDelete', { name: sessionTitle });
    if (await askForConfirmation(message, confirmDialog)) {
        emit('deleteConversation', session.session_id);
    }
}

function handleTransportModeChange(mode: string | null) {
    if (mode === 'sse' || mode === 'websocket') {
        emit('updateTransportMode', mode);
    }
}

function handleSendShortcutChange(mode: string | null) {
    if (mode === 'enter' || mode === 'shift_enter') {
        emit('updateSendShortcut', mode);
    }
}

async function loadUserProfile() {
    try {
        const sbToken = localStorage.getItem('supabase-access-token');
        const sbUserRaw = localStorage.getItem('supabase-user');
        const headers: Record<string, string> = {};
        
        if (sbToken && sbUserRaw) {
            try {
                const sbUser = JSON.parse(sbUserRaw);
                if (sbUser && sbUser.id) {
                    headers['X-Supabase-Access-Token'] = sbToken;
                    headers['X-Supabase-User-Id'] = sbUser.id;
                }
            } catch (e) {}
        }
        
        const res = await axios.get('/api/user/profile', { headers });
        if (res?.data?.status === 'ok' && res?.data?.data) {
            const data = res.data.data;
            profileFormNickname.value = String(data.nickname || '').trim();
            profileFormAvatarUrl.value = String(data.avatar_url || '').trim();
            if (!profileFormNickname.value && sbUserRaw) {
                try {
                    const sbUser = JSON.parse(sbUserRaw);
                    const meta = sbUser?.user_metadata || {};
                    const name = String(meta?.full_name || meta?.name || '').trim();
                    const avatar = String(meta?.avatar_url || '').trim();
                    if (name) profileFormNickname.value = name;
                    if (avatar) profileFormAvatarUrl.value = avatar;
                } catch (e) {}
            }
        }
    } catch {
        profileFormNickname.value = '';
        profileFormAvatarUrl.value = '';
    }
}

function openUserProfileDialog() {
    showUserProfileDialog.value = true;
}

async function saveUserProfile() {
    savingUserProfile.value = true;
    try {
        const sbToken = localStorage.getItem('supabase-access-token');
        const sbUserRaw = localStorage.getItem('supabase-user');
        const headers: Record<string, string> = {};
        
        if (sbToken && sbUserRaw) {
            try {
                const sbUser = JSON.parse(sbUserRaw);
                if (sbUser && sbUser.id) {
                    headers['X-Supabase-Access-Token'] = sbToken;
                    headers['X-Supabase-User-Id'] = sbUser.id;
                }
            } catch (e) {}
        }
        
        await axios.post('/api/user/profile', {
            nickname: profileFormNickname.value,
            avatar_url: profileFormAvatarUrl.value,
        }, { headers });
        showUserProfileDialog.value = false;
    } finally {
        savingUserProfile.value = false;
    }
}

function onAvatarFileSelected(value: File[] | File | null) {
    const file = Array.isArray(value) ? value[0] : value;
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
        profileFormAvatarUrl.value = String(reader.result || '');
    };
    reader.readAsDataURL(file);
}

onMounted(() => {
    loadUserProfile();
});
</script>

<style scoped>
.sidebar-wrapper {
    position: relative;
    height: 100%;
    display: flex;
}

.sidebar-wrapper.is-mobile {
    position: static;
    height: auto;
    display: block;
    width: 0;
}

.sidebar-panel {
    max-width: 270px;
    min-width: 240px;
    display: flex;
    flex-direction: column;
    padding: 0;
    height: 100%;
    max-height: 100%;
    position: relative;
    background-color: transparent;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
    border-right: 1px solid rgba(var(--v-theme-border), 0.5);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.sidebar-header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    height: 64px;
}

.logo-container {
    display: flex;
    align-items: center;
    gap: 8px;
}

.logo-box {
    width: 24px;
    height: 24px;
    border-radius: 6px;
    object-fit: cover;
}

.logo-text {
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: rgb(var(--v-theme-primary));
}

.new-chat-section {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 16px;
    margin-bottom: 16px;
}

.tp-new-chat-btn {
    background-color: rgb(var(--v-theme-primary)) !important;
    color: rgb(var(--v-theme-background)) !important;
    height: 40px !important;
    border-radius: 8px !important;
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 0.05em;
    flex: 1;
    text-transform: none !important;
}

.tp-refresh-btn {
    width: 40px !important;
    height: 40px !important;
    border-radius: 8px !important;
    border: 1px solid rgba(var(--v-theme-border), 0.5);
    color: rgb(var(--v-theme-textSecondary));
}

.sidebar-search-container {
    padding: 0 16px;
    margin-bottom: 16px;
}

.tp-search-box {
    display: flex;
    align-items: center;
    height: 36px;
    background-color: rgba(var(--v-theme-surface), 0.5);
    border: 1px solid rgba(var(--v-theme-border), 0.5);
    border-radius: 8px;
    transition: all 0.2s ease;
}

.tp-search-box:focus-within {
    border-color: rgb(var(--v-theme-primary));
    background-color: rgb(var(--v-theme-surface));
}

.tp-search-input {
    flex: 1;
    height: 100%;
    border: none;
    outline: none;
    background: transparent;
    padding: 0 8px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: rgb(var(--v-theme-primary));
}

.tp-search-input::placeholder {
    color: rgb(var(--v-theme-textTertiary));
    opacity: 0.7;
}

.sidebar-collapsed {
    width: 0 !important;
    min-width: 0 !important;
    padding: 0 !important;
    border-right: none;
    opacity: 0;
    overflow: hidden;
    pointer-events: none;
}

.mobile-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    max-width: 280px !important;
    min-width: 280px !important;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 1000;
}

.mobile-sidebar-open {
    transform: translateX(0) !important;
}

.sidebar-expand-btn-container {
    position: absolute;
    top: 16px;
    left: 16px;
    z-index: 10;
}

.sidebar-expand-btn {
    background-color: rgba(var(--v-theme-surface), 0.8) !important;
    border: 1px solid rgba(var(--v-theme-border), 0.5);
    backdrop-filter: blur(4px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.new-chat-btn {
    justify-content: flex-start;
    background-color: transparent !important;
    border-radius: 20px;
    padding: 8px 16px !important;
}

.conversation-list {
    background-color: transparent !important;
    padding: 0 16px !important;
}

.conversation-item-twopixel {
    border-radius: 8px !important;
    border: none !important;
    margin-bottom: 4px !important;
    padding: 10px 12px !important;
    transition: all 0.2s ease;
    min-height: auto;
    background-color: transparent !important;
}

.conversation-item-twopixel :deep(.v-list-item__overlay),
.conversation-item-twopixel :deep(.v-list-item__underlay) {
    display: none !important;
}

.conversation-item-twopixel:hover {
    background-color: rgba(var(--v-theme-on-surface), 0.04) !important;
}

.item-active {
    background-color: rgba(var(--v-theme-on-surface), 0.06) !important;
    box-shadow: none !important;
}

.conversation-content {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.conversation-title-row {
    display: flex;
    align-items: center;
    gap: 8px;
}

.conversation-title-text {
    flex: 1;
    min-width: 0;
    font-size: 14px;
    font-weight: 500;
    color: rgb(var(--v-theme-primaryText)) !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.token-badge {
    font-size: 11px;
    padding: 0px 4px;
    background-color: transparent;
    border: 1px solid rgba(var(--v-theme-primaryText), 0.16);
    border-radius: 4px;
    color: rgb(var(--v-theme-secondaryText)) !important;
    font-family: monospace;
    flex-shrink: 0;
}

.time-text {
    font-size: 12px;
    color: rgb(var(--v-theme-secondaryText)) !important;
    font-family: monospace;
    margin-right: 4px;
}

.conversation-preview {
    font-size: 13px;
    color: rgb(var(--v-theme-secondaryText)) !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.conversation-actions {
    display: flex;
    gap: 2px;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease;
}

.conversation-item-twopixel:hover .conversation-actions {
    opacity: 1;
    visibility: visible;
}

.edit-title-btn,
.delete-conversation-btn {
    opacity: 0.5;
    transition: opacity 0.2s ease;
}

.edit-title-btn:hover,
.delete-conversation-btn:hover {
    opacity: 1;
}

.icon-message {
    color: rgb(var(--v-theme-secondaryText)) !important;
    margin-top: 2px;
}

.item-active .icon-message {
    color: rgb(var(--v-theme-primaryText)) !important;
}

.sidebar-search-container {
    padding: 16px;
    padding-bottom: 12px;
}

.sidebar-footer {
    display: none;
    margin-top: auto;
    padding: 8px 12px 16px;
    flex-direction: column;
    gap: 8px;
}

.sidebar-user-footer {
    margin-top: auto;
    padding: 8px 12px 16px;
}

.sidebar-user-card {
    width: 100%;
    border: 1px solid rgba(var(--v-theme-border), 0.5);
    border-radius: 10px;
    background: rgba(var(--v-theme-surface), 0.6);
    padding: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
}

.sidebar-user-card:hover {
    border-color: rgba(var(--v-theme-primary), 0.4);
}

.sidebar-user-meta {
    min-width: 0;
    flex: 1;
    text-align: left;
}

.sidebar-user-name {
    font-size: 12px;
    font-weight: 700;
    color: rgb(var(--v-theme-primary));
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.sidebar-user-subtitle {
    font-size: 11px;
    color: rgb(var(--v-theme-textSecondary));
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.sidebar-user-avatar-text {
    font-size: 12px;
    font-weight: 700;
}

.sidebar-user-avatar-text-lg {
    font-size: 18px;
}

.sidebar-user-edit-icon {
    opacity: 0.7;
}

.search-input :deep(.v-field__outline__start),
.search-input :deep(.v-field__outline__end) {
    border-color: rgba(var(--v-theme-border), 0.5);
}

.search-input :deep(input) {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}

.new-chat-btn-twopixel {
    background-color: rgb(var(--v-theme-primary)) !important;
    color: rgb(var(--v-theme-surface)) !important;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.05em;
    height: 40px !important;
    text-transform: none;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    flex: 1;
}

.refresh-btn {
    color: rgb(var(--v-theme-textSecondary));
    border: 1px solid rgba(var(--v-theme-border), 0.5);
    border-radius: 8px;
    width: 40px;
    height: 40px;
    margin-left: 8px;
}

.list-section-header {
    padding: 8px 24px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgb(var(--v-theme-textTertiary));
    display: flex;
    align-items: center;
    gap: 8px;
}

.list-section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background-color: rgba(var(--v-theme-border), 0.3);
}

.chat-settings-group-trigger :deep(.v-list-item__append) {
    display: flex;
    align-items: center;
    gap: 6px;
}

.chat-settings-group-current {
    font-size: 14px;
    line-height: 1;
    opacity: 0.8;
}

.chat-settings-transport-current {
    font-size: 12px;
}

.chat-settings-group-arrow {
    opacity: 0.7;
}

.language-flag {
    font-size: 16px;
    margin-right: 8px;
}

.new-chat-row {
    display: flex;
    align-items: center;
    gap: 4px;
}

.new-chat-row .new-chat-btn {
    flex: 1;
    min-width: 0;
}

.batch-action-bar {
    display: flex;
    align-items: center;
    padding: 4px 12px;
    gap: 4px;
    flex-shrink: 0;
}

.batch-selected-count {
    font-size: 12px;
    opacity: 0.7;
    white-space: nowrap;
}

.batch-checkbox {
    flex: none;
    transition: opacity 0.2s ease, transform 0.2s ease;
}

.batch-checkbox-slot {
    width: 0;
    opacity: 0;
    overflow: hidden;
    pointer-events: none;
    transform: translateX(-8px);
    transition: width 0.2s ease, opacity 0.2s ease, transform 0.2s ease;
}

.batch-checkbox-slot--active {
    width: 28px;
    opacity: 1;
    pointer-events: auto;
    transform: translateX(0);
}

.profile-dialog-card {
    background-color: rgb(var(--v-theme-surface));
    border-radius: 24px !important;
}

.profile-banner {
    height: 100px;
    background: linear-gradient(180deg, #333333 0%, #1a1a1a 100%);
    position: relative;
}

.avatar-upload-wrapper {
    border-radius: 50%;
    overflow: hidden;
    border: 4px solid rgb(var(--v-theme-surface));
    background-color: rgb(var(--v-theme-surface));
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}

.avatar-upload-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.4);
    opacity: 0;
    transition: opacity 0.2s ease;
    border-radius: 50%;
}

.avatar-upload-wrapper:hover .avatar-upload-overlay {
    opacity: 1;
}

.custom-nickname-input :deep(.v-field) {
    background-color: #424242 !important;
    border-radius: 16px !important;
    color: #ffffff;
}

.custom-nickname-input :deep(input) {
    color: #ffffff;
}

.custom-nickname-input :deep(.v-field__overlay) {
    display: none;
}

.custom-save-btn {
    background-color: rgb(var(--v-theme-on-surface)) !important;
    color: rgb(var(--v-theme-surface)) !important;
    border-radius: 16px !important;
    height: 48px !important;
    font-size: 15px !important;
    letter-spacing: 0.5px !important;
}

.custom-logout-btn {
    background-color: rgba(var(--v-theme-error), 0.1) !important;
    color: rgb(var(--v-theme-error)) !important;
    border-radius: 16px !important;
    height: 48px !important;
    font-size: 15px !important;
    letter-spacing: 0.5px !important;
}
</style>
