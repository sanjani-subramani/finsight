import Papa from 'papaparse'
import { useState } from 'react'
import { useCreateReconRun } from '../../hooks/useReconx'
import './NewRunPanel.css'

type SourceKey = 'internal' | 'gateway' | 'bank'

interface SourceState {
  fileName: string | null
  rawText: string | null
  preview: Record<string, string>[]
  parsedAll: Record<string, string>[]
}

const EMPTY_SOURCE: SourceState = { fileName: null, rawText: null, preview: [], parsedAll: [] }

function DropZone({
  label,
  state,
  onFile,
}: {
  label: string
  state: SourceState
  onFile: (file: File) => void
}) {
  return (
    <div
      className="drop-zone"
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault()
        const file = e.dataTransfer.files[0]
        if (file) onFile(file)
      }}
    >
      <p className="drop-zone__label">{label}</p>
      <input
        type="file"
        accept=".csv"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) onFile(file)
        }}
      />
      {state.fileName && <p className="drop-zone__filename">{state.fileName}</p>}
      {state.preview.length > 0 && (
        <table className="drop-zone__preview">
          <caption>Preview -- first {state.preview.length} rows (client-side only)</caption>
          <thead>
            <tr>
              {Object.keys(state.preview[0]).map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {state.preview.map((row, i) => (
              <tr key={i}>
                {Object.keys(state.preview[0]).map((col) => (
                  <td key={col}>{row[col]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export interface NewRunPanelProps {
  orgId: string
  onCreated?: (runId: string) => void
}

/**
 * This preview is PREVIEW-ONLY. Parsing a CSV in the browser (PapaParse)
 * is convenient for showing an ops engineer "does this look like what I
 * meant to upload" before committing, but it is never the authoritative
 * parse -- app.modules.org.reconx.ingest does that server-side with
 * pandas, against the exact same ReconRecord contract the matching
 * engine consumes. A client-side quirk (locale-specific date parsing,
 * a stray BOM, Excel's CSV dialect) must never silently diverge from
 * what the backend actually reconciles against.
 *
 * Reflecting that: the bank slot is sent to the backend as the RAW file
 * text (ingest_bank accepts a CSV string directly and parses it
 * server-side) -- true preview-only. internal/gateway have no raw-CSV
 * ingestion endpoint (Step 15 only accepts already-parsed records for
 * those two sources), so their PapaParse output is what's actually
 * submitted; there is no second, server-side CSV parse to defer to for
 * them today.
 */
export function NewRunPanel({ orgId, onCreated }: NewRunPanelProps) {
  const [internal, setInternal] = useState<SourceState>(EMPTY_SOURCE)
  const [gateway, setGateway] = useState<SourceState>(EMPTY_SOURCE)
  const [bank, setBank] = useState<SourceState>(EMPTY_SOURCE)
  const createRun = useCreateReconRun(orgId)

  function loadFile(key: SourceKey, file: File) {
    const setter = key === 'internal' ? setInternal : key === 'gateway' ? setGateway : setBank
    Papa.parse<Record<string, string>>(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        setter({
          fileName: file.name,
          rawText: null,
          preview: results.data.slice(0, 5),
          parsedAll: results.data,
        })
      },
    })
    file.text().then((text) => {
      setter((prev) => ({ ...prev, rawText: text }))
    })
  }

  async function handleSubmit() {
    if (!bank.rawText) return
    const result = await createRun.mutateAsync({
      internal: internal.parsedAll,
      gateway: gateway.parsedAll,
      bank: bank.rawText,
    })
    onCreated?.(result.run_id)
  }

  const canSubmit = internal.parsedAll.length > 0 && gateway.parsedAll.length > 0 && !!bank.rawText

  return (
    <div className="new-run-panel">
      <h2>New reconciliation run</h2>
      <div className="new-run-panel__drops">
        <DropZone label="Internal ledger CSV" state={internal} onFile={(f) => loadFile('internal', f)} />
        <DropZone label="Gateway export CSV" state={gateway} onFile={(f) => loadFile('gateway', f)} />
        <DropZone label="Bank statement CSV" state={bank} onFile={(f) => loadFile('bank', f)} />
      </div>
      <button type="button" disabled={!canSubmit || createRun.isPending} onClick={handleSubmit}>
        {createRun.isPending ? 'Running reconciliation…' : 'Run reconciliation'}
      </button>
      {createRun.isError && <p className="new-run-panel__error">Could not start the run. Please try again.</p>}
    </div>
  )
}
