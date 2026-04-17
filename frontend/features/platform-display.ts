import type { AppLocale } from '~/features/i18n/use-app-i18n'

export type PlatformDisplayValue = 'web' | 'h5' | 'pwa' | 'ios' | 'android'

const PLATFORM_LABELS: Record<AppLocale, Record<PlatformDisplayValue, string>> = {
  'zh-TW': {
    web: '網頁',
    h5: '行動網頁',
    pwa: 'PWA',
    ios: 'iOS',
    android: 'Android'
  },
  en: {
    web: 'Web',
    h5: 'Mobile Web',
    pwa: 'PWA',
    ios: 'iOS',
    android: 'Android'
  }
}

export function formatPlatformLabel(
  platform: string,
  locale: AppLocale = 'zh-TW'
): string {
  const labels = PLATFORM_LABELS[locale]

  if (platform in labels) {
    return labels[platform as PlatformDisplayValue]
  }

  return platform
}
