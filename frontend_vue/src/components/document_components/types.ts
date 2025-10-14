// Shared document-related types for Document Manager components
export interface EgnyteFolder {
  id: string
  name: string
  path: string
  count: number
  metadata?: Record<string, any>
}

export interface EgnyteFile {
  id: string
  name: string
  path: string
  type: string
  size: number
  modified: string
  tags: string[]
  metadata?: Record<string, any>
}

export interface ViewMode {
  id: string
  label: string
  icon: string
  description: string
}
