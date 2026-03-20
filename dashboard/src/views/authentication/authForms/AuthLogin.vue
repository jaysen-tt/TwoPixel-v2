<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { Form } from 'vee-validate';
import { useModuleI18n } from '@/i18n/composables';

const { tm: t } = useModuleI18n('features/auth');

const valid = ref(false);
const show1 = ref(false);
const show2 = ref(false);
const password = ref('');
const confirmPassword = ref('');
const username = ref('');
const loading = ref(false);
const mode = ref<'login' | 'signup'>('login');
const forgotSending = ref(false);
const authMessage = ref('');
const authMessageType = ref<'success' | 'error'>('error');

/* eslint-disable @typescript-eslint/no-explicit-any */
async function validate(values: any, { setErrors }: any) {
  loading.value = true;
  authMessage.value = '';

  const normalizedUsername = String(username.value || '').trim();
  const isEmailLogin = normalizedUsername.includes('@');
  if (mode.value === 'login' && !isEmailLogin) {
    setErrors({ apiError: t('loginEmailRequired') });
    loading.value = false;
    return;
  }
  if (mode.value === 'signup' && !isEmailLogin) {
    setErrors({ apiError: t('signupEmailRequired') });
    loading.value = false;
    return;
  }
  if (mode.value === 'signup' && String(password.value || '') !== String(confirmPassword.value || '')) {
    setErrors({ apiError: t('signupPasswordMismatch') });
    loading.value = false;
    return;
  }

  const authStore = useAuthStore();
  // @ts-ignore
  authStore.returnUrl = new URLSearchParams(window.location.search).get('redirect');
  const runner = mode.value === 'signup'
    ? authStore.signup(normalizedUsername, password.value)
    : authStore.login(normalizedUsername, password.value);
  return runner.then((res) => {
    console.log(res);
    loading.value = false;
  }).catch((err) => {
    setErrors({ apiError: err });
    loading.value = false;
  });
}

async function onForgotPassword() {
  const normalizedUsername = String(username.value || '').trim();
  const isEmail = normalizedUsername.includes('@');
  if (!isEmail) {
    authMessageType.value = 'error';
    authMessage.value = t('forgotPasswordEmailRequired');
    return;
  }
  forgotSending.value = true;
  const authStore = useAuthStore();
  authStore.forgotPassword(normalizedUsername).then((message) => {
    authMessageType.value = 'success';
    authMessage.value = String(message || '');
    forgotSending.value = false;
  }).catch((err) => {
    authMessageType.value = 'error';
    authMessage.value = String(err);
    forgotSending.value = false;
  });
}

</script>

