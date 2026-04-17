import type { AppLocale } from '~/features/i18n/use-app-i18n'

export type TaskStatus =
  | 'draft'
  | 'open'
  | 'assigned'
  | 'in_progress'
  | 'submitted'
  | 'closed'

export type TaskResolutionOutcome =
  | 'confirmed_issue'
  | 'needs_follow_up'
  | 'not_reproducible'
  | 'cancelled'

export const TASK_STATUSES: TaskStatus[] = [
  'draft',
  'open',
  'assigned',
  'in_progress',
  'submitted',
  'closed'
]

const TASK_STATUS_LABELS: Record<AppLocale, Record<TaskStatus, string>> = {
  'zh-TW': {
    draft: '草稿',
    open: '開放中',
    assigned: '已指派',
    in_progress: '進行中',
    submitted: '已提交',
    closed: '已關閉'
  },
  en: {
    draft: 'Draft',
    open: 'Open',
    assigned: 'Assigned',
    in_progress: 'In progress',
    submitted: 'Submitted',
    closed: 'Closed'
  }
}

export const TASK_RESOLUTION_OUTCOMES: TaskResolutionOutcome[] = [
  'confirmed_issue',
  'needs_follow_up',
  'not_reproducible',
  'cancelled'
]

const TASK_RESOLUTION_OUTCOME_LABELS: Record<
  AppLocale,
  Record<TaskResolutionOutcome, string>
> = {
  'zh-TW': {
    confirmed_issue: '確認問題',
    needs_follow_up: '需要後續追蹤',
    not_reproducible: '無法重現',
    cancelled: '取消處理'
  },
  en: {
    confirmed_issue: 'Confirmed issue',
    needs_follow_up: 'Needs follow-up',
    not_reproducible: 'Not reproducible',
    cancelled: 'Cancelled'
  }
}

export function isTaskStatus(value: unknown): value is TaskStatus {
  return typeof value === 'string' && TASK_STATUSES.includes(value as TaskStatus)
}

export function formatTaskStatusLabel(
  value: TaskStatus,
  locale: AppLocale = 'zh-TW'
): string {
  return TASK_STATUS_LABELS[locale][value]
}

export function formatTaskResolutionOutcomeLabel(
  value: TaskResolutionOutcome,
  locale: AppLocale = 'zh-TW'
): string {
  return TASK_RESOLUTION_OUTCOME_LABELS[locale][value]
}

export interface TaskListItem {
  id: string
  campaign_id: string
  device_profile_id: string | null
  title: string
  status: TaskStatus
  updated_at: string
  qualification_context?: TaskQualificationContext
  resolution_context?: TaskResolutionContext
}

export interface TaskDetail {
  id: string
  campaign_id: string
  device_profile_id: string | null
  title: string
  instruction_summary: string | null
  status: TaskStatus
  submitted_at: string | null
  created_at: string
  updated_at: string
  qualification_context?: TaskQualificationContext
  participation_request_context?: TaskParticipationRequestContext
  resolution_context?: TaskResolutionContext
}

export interface TaskQualificationContext {
  device_profile_id: string
  device_profile_name: string
  qualification_status: 'qualified' | 'not_qualified'
  matched_rule_id: string | null
  reason_summary: string | null
  qualification_drift: boolean
}

export interface TaskParticipationRequestContext {
  request_id: string
  request_status: 'pending' | 'accepted' | 'declined' | 'withdrawn'
  tester_account_id: string
  tester_account_display_name: string
  assignment_created_at: string | null
}

export interface TaskResolutionContext {
  resolution_outcome: TaskResolutionOutcome
  resolution_note: string | null
  resolved_at: string
  resolved_by_account_id: string
  resolved_by_account_display_name: string
}

export interface TaskFormValues {
  title: string
  instruction_summary: string
  device_profile_id: string
  status: TaskStatus
}

export interface TaskCreatePayload {
  title: string
  instruction_summary: string | null
  device_profile_id: string | null
  status: TaskStatus
}

export interface TaskUpdatePayload {
  title?: string
  instruction_summary?: string | null
  device_profile_id?: string | null
  status?: TaskStatus
  resolution_outcome?: TaskResolutionOutcome | null
  resolution_note?: string | null
}

export interface TaskAssignmentQualificationPreview {
  device_profile_id: string
  device_profile_name: string
  qualification_status: 'qualified' | 'not_qualified'
  matched_rule_id: string | null
  reason_codes: string[]
  reason_summary: string | null
}
