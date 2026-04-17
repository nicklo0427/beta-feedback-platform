import { useState } from '#imports'
import { watch } from 'vue'

export type ThemeMode = 'light' | 'dark'

const THEME_STORAGE_KEY = 'beta-feedback-platform.theme-mode'

function applyThemeToDocument(themeMode: ThemeMode): void {
  if (!import.meta.client) {
    return
  }

  document.documentElement.dataset.theme = themeMode
  document.documentElement.style.colorScheme = themeMode
}

export function useThemeMode() {
  return useState<ThemeMode>('theme-mode', () => 'light')
}

export function useThemePersistence(): void {
  const themeMode = useThemeMode()
  const hydrated = useState<boolean>('theme-mode-hydrated', () => false)
  const watchRegistered = useState<boolean>('theme-mode-watch-registered', () => false)

  if (import.meta.client && !hydrated.value) {
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY)
    if (storedTheme === 'light' || storedTheme === 'dark') {
      themeMode.value = storedTheme
    } else {
      themeMode.value = 'light'
    }

    applyThemeToDocument(themeMode.value)
    hydrated.value = true
  }

  if (import.meta.client && !watchRegistered.value) {
    watch(
      themeMode,
      (nextTheme) => {
        window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme)
        applyThemeToDocument(nextTheme)
      },
      {
        immediate: true,
        flush: 'post'
      }
    )
    watchRegistered.value = true
  }
}