<template>
  <Form @submit="validate" class="mt-4 login-form" v-slot="{ errors, isSubmitting }">
    <div class="mode-switch mb-6">
      <v-btn 
        class="text-body-2 font-weight-medium"
        :variant="mode === 'login' ? 'flat' : 'text'" 
        :color="mode === 'login' ? 'surface' : 'transparent'"
        :style="{ color: mode === 'login' ? 'rgb(var(--v-theme-on-surface))' : 'rgb(var(--v-theme-on-surface-variant))', borderRadius: '8px' }"
        elevation="0"
        @click="mode = 'login'"
      >
        {{ t('login') }}
      </v-btn>
      <v-btn 
        class="text-body-2 font-weight-medium"
        :variant="mode === 'signup' ? 'flat' : 'text'" 
        :color="mode === 'signup' ? 'surface' : 'transparent'"
        :style="{ color: mode === 'signup' ? 'rgb(var(--v-theme-on-surface))' : 'rgb(var(--v-theme-on-surface-variant))', borderRadius: '8px' }"
        elevation="0"
        @click="mode = 'signup'"
      >
        {{ t('signup') }}
      </v-btn>
    </div>

    <v-text-field v-model="username" :label="t('username')" class="mb-4 input-field" required hide-details="auto"
      variant="outlined" rounded="lg" prepend-inner-icon="mdi-account" :disabled="loading" color="primary"></v-text-field>

    <v-text-field v-model="password" :label="t('password')" required variant="outlined" rounded="lg" hide-details="auto"
      :append-inner-icon="show1 ? 'mdi-eye-off' : 'mdi-eye'" :type="show1 ? 'text' : 'password'"
      @click:append-inner="show1 = !show1" class="pwd-input" prepend-inner-icon="mdi-lock" :disabled="loading" color="primary"></v-text-field>

    <div v-if="mode === 'login'" class="mt-2 d-flex justify-end">
      <v-btn
        variant="text"
        size="small"
        color="primary"
        :loading="forgotSending"
        :disabled="loading || forgotSending"
        @click="onForgotPassword"
      >
        {{ t('forgotPassword') }}
      </v-btn>
    </div>

    <v-text-field v-if="mode === 'signup'" v-model="confirmPassword" :label="t('confirmPassword')" required variant="outlined" rounded="lg" hide-details="auto"
      :append-inner-icon="show2 ? 'mdi-eye-off' : 'mdi-eye'" :type="show2 ? 'text' : 'password'"
      @click:append-inner="show2 = !show2" class="pwd-input mt-4" prepend-inner-icon="mdi-lock-check" :disabled="loading" color="primary"></v-text-field>

    <div class="mt-2 mb-6">
      <small style="color: rgb(var(--v-theme-on-surface-variant)); font-size: 12px; font-weight: 500;">{{ mode === 'signup' ? t('signupHint') : t('defaultHint') }}</small>
    </div>

    <v-btn :loading="isSubmitting || loading" block class="submit-btn" size="x-large"
      :disabled="valid" type="submit" elevation="0">
      <span class="submit-btn-text">{{ mode === 'signup' ? t('signup') : t('login') }}</span>
    </v-btn>

    <div v-if="authMessage" class="mt-4 error-container">
      <v-alert :color="authMessageType" variant="tonal" icon="mdi-alert-circle" border="start">
        {{ authMessage }}
      </v-alert>
    </div>

    <div v-if="errors.apiError" class="mt-4 error-container">
      <v-alert color="error" variant="tonal" icon="mdi-alert-circle" border="start">
        {{ errors.apiError }}
      </v-alert>
    </div>
  </Form>
</template>

<style lang="scss">
.login-form {
  .mode-switch {
    display: flex;
    gap: 8px;
    background-color: rgba(var(--v-theme-on-surface), 0.04);
    padding: 4px;
    border-radius: 12px;
    width: fit-content;
  }
  
  .v-text-field .v-field--active input {
    font-weight: 500;
  }

  .input-field,
  .pwd-input {
    .v-field__field {
      padding-top: 5px;
      padding-bottom: 5px;
    }

    .v-field__outline {
      opacity: 0.5;
    }

    &:hover .v-field__outline {
      opacity: 0.8;
    }

    .v-field--focused .v-field__outline {
      opacity: 1;
    }

    .v-field__prepend-inner {
      padding-right: 8px;
      opacity: 0.7;
    }
    
    .v-field__append-inner {
      opacity: 0.6;
      cursor: pointer;
      &:hover {
        opacity: 1;
      }
    }
  }

  .submit-btn {
    height: 52px;
    transition: all 0.3s ease;
    border-radius: 12px !important;
    background-color: rgb(var(--v-theme-on-surface)) !important;
    color: rgb(var(--v-theme-surface)) !important;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(var(--v-theme-on-surface), 0.15) !important;
    }

    .submit-btn-text {
      font-size: 1.05rem;
      font-weight: 500;
      letter-spacing: normal;
    }
  }

  .error-container {
    .v-alert {
      border-left-width: 4px !important;
    }
  }
}

.custom-divider {
  border-color: rgba(0, 0, 0, 0.08) !important;
}
</style>
