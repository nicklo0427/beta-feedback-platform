import type {
  FeedbackCategory,
  FeedbackCreatePayload,
  FeedbackDetail,
  FeedbackFormValues,
  FeedbackRatingValue,
  FeedbackSeverity,
  FeedbackUpdatePayload
} from './types'

function normalizeRequiredValue(value: string): string {
  return value.trim()
}

function normalizeOptionalValue(value: string): string | null {
  const normalized = value.trim()
  return normalized || null
}

function normalizeRatingValue(value: FeedbackRatingValue): number | null {
  if (!value) {
    return null
  }

  return Number.parseInt(value, 10)
}

export function createEmptyFeedbackFormValues(): FeedbackFormValues {
  return {
    summary: '',
    rating: '',
    severity: '',
    category: '',
    reproduction_steps: '',
    expected_result: '',
    actual_result: '',
    note: ''
  }
}

export function toFeedbackFormValues(feedback: FeedbackDetail): FeedbackFormValues {
  return {
    summary: feedback.summary,
    rating: feedback.rating === null ? '' : String(feedback.rating) as FeedbackRatingValue,
    severity: feedback.severity,
    category: feedback.category,
    reproduction_steps: feedback.reproduction_steps ?? '',
    expected_result: feedback.expected_result ?? '',
    actual_result: feedback.actual_result ?? '',
    note: feedback.note ?? ''
  }
}

export function buildFeedbackCreatePayload(
  values: FeedbackFormValues
): FeedbackCreatePayload {
  return {
    summary: normalizeRequiredValue(values.summary),
    rating: normalizeRatingValue(values.rating),
    severity: values.severity as FeedbackSeverity,
    category: values.category as FeedbackCategory,
    reproduction_steps: normalizeOptionalValue(values.reproduction_steps),
    expected_result: normalizeOptionalValue(values.expected_result),
    actual_result: normalizeOptionalValue(values.actual_result),
    note: normalizeOptionalValue(values.note)
  }
}

export function buildFeedbackUpdatePayload(
  values: FeedbackFormValues,
  initialValues: FeedbackFormValues
): FeedbackUpdatePayload | null {
  const payload: FeedbackUpdatePayload = {}

  const currentSummary = normalizeRequiredValue(values.summary)
  const initialSummary = normalizeRequiredValue(initialValues.summary)
  if (currentSummary !== initialSummary) {
    payload.summary = currentSummary
  }

  const currentRating = normalizeRatingValue(values.rating)
  const initialRating = normalizeRatingValue(initialValues.rating)
  if (currentRating !== initialRating) {
    payload.rating = currentRating
  }

  if (values.severity !== initialValues.severity) {
    payload.severity = values.severity as FeedbackSeverity
  }

  if (values.category !== initialValues.category) {
    payload.category = values.category as FeedbackCategory
  }

  const currentReproductionSteps = normalizeOptionalValue(values.reproduction_steps)
  const initialReproductionSteps = normalizeOptionalValue(initialValues.reproduction_steps)
  if (currentReproductionSteps !== initialReproductionSteps) {
    payload.reproduction_steps = currentReproductionSteps
  }

  const currentExpectedResult = normalizeOptionalValue(values.expected_result)
  const initialExpectedResult = normalizeOptionalValue(initialValues.expected_result)
  if (currentExpectedResult !== initialExpectedResult) {
    payload.expected_result = currentExpectedResult
  }

  const currentActualResult = normalizeOptionalValue(values.actual_result)
  const initialActualResult = normalizeOptionalValue(initialValues.actual_result)
  if (currentActualResult !== initialActualResult) {
    payload.actual_result = currentActualResult
  }

  const currentNote = normalizeOptionalValue(values.note)
  const initialNote = normalizeOptionalValue(initialValues.note)
  if (currentNote !== initialNote) {
    payload.note = currentNote
  }

  if (Object.keys(payload).length === 0) {
    return null
  }

  return payload
}
