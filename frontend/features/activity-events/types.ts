export type ActivityEntityType = 'participation_request' | 'task' | 'feedback'

export type ActivityEventType =
  | 'participation_request_created'
  | 'participation_request_accepted'
  | 'participation_request_declined'
  | 'participation_request_withdrawn'
  | 'task_created'
  | 'task_created_from_participation_request'
  | 'feedback_submitted'
  | 'feedback_reviewed'
  | 'feedback_needs_more_info'
  | 'feedback_resubmitted'
  | 'task_resolved'

export interface ActivityEventItem {
  id: string
  entity_type: ActivityEntityType
  entity_id: string
  event_type: ActivityEventType
  actor_account_id: string
  actor_account_display_name: string | null
  summary: string
  created_at: string
}
