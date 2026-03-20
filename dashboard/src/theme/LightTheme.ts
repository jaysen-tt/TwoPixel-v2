import type { ThemeTypes } from '@/types/themeTypes/ThemeType';

const PurpleTheme: ThemeTypes = {
  name: 'PurpleTheme',
  dark: false,
  variables: {
    'border-color': '#1A1A1A',
    'carousel-control-size': 10
  },
  colors: {
    primary: '#1A1A1A',
    secondary: '#333333',
    info: '#03c9d7',
    success: '#00c853',
    accent: '#FFAB91',
    warning: '#ffc107',
    error: '#f44336',
    lightprimary: '#E0E0E0',
    lightsecondary: '#F5F5F5',
    lightsuccess: '#b9f6ca',
    lighterror: '#f9d8d8',
    lightwarning: '#fff8e1',
    primaryText: '#1A1A1A',
    secondaryText: '#666666',
    darkprimary: '#000000',
    darksecondary: '#1A1A1A',
    borderLight: '#d0d0d0',
    border: '#d0d0d0',
    inputBorder: '#787878',
    containerBg: '#F9F7F5',
    surface: '#FFFFFF',
    'on-surface-variant': '#FFFFFF',
    facebook: '#4267b2',
    twitter: '#1da1f2',
    linkedin: '#0e76a8',
    gray100: '#fafafacc',
    primary200: '#90caf9',
    secondary200: '#8cc4e1',
    background: '#F9F7F5',
    overlay: '#ffffffaa',
    codeBg: '#ececec',
    preBg: 'rgb(249, 249, 249)',
    code: 'rgb(13, 13, 13)',
    chatMessageBubble: '#FFFFFF',
    mcpCardBg: '#FFFFFF',
  }
};

export { PurpleTheme };
