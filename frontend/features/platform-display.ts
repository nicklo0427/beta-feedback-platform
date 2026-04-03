export type PlatformDisplayValue = 'web' | 'h5' | 'pwa' | 'ios' | 'android'

const PLATFORM_LABELS: Record<PlatformDisplayValue, string> = {
  web: 'Web',
  h5: 'Mobile Web',
  pwa: 'PWA',
  ios: 'iOS',
  android: 'Android'
}

export function formatPlatformLabel(platform: string): string {
  if (platform in PLATFORM_LABELS) {
    return PLATFORM_LABELS[platform as PlatformDisplayValue]
  }

  return platform
}
