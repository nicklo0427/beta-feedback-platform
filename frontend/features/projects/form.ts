import type {
  ProjectCreatePayload,
  ProjectDetail,
  ProjectFormValues,
  ProjectUpdatePayload
} from './types'

function normalizeRequiredValue(value: string): string {
  return value.trim()
}

function normalizeOptionalValue(value: string): string | null {
  const normalized = value.trim()
  return normalized || null
}

export function createEmptyProjectFormValues(): ProjectFormValues {
  return {
    name: '',
    description: ''
  }
}

export function toProjectFormValues(project: ProjectDetail): ProjectFormValues {
  return {
    name: project.name,
    description: project.description ?? ''
  }
}

export function buildProjectCreatePayload(
  values: ProjectFormValues
): ProjectCreatePayload {
  return {
    name: normalizeRequiredValue(values.name),
    description: normalizeOptionalValue(values.description)
  }
}

export function buildProjectUpdatePayload(
  values: ProjectFormValues,
  initialValues: ProjectFormValues
): ProjectUpdatePayload | null {
  const payload: ProjectUpdatePayload = {}

  const currentName = normalizeRequiredValue(values.name)
  const initialName = normalizeRequiredValue(initialValues.name)
  if (currentName !== initialName) {
    payload.name = currentName
  }

  const currentDescription = normalizeOptionalValue(values.description)
  const initialDescription = normalizeOptionalValue(initialValues.description)
  if (currentDescription !== initialDescription) {
    payload.description = currentDescription
  }

  if (Object.keys(payload).length === 0) {
    return null
  }

  return payload
}
