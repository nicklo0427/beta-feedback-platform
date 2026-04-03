export interface DeviceProfileReputationSummary {
  device_profile_id: string
  tasks_assigned_count: number
  tasks_submitted_count: number
  feedback_submitted_count: number
  submission_rate: number
  last_feedback_at: string | null
  updated_at: string
}

export interface CampaignReputationSummary {
  campaign_id: string
  tasks_total_count: number
  tasks_closed_count: number
  feedback_received_count: number
  closure_rate: number
  last_feedback_at: string | null
  updated_at: string
}
