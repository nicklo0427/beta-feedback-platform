export type DeviceProfilePlatform = 'web' | 'h5' | 'pwa' | 'ios' | 'android'

export const DEVICE_PROFILE_PLATFORM_OPTIONS: DeviceProfilePlatform[] = [
  'web',
  'h5',
  'pwa',
  'ios',
  'android'
]

export interface DeviceProfileListItem {
  id: string
  name: string
  platform: DeviceProfilePlatform
  device_model: string
  os_name: string
  updated_at: string
}

export interface DeviceProfileDetail {
  id: string
  name: string
  platform: DeviceProfilePlatform
  device_model: string
  os_name: string
  os_version: string | null
  browser_name: string | null
  browser_version: string | null
  locale: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface DeviceProfileFormValues {
  name: string
  platform: DeviceProfilePlatform | ''
  device_model: string
  os_name: string
  os_version: string
  browser_name: string
  browser_version: string
  locale: string
  notes: string
}

export interface DeviceProfileCreatePayload {
  name: string
  platform: DeviceProfilePlatform
  device_model: string
  os_name: string
  os_version: string | null
  browser_name: string | null
  browser_version: string | null
  locale: string | null
  notes: string | null
}

export interface DeviceProfileUpdatePayload {
  name?: string
  platform?: DeviceProfilePlatform
  device_model?: string
  os_name?: string
  os_version?: string | null
  browser_name?: string | null
  browser_version?: string | null
  locale?: string | null
  notes?: string | null
}
