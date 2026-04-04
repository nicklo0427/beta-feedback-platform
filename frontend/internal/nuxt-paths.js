import { joinRelativeURL } from 'ufo'

const APP_BASE_URL = '/'
const BUILD_ASSETS_DIR = '/_nuxt/'

export function baseURL() {
  return APP_BASE_URL
}

export function buildAssetsDir() {
  return BUILD_ASSETS_DIR
}

export function publicAssetsURL(...path) {
  return path.length
    ? joinRelativeURL(APP_BASE_URL, ...path)
    : APP_BASE_URL
}

export function buildAssetsURL(...path) {
  return joinRelativeURL(publicAssetsURL(), buildAssetsDir(), ...path)
}
