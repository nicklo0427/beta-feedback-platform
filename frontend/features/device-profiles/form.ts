import type {
  DeviceProfileCreatePayload,
  DeviceProfileDetail,
  DeviceProfileFormValues,
  DeviceProfilePlatform,
  DeviceProfileUpdatePayload
} from './types'

function normalizeRequiredValue(value: string): string {
  return value.trim()
}

function normalizeOptionalValue(value: string): string | null {
  const normalized = value.trim()
  return normalized || null
}

export function createEmptyDeviceProfileFormValues(): DeviceProfileFormValues {
  return {
    name: '',
    platform: '',
    device_model: '',
    os_name: '',
    os_version: '',
    browser_name: '',
    browser_version: '',
    locale: '',
    notes: ''
  }
}

export function toDeviceProfileFormValues(
  deviceProfile: DeviceProfileDetail
): DeviceProfileFormValues {
  return {
    name: deviceProfile.name,
    platform: deviceProfile.platform,
    device_model: deviceProfile.device_model,
    os_name: deviceProfile.os_name,
    os_version: deviceProfile.os_version ?? '',
    browser_name: deviceProfile.browser_name ?? '',
    browser_version: deviceProfile.browser_version ?? '',
    locale: deviceProfile.locale ?? '',
    notes: deviceProfile.notes ?? ''
  }
}

export function buildDeviceProfileCreatePayload(
  values: DeviceProfileFormValues
): DeviceProfileCreatePayload {
  return {
    name: normalizeRequiredValue(values.name),
    platform: values.platform as DeviceProfilePlatform,
    device_model: normalizeRequiredValue(values.device_model),
    os_name: normalizeRequiredValue(values.os_name),
    os_version: normalizeOptionalValue(values.os_version),
    browser_name: normalizeOptionalValue(values.browser_name),
    browser_version: normalizeOptionalValue(values.browser_version),
    locale: normalizeOptionalValue(values.locale),
    notes: normalizeOptionalValue(values.notes)
  }
}

export function buildDeviceProfileUpdatePayload(
  values: DeviceProfileFormValues,
  initialValues: DeviceProfileFormValues
): DeviceProfileUpdatePayload | null {
  const payload: DeviceProfileUpdatePayload = {}

  const currentName = normalizeRequiredValue(values.name)
  const initialName = normalizeRequiredValue(initialValues.name)
  if (currentName !== initialName) {
    payload.name = currentName
  }

  if (values.platform !== initialValues.platform) {
    payload.platform = values.platform as DeviceProfilePlatform
  }

  const currentDeviceModel = normalizeRequiredValue(values.device_model)
  const initialDeviceModel = normalizeRequiredValue(initialValues.device_model)
  if (currentDeviceModel !== initialDeviceModel) {
    payload.device_model = currentDeviceModel
  }

  const currentOsName = normalizeRequiredValue(values.os_name)
  const initialOsName = normalizeRequiredValue(initialValues.os_name)
  if (currentOsName !== initialOsName) {
    payload.os_name = currentOsName
  }

  const currentOsVersion = normalizeOptionalValue(values.os_version)
  const initialOsVersion = normalizeOptionalValue(initialValues.os_version)
  if (currentOsVersion !== initialOsVersion) {
    payload.os_version = currentOsVersion
  }

  const currentBrowserName = normalizeOptionalValue(values.browser_name)
  const initialBrowserName = normalizeOptionalValue(initialValues.browser_name)
  if (currentBrowserName !== initialBrowserName) {
    payload.browser_name = currentBrowserName
  }

  const currentBrowserVersion = normalizeOptionalValue(values.browser_version)
  const initialBrowserVersion = normalizeOptionalValue(initialValues.browser_version)
  if (currentBrowserVersion !== initialBrowserVersion) {
    payload.browser_version = currentBrowserVersion
  }

  const currentLocale = normalizeOptionalValue(values.locale)
  const initialLocale = normalizeOptionalValue(initialValues.locale)
  if (currentLocale !== initialLocale) {
    payload.locale = currentLocale
  }

  const currentNotes = normalizeOptionalValue(values.notes)
  const initialNotes = normalizeOptionalValue(initialValues.notes)
  if (currentNotes !== initialNotes) {
    payload.notes = currentNotes
  }

  if (Object.keys(payload).length === 0) {
    return null
  }

  return payload
}
