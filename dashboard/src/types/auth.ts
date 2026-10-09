// Mirrors app/api/schemas/auth.py response shapes exactly -- field names
// match the backend JSON so a schema drift shows up as a TS error here
// rather than a silent runtime mismatch.

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserResponse {
  id: string
  email: string
  display_name: string | null
  phone: string | null
  account_type: string
  is_active: boolean
  is_verified: boolean
  risk_tolerance: string
  onboarding_stage: string
}

// Org roles as declared by the ck_org_memberships_role check constraint
// (app/models/tables.py) -- keep this union in sync with the backend.
export type OrgRole = 'owner' | 'ops_engineer' | 'recon_analyst' | 'viewer'

export interface OrgMembershipResponse {
  org_id: string
  org_name: string
  org_slug: string
  role: OrgRole
}
