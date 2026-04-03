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

export function isTaskStatus(value: unknown): value is TaskStatus {
  return typeof value === 'string' && TASK_STATUSES.includes(value as TaskStatus)
}

export interface TaskListItem {
  id: string
  campaign_id: string
  device_profile_id: string | null
  title: string
  status: TaskStatus
  updated_at: string
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
}
