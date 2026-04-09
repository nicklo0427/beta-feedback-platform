export type TaskStatus =
  | 'draft'
  | 'open'
  | 'assigned'
  | 'in_progress'
  | 'submitted'
  | 'closed'

export const TASK_STATUSES: TaskStatus[] = [
  'draft',
  'open',
  'assigned',
  'in_progress',
  'submitted',
  'closed'
]

const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  draft: '草稿',
  open: '開放中',
  assigned: '已指派',
  in_progress: '進行中',
  submitted: '已提交',
  closed: '已關閉'
}

export function isTaskStatus(value: unknown): value is TaskStatus {
  return typeof value === 'string' && TASK_STATUSES.includes(value as TaskStatus)
}

export function formatTaskStatusLabel(value: TaskStatus): string {
  return TASK_STATUS_LABELS[value]
}

export interface TaskListItem {
  id: string
  campaign_id: string
  device_profile_id: string | null
  title: string
  status: TaskStatus
  updated_at: string
  qualification_context?: TaskQualificationContext
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
}

export interface TaskQualificationContext {
  device_profile_id: string
  device_profile_name: string
  qualification_status: 'qualified' | 'not_qualified'
  matched_rule_id: string | null
  reason_summary: string | null
  qualification_drift: boolean
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
}

export interface TaskAssignmentQualificationPreview {
  device_profile_id: string
  device_profile_name: string
  qualification_status: 'qualified' | 'not_qualified'
  matched_rule_id: string | null
  reason_codes: string[]
  reason_summary: string | null
}
