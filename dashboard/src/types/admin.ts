export interface QueueDepthResponse {
  topic: string
  length: number
  pending: number
}

export interface DlqMessageResponse {
  message_id: string
  payload: any
}

export interface DlqReplayResponse {
  message_id: string
  requeued_to: string
}

export interface WorkerHealthResponse {
  status: 'healthy' | 'unhealthy' | 'unknown'
  last_heartbeat: string | null
  seconds_since_heartbeat: number | null
}
