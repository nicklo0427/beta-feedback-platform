import type {
  ParticipationRequestCreatePayload,
  ParticipationRequestFormValues
} from './types'

function normalizeRequiredValue(value: string): string {
  return value.trim()
}

function normalizeOptionalValue(value: string): string | null {
  const normalized = value.trim()
  return normalized || null
}

export function createEmptyParticipationRequestFormValues(
  deviceProfileId = ''
): ParticipationRequestFormValues {
  return {
    device_profile_id: deviceProfileId,
    note: ''
  }
}

export function buildParticipationRequestCreatePayload(
  values: ParticipationRequestFormValues
): ParticipationRequestCreatePayload {
  return {
    device_profile_id: normalizeRequiredValue(values.device_profile_id),
    note: normalizeOptionalValue(values.note)
  }
}
