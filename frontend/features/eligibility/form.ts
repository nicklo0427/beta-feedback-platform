import type {
  EligibilityRuleCreatePayload,
  EligibilityRuleDetail,
  EligibilityRuleFormValues,
  EligibilityRulePlatform,
  EligibilityRuleUpdatePayload
} from './types'

function normalizeOptionalValue(value: string): string | null {
  const normalized = value.trim()
  return normalized || null
}

export function createEmptyEligibilityRuleFormValues(): EligibilityRuleFormValues {
  return {
    platform: '',
    os_name: '',
    os_version_min: '',
    os_version_max: '',
    install_channel: '',
    is_active: true
  }
}

export function toEligibilityRuleFormValues(
  eligibilityRule: EligibilityRuleDetail
): EligibilityRuleFormValues {
  return {
    platform: eligibilityRule.platform,
    os_name: eligibilityRule.os_name ?? '',
    os_version_min: eligibilityRule.os_version_min ?? '',
    os_version_max: eligibilityRule.os_version_max ?? '',
    install_channel: eligibilityRule.install_channel ?? '',
    is_active: eligibilityRule.is_active
  }
}

export function buildEligibilityRuleCreatePayload(
  values: EligibilityRuleFormValues
): EligibilityRuleCreatePayload {
  return {
    platform: values.platform as EligibilityRulePlatform,
    os_name: normalizeOptionalValue(values.os_name),
    os_version_min: normalizeOptionalValue(values.os_version_min),
    os_version_max: normalizeOptionalValue(values.os_version_max),
    install_channel: normalizeOptionalValue(values.install_channel),
    is_active: values.is_active
  }
}

export function buildEligibilityRuleUpdatePayload(
  values: EligibilityRuleFormValues,
  initialValues: EligibilityRuleFormValues
): EligibilityRuleUpdatePayload | null {
  const payload: EligibilityRuleUpdatePayload = {}

  if (values.platform !== initialValues.platform) {
    payload.platform = values.platform as EligibilityRulePlatform
  }

  const currentOsName = normalizeOptionalValue(values.os_name)
  const initialOsName = normalizeOptionalValue(initialValues.os_name)
  if (currentOsName !== initialOsName) {
    payload.os_name = currentOsName
  }

  const currentOsVersionMin = normalizeOptionalValue(values.os_version_min)
  const initialOsVersionMin = normalizeOptionalValue(initialValues.os_version_min)
  if (currentOsVersionMin !== initialOsVersionMin) {
    payload.os_version_min = currentOsVersionMin
  }

  const currentOsVersionMax = normalizeOptionalValue(values.os_version_max)
  const initialOsVersionMax = normalizeOptionalValue(initialValues.os_version_max)
  if (currentOsVersionMax !== initialOsVersionMax) {
    payload.os_version_max = currentOsVersionMax
  }

  const currentInstallChannel = normalizeOptionalValue(values.install_channel)
  const initialInstallChannel = normalizeOptionalValue(initialValues.install_channel)
  if (currentInstallChannel !== initialInstallChannel) {
    payload.install_channel = currentInstallChannel
  }

  if (values.is_active !== initialValues.is_active) {
    payload.is_active = values.is_active
  }

  if (Object.keys(payload).length === 0) {
    return null
  }

  return payload
}
