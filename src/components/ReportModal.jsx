import { useState } from 'react';

const API_BASE = import.meta.env.VITE_REPORT_API_URL || '';

/* Steps match real backend SSE events — idx 0-3 */
const STEPS = [
  { label: 'DataCollector',   role: 'Structuring KD + HMIS data',      pct: 15  },
  { label: 'Analyst',         role: 'Root causes & priorities',         pct: 55  },
  { label: 'ReportWriter',    role: 'Building HTML report',             pct: 90  },
  { label: 'QualityChecker',  role: 'Tone & accuracy review',           pct: 100 },
];

export default function ReportModal({ divisionId, divisionName, divisionColor, onClose }) {
  const [phase,   setPhase]   = useState('idle'); // idle | loading | done | error
  const [stepIdx, setStepIdx] = useState(0);
  const [html,    setHtml]    = useState('');
  const [errMsg,  setErrMsg]  = useState('');

  /* SSE stream reader — real progress from backend, no fake timer */
  async function generate() {
    setPhase('loading');
    setStepIdx(0);
    try {
      const res = await fetch(`${API_BASE}/api/report/${divisionId}`, {
        method: 'POST',
      });
      /* Pre-SSE failures (404 / 405 / 500 before streaming starts) */
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Server error' }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let   buffer  = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          let event;
          try { event = JSON.parse(line.slice(6)); } catch { continue; }
          if (event.type === 'step')  setStepIdx(event.idx);
          if (event.type === 'done')  { setHtml(event.html); setPhase('done'); }
          if (event.type === 'error') { setErrMsg(event.message); setPhase('error'); }
        }
      }
    } catch (e) {
      setErrMsg(e.message);
      setPhase('error');
    }
  }

  /* Blob URL — avoids deprecated document.write and popup-blocker issues */
  function handlePrint() {
    const blob = new Blob([html], { type: 'text/html' });
    const url  = URL.createObjectURL(blob);
    const win  = window.open(url, '_blank');
    if (win) {
      win.addEventListener('load', () => {
        setTimeout(() => { win.print(); URL.revokeObjectURL(url); }, 400);
      });
    }
  }

  const step = STEPS[Math.min(stepIdx, STEPS.length - 1)];

  const accent = divisionColor || '#FF5500';

  return (
    <div className="rpt-overlay" style={{ '--rpt-accent': accent }} onClick={onClose}>
      <div className="rpt-modal" onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="rpt-header">
          <div>
            <p className="rpt-header-label">REPORT GENERATOR</p>
            <h2 className="rpt-header-title">{divisionName}</h2>
          </div>
          <div className="rpt-header-actions">
            {phase === 'done' && (
              <button className="rpt-btn rpt-btn--pdf" onClick={handlePrint}>
                Download PDF
              </button>
            )}
            <button className="rpt-btn rpt-btn--close" onClick={onClose}>
              ✕
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="rpt-body">

          {/* Idle */}
          {phase === 'idle' && (
            <div className="rpt-idle">
              <div className="rpt-idle-pipeline">
                {STEPS.map((s, i) => (
                  <div key={i} className="rpt-idle-node-wrap">
                    <div className="rpt-idle-node" style={{ '--ac': accent }}>
                      <span className="rpt-idle-node-num">{i + 1}</span>
                    </div>
                    <span className="rpt-idle-node-label">{s.label}</span>
                    {i < STEPS.length - 1 && <div className="rpt-idle-connector" style={{ '--ac': accent }} />}
                  </div>
                ))}
              </div>
              <h3 className="rpt-idle-title">Generate Division Report</h3>
              <p className="rpt-idle-desc">
                4 AI agents will analyse all {divisionName} KDs and HMIS trends —
                then write a 4–5 page executive report with strategic recommendations.
                Takes ~60–90 seconds.
              </p>
              <div className="rpt-idle-pills">
                <span className="rpt-pill">KD Performance</span>
                <span className="rpt-pill">Gap Analysis</span>
                <span className="rpt-pill">HMIS Trends</span>
                <span className="rpt-pill">Recommendations</span>
              </div>
              <button className="rpt-btn rpt-btn--generate" onClick={generate}>
                Generate Report
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
              </button>
            </div>
          )}

          {/* Loading */}
          {phase === 'loading' && (
            <div className="rpt-loading">
              <div className="rpt-pipeline">
                {STEPS.map((s, i) => {
                  const isDone   = i < stepIdx;
                  const isActive = i === stepIdx;
                  return (
                    <div key={i}>
                      <div className={`rpt-pipeline-row${isDone ? ' rpt-pipeline-row--done' : ''}${isActive ? ' rpt-pipeline-row--active' : ''}`}>
                        <div className="rpt-pipeline-dot">
                          {isDone
                            ? <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00c97a" strokeWidth="3" strokeLinecap="round"><path d="M5 13l4 4L19 7"/></svg>
                            : isActive
                              ? <span className="rpt-pipeline-pulse" />
                              : null
                          }
                        </div>
                        <div className="rpt-pipeline-text">
                          <span className="rpt-pipeline-name">{s.label}</span>
                          <span className="rpt-pipeline-role">{s.role}</span>
                        </div>
                        {isActive && <span className="rpt-pipeline-badge">Running</span>}
                        {isDone   && <span className="rpt-pipeline-badge rpt-pipeline-badge--done">Done</span>}
                      </div>
                      {i < STEPS.length - 1 && (
                        <div className={`rpt-pipeline-line${isDone ? ' rpt-pipeline-line--done' : ''}`} />
                      )}
                    </div>
                  );
                })}
              </div>
              <div className="rpt-progress-bar" style={{ marginTop: 24 }}>
                <div className="rpt-progress-fill" style={{ width: `${step.pct}%` }} />
              </div>
              <p className="rpt-loading-sub">
                Powered by Groq · {step.pct}% complete
              </p>
            </div>
          )}

          {/* Error */}
          {phase === 'error' && (
            <div className="rpt-error">
              <p className="rpt-error-title">Report generation failed</p>
              <p className="rpt-error-msg">{errMsg}</p>
              <p className="rpt-error-hint">
                Ensure <code>GROQ_API_KEY</code> is set in Vercel environment variables.
                Timeout errors require Vercel Pro for 60-second function execution.
              </p>
              <button className="rpt-btn rpt-btn--generate" onClick={() => setPhase('idle')}>
                Try Again
              </button>
            </div>
          )}

          {/* Done — render HTML report */}
          {phase === 'done' && (
            <div className="rpt-report-frame">
              <div className="rpt-success-strip">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00c97a" strokeWidth="2.5" strokeLinecap="round"><path d="M5 13l4 4L19 7"/></svg>
                Report ready — {divisionName} · FY 2025-26
              </div>
              <iframe
                title="Division Report"
                srcDoc={html}
                className="rpt-iframe"
                sandbox="allow-same-origin"
              />
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
