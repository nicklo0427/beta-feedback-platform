export interface ApiErrorPayload {
  code: string
  message: string
  details: unknown
}

export interface ListResponse<T> {
  items: T[]
  total: number
}

export class ApiClientError extends Error {
  statusCode?: number
  code: string
  details: unknown

  constructor(options: {
    message: string
    code?: string
    details?: unknown
    statusCode?: number
  }) {
    super(options.message)
    this.name = 'ApiClientError'
    this.statusCode = options.statusCode
    this.code = options.code ?? 'internal_error'
    this.details = options.details ?? null
  }
}

function isApiErrorPayload(value: unknown): value is ApiErrorPayload {
  return Boolean(
    value &&
      typeof value === 'object' &&
      'code' in value &&
      'message' in value &&
      'details' in value
  )
}

function normalizeApiError(error: unknown): ApiClientError {
  const fallback = new ApiClientError({
    message: 'Unable to reach the backend API.',
    code: 'internal_error'
  })

  if (!error || typeof error !== 'object') {
    return fallback
  }

  const candidate = error as {
    statusCode?: number
    status?: number
    data?: unknown
    message?: string
  }

  if (isApiErrorPayload(candidate.data)) {
    return new ApiClientError({
      message: candidate.data.message,
      code: candidate.data.code,
      details: candidate.data.details,
      statusCode: candidate.statusCode ?? candidate.status
    })
  }

  return new ApiClientError({
    message: candidate.message ?? fallback.message,
    statusCode: candidate.statusCode ?? candidate.status
  })
}

export function useApiClient() {
  const config = useRuntimeConfig()

  async function request<T>(path: string): Promise<T> {
    try {
      return await $fetch<T>(path, {
        baseURL: config.public.apiBaseUrl
      })
    } catch (error) {
      throw normalizeApiError(error)
    }
  }

  return {
    apiBaseUrl: config.public.apiBaseUrl,
    request
  }
}
