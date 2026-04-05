import type {
  AccountCreatePayload,
  AccountDetail,
  AccountFormValues,
  AccountRole,
  AccountUpdatePayload
} from './types'

function normalizeRequiredValue(value: string): string {
  return value.trim()
}

function normalizeOptionalValue(value: string): string | null {
  const normalized = value.trim()
  return normalized || null
}

export function createEmptyAccountFormValues(): AccountFormValues {
  return {
    display_name: '',
    role: '',
    bio: '',
    locale: ''
  }
}

export function toAccountFormValues(account: AccountDetail): AccountFormValues {
  return {
    display_name: account.display_name,
    role: account.role,
    bio: account.bio ?? '',
    locale: account.locale ?? ''
  }
}

export function buildAccountCreatePayload(
  values: AccountFormValues
): AccountCreatePayload {
  return {
    display_name: normalizeRequiredValue(values.display_name),
    role: values.role as AccountRole,
    bio: normalizeOptionalValue(values.bio),
    locale: normalizeOptionalValue(values.locale)
  }
}

export function buildAccountUpdatePayload(
  values: AccountFormValues,
  initialValues: AccountFormValues
): AccountUpdatePayload | null {
  const payload: AccountUpdatePayload = {}

  const currentDisplayName = normalizeRequiredValue(values.display_name)
  const initialDisplayName = normalizeRequiredValue(initialValues.display_name)
  if (currentDisplayName !== initialDisplayName) {
    payload.display_name = currentDisplayName
  }

  if (values.role !== initialValues.role) {
    payload.role = values.role as AccountRole
  }

  const currentBio = normalizeOptionalValue(values.bio)
  const initialBio = normalizeOptionalValue(initialValues.bio)
  if (currentBio !== initialBio) {
    payload.bio = currentBio
  }

  const currentLocale = normalizeOptionalValue(values.locale)
  const initialLocale = normalizeOptionalValue(initialValues.locale)
  if (currentLocale !== initialLocale) {
    payload.locale = currentLocale
  }

  if (Object.keys(payload).length === 0) {
    return null
  }

  return payload
}
