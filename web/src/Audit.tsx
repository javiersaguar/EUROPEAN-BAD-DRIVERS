import { useState } from 'react'
// Development-only audit control. Vite removes this module from production.
export default function Audit() {
  const [result, setResult] = useState('')
  async function audit() {
    setResult('Comprobando…')
    const axe = await import('axe-core')
    const report = await axe.default.run(document.querySelector('main')!, {
      runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] },
    })
    setResult(
      JSON.stringify(
        report.violations.map((v) => ({
          id: v.id,
          impact: v.impact,
          nodes: v.nodes.map((n) => ({ target: n.target, summary: n.failureSummary })),
        })),
        null,
        2,
      ),
    )
  }
  return (
    <aside style={{ padding: 20, marginLeft: 250 }}>
      <button onClick={() => void audit()}>Auditar accesibilidad</button>
      <pre role="status" data-audit-done={result.startsWith('[')}>
        {result}
      </pre>
    </aside>
  )
}
