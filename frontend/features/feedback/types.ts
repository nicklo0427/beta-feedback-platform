import type { AppLocale } from '~/features/i18n/use-app-i18n'

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

export interface FeedbackQueueItem {
  id: string
  task_id: string
  campaign_id: string
  summary: string
  severity: FeedbackSeverity
  category: FeedbackCategory
  review_status: FeedbackReviewStatus
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
  resubmitted_at: string | null
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

export interface FeedbackQueueFilters {
  mine?: boolean
  actorId?: string | null
  reviewStatus?: FeedbackReviewStatus | null
}

const FEEDBACK_REVIEW_STATUS_LABELS: Record<
  AppLocale,
  Record<FeedbackReviewStatus, string>
> = {
  'zh-TW': {
    submitted: '已送出',
    needs_more_info: '需要補充',
    reviewed: '已看過'
  },
  en: {
    submitted: 'Sent',
    needs_more_info: 'More detail needed',
    reviewed: 'Reviewed'
  }
}

const FEEDBACK_SEVERITY_LABELS: Record<AppLocale, Record<FeedbackSeverity, string>> = {
  'zh-TW': {
    low: '低',
    medium: '中',
    high: '高',
    critical: '嚴重'
  },
  en: {
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    critical: 'Critical'
  }
}

const FEEDBACK_CATEGORY_LABELS: Record<AppLocale, Record<FeedbackCategory, string>> = {
  'zh-TW': {
    bug: '錯誤',
    usability: '易用性',
    performance: '效能',
    compatibility: '相容性',
    other: '其他'
  },
  en: {
    bug: 'Bug',
    usability: 'Usability',
    performance: 'Performance',
    compatibility: 'Compatibility',
    other: 'Other'
  }
}

export function formatFeedbackReviewStatusLabel(
  value: FeedbackReviewStatus,
  locale: AppLocale = 'zh-TW'
): string {
  return FEEDBACK_REVIEW_STATUS_LABELS[locale][value]
}

export function formatFeedbackSeverityLabel(
  value: FeedbackSeverity,
  locale: AppLocale = 'zh-TW'
): string {
  return FEEDBACK_SEVERITY_LABELS[locale][value]
}

export function formatFeedbackCategoryLabel(
  value: FeedbackCategory,
  locale: AppLocale = 'zh-TW'
): string {
  return FEEDBACK_CATEGORY_LABELS[locale][value]
}
