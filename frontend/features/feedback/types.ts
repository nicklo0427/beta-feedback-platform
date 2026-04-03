export type FeedbackSeverity = 'low' | 'medium' | 'high' | 'critical'

export type FeedbackCategory =
  | 'bug'
  | 'usability'
  | 'performance'
  | 'compatibility'
  | 'other'

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
  submitted_at: string
  updated_at: string
}
