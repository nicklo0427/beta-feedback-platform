import type {
  TaskCreatePayload,
  TaskDetail,
  TaskFormValues,
  TaskUpdatePayload
} from './types'

function normalizeRequiredValue(value: string): string {
  return value.trim()
}

function normalizeOptionalValue(value: string): string | null {
  const normalized = value.trim()
  return normalized || null
}

export function createEmptyTaskFormValues(): TaskFormValues {
  return {
    title: '',
    instruction_summary: '',
    device_profile_id: '',
    status: 'draft'
  }
}

export function toTaskFormValues(task: TaskDetail): TaskFormValues {
  return {
    title: task.title,
    instruction_summary: task.instruction_summary ?? '',
    device_profile_id: task.device_profile_id ?? '',
    status: task.status
  }
}

export function buildTaskCreatePayload(values: TaskFormValues): TaskCreatePayload {
  return {
    title: normalizeRequiredValue(values.title),
    instruction_summary: normalizeOptionalValue(values.instruction_summary),
    device_profile_id: normalizeOptionalValue(values.device_profile_id),
    status: values.status
  }
}

export function buildTaskUpdatePayload(
  values: TaskFormValues,
  initialValues: TaskFormValues
): TaskUpdatePayload | null {
  const payload: TaskUpdatePayload = {}

  const currentTitle = normalizeRequiredValue(values.title)
  const initialTitle = normalizeRequiredValue(initialValues.title)
  if (currentTitle !== initialTitle) {
    payload.title = currentTitle
  }

  const currentInstructionSummary = normalizeOptionalValue(values.instruction_summary)
  const initialInstructionSummary = normalizeOptionalValue(initialValues.instruction_summary)
  if (currentInstructionSummary !== initialInstructionSummary) {
    payload.instruction_summary = currentInstructionSummary
  }

  const currentDeviceProfileId = normalizeOptionalValue(values.device_profile_id)
  const initialDeviceProfileId = normalizeOptionalValue(initialValues.device_profile_id)
  if (currentDeviceProfileId !== initialDeviceProfileId) {
    payload.device_profile_id = currentDeviceProfileId
  }

  if (values.status !== initialValues.status) {
    payload.status = values.status
  }

  if (Object.keys(payload).length === 0) {
    return null
  }

  return payload
}
