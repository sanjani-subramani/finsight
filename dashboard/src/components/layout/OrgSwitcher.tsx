import { useOrgAuth } from '../../auth/useOrgAuth'

export function OrgSwitcher() {
  const { orgs, currentOrgId, switchOrg } = useOrgAuth()

  if (orgs.length <= 1) {
    return <span className="org-switcher org-switcher--single">{orgs[0]?.org_name ?? 'No organization'}</span>
  }

  return (
    <select
      aria-label="Organization"
      className="org-switcher"
      value={currentOrgId ?? ''}
      onChange={(e) => switchOrg(e.target.value)}
    >
      {orgs.map((org) => (
        <option key={org.org_id} value={org.org_id}>
          {org.org_name}
        </option>
      ))}
    </select>
  )
}
