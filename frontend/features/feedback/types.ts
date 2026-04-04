export type FeedbackSeverity = 'low' | 'medium' | 'high' | 'critical'

export type FeedbackCategory =
  | 'bug'
  | 'usability'
  | 'performance'
  | 'compatibility'
  | 'other'

export type FeedbackReviewStatus = 'submitted' | 'needs_more_info' | 'reviewed'

export const FEEDBACK_SEVERITY_OPTIONS: FeedbackSeverity[] = [
  'low',
  'medium',
  'high',
  'critical'
]

export const FEEDBACK_CATEGORY_OPTIONS: FeedbackCategory[] = [
  'bug',
  'usability',
  'performance',
  'compatibility',
  'other'
]

export const FEEDBACK_RATING_OPTIONS = ['1', '2', '3', '4', '5'] as const

export const FEEDBACK_REVIEW_STATUS_OPTIONS: FeedbackReviewStatus[] = [
  'submitted',
  'needs_more_info',
  'reviewed'
]

export type FeedbackRatingValue = '' | (typeof FEEDBACK_RATING_OPTIONS)[number]

export interface FeedbackListItem {
  id: string
  task_id: string
  summary: string
  severity: FeedbackSeverity
  category: FeedbackCategory
  submitted_at: string
}

export interface FeedbackDetail {
  id: string
  task_id: string
  campaign_id: string
  device_profile_id: string | null
  summary: string
  rating: number | null
  severity: FeedbackSeverity
  category: FeedbackCategory
  reproduction_steps: string | null
  expected_result: string | null
  actual_result: string | null
  note: string | null
  review_status: FeedbackReviewStatus
  developer_note: string | null
  submitted_at: string
  updated_at: string
}

export interface FeedbackFormValues {
  summary: string
  rating: FeedbackRatingValue
  severity: FeedbackSeverity | ''
  category: FeedbackCategory | ''
  reproduction_steps: string
  expected_result: string
  actual_result: string
  note: string
}

export interface FeedbackCreatePayload {
  summary: string
  rating: number | null
  severity: FeedbackSeverity
  category: FeedbackCategory
  reproduction_steps: string | null
  expected_result: string | null
  actual_result: string | null
  note: string | null
}

export interface FeedbackUpdatePayload {
  summary?: string
  rating?: number | null
  severity?: FeedbackSeverity
  category?: FeedbackCategory
  reproduction_steps?: string | null
  expected_result?: string | null
  actual_result?: string | null
  note?: string | null
  review_status?: FeedbackReviewStatus
  developer_note?: string | null
}

const FEEDBACK_REVIEW_STATUS_LABELS: Record<FeedbackReviewStatus, string> = {
  submitted: 'Submitted',
  needs_more_info: 'Needs More Info',
  reviewed: 'Reviewed'
}

export function formatFeedbackReviewStatusLabel(value: FeedbackReviewStatus): string {
  return FEEDBACK_REVIEW_STATUS_LABELS[value]
}
