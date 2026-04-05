export interface ProjectListItem {
  id: string
  name: string
  description: string | null
  owner_account_id?: string | null
  updated_at: string
}

export interface ProjectDetail {
  id: string
  name: string
  description: string | null
  owner_account_id?: string | null
  created_at: string
  updated_at: string
}

export interface ProjectFormValues {
  name: string
  description: string
}

export interface ProjectCreatePayload {
  name: string
  description: string | null
}

export interface ProjectUpdatePayload {
  name?: string
  description?: string | null
}
