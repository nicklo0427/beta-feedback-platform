// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: ['~/assets/scss/main.scss'],
  modules: ['@pinia/nuxt'],
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1',
      authMode:
        process.env.NUXT_PUBLIC_AUTH_MODE ??
        process.env.BFP_AUTH_MODE ??
        'session_with_header_fallback'
    }
  },
  typescript: {
    strict: true
  }
})
