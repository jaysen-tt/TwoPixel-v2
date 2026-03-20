import type { ThemeTypes } from '@/types/themeTypes/ThemeType';

const PurpleThemeDark: ThemeTypes = {
  name: 'PurpleThemeDark',
  dark: true,
  variables: {
    'border-color': '#FFFFFF',
    'carousel-control-size': 10
  },
  colors: {
    primary: '#FFFFFF',
    secondary: '#CCCCCC',
    info: '#03c9d7',
    success: '#52c41a',
    accent: '#FFAB91',
    warning: '#faad14',
    error: '#ff4d4f',
    lightprimary: '#333333',
    lightsecondary: '#444444',
    lightsuccess: '#b9f6ca',
    lighterror: '#f9d8d8',
    lightwarning: '#fff8e1',
    primaryText: '#FFFFFF',
    secondaryText: '#AAAAAA',
    darkprimary: '#E0E0E0',
    darksecondary: '#BBBBBB',
    borderLight: '#444444',
    border: '#333333ee',
    inputBorder: '#787878',
    containerBg: '#1A1A1A',
    surface: '#262626',
    'on-surface-variant': '#000',
    facebook: '#4267b2',
    twitter: '#1da1f2',
    linkedin: '#0e76a8',
    gray100: '#cccccccc',
    primary200: '#84c9ea',
    secondary200: '#8cc4e1',
    background: '#1A1A1A',
    overlay: '#111111aa',
    codeBg: '#282833',
    preBg: 'rgb(23, 23, 23)',
    code: '#ffffffdd',
    chatMessageBubble: '#262626',
    mcpCardBg: '#262626',
  }
};

export { PurpleThemeDark };
