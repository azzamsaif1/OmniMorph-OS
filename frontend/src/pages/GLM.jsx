import { useState, useEffect } from 'react';

export default function GLM() {
  const [status, setStatus] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [evolutionResult, setEvolutionResult] = useState(null);
  const [genesisResult, setGenesisResult] = useState(null);
  const [evolutionForm, setEvolutionForm] = useState({
    task: 'Optimize vector database query performance',
    goal: 'Achieve 6x improvement in QPS',
    max_iterations: 100,
    duration_hours: 1,
  });
  const [genesisForm, setGenesisForm] = useState({
    specification: 'Linux desktop environment with window manager, status bar, VPN manager, and Chinese font support',
    hours: 1,
    max_steps: 200,
  });
  const [loading, setLoading] = useState({ evolution: false, genesis: false });

  useEffect(() => {
    fetch('/api/glm/status').then(r => r.json()).then(setStatus).catch(() => {});
    fetch('/api/glm/comparison').then(r => r.json()).then(setComparison).catch(() => {});
  }, []);

  const startEvolution = async () => {
    setLoading(l => ({ ...l, evolution: true }));
    try {
      const res = await fetch('/api/glm/evolution/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(evolutionForm),
      });
      const data = await res.json();
      setEvolutionResult(data);
    } catch (e) {
      setEvolutionResult({ error: e.message });
    }
    setLoading(l => ({ ...l, evolution: false }));
  };

  const startGenesis = async () => {
    setLoading(l => ({ ...l, genesis: true }));
    try {
      const res = await fetch('/api/glm/genesis/build', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(genesisForm),
      });
      const data = await res.json();
      setGenesisResult(data);
    } catch (e) {
      setGenesisResult({ error: e.message });
    }
    setLoading(l => ({ ...l, genesis: false }));
  };

  return (
    <div style={{ padding: '2rem', maxWidth: 1200, margin: '0 auto' }}>
      <h1 style={{ color: '#cdd6f4', marginBottom: '0.5rem' }}>
        GLM-5.1 Integration
      </h1>
      <p style={{ color: '#a6adc8', marginBottom: '2rem' }}>
        Self-Evolving Engineering System — 744B MoE, 202K context, SWE-Bench Pro 58.4%
      </p>

      {/* Status Banner */}
      {status && (
        <div style={{
          background: '#1e1e2e', border: '1px solid #45475a', borderRadius: 8,
          padding: '1.5rem', marginBottom: '2rem'
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <StatCard
              label="Status"
              value={status.feature_flag ? 'Enabled' : 'Fallback (Gemini)'}
              color={status.feature_flag ? '#a6e3a1' : '#f9e2af'}
            />
            <StatCard label="Context Window" value="202,752 tokens" color="#89b4fa" />
            <StatCard label="SWE-Bench Pro" value="58.4%" color="#cba6f7" />
            <StatCard label="Max Session" value="8 hours" color="#f5c2e7" />
            <StatCard label="Max Iterations" value="655+" color="#94e2d5" />
            <StatCard label="Architecture" value="256 experts, 8 active" color="#fab387" />
          </div>
        </div>
      )}

      {/* Comparison Table */}
      {comparison && (
        <div style={{
          background: '#1e1e2e', border: '1px solid #45475a', borderRadius: 8,
          padding: '1.5rem', marginBottom: '2rem'
        }}>
          <h2 style={{ color: '#cdd6f4', marginBottom: '1rem' }}>
            GLM-5.1 vs Claude Mythos vs GPT-5.4
          </h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', color: '#cdd6f4' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #45475a' }}>
                  <th style={thStyle}>Metric</th>
                  {comparison.models.map(m => (
                    <th key={m.name} style={thStyle}>{m.name.split('(')[0].trim()}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <CompRow label="SWE-Bench Pro" values={comparison.models.map(m => `${m.swe_bench_pro}%`)} highlight={0} />
                <CompRow label="Architecture" values={comparison.models.map(m => m.architecture)} />
                <CompRow label="Context Window" values={comparison.models.map(m => m.context_window.toLocaleString())} highlight={0} />
                <CompRow label="Autonomous Hours" values={comparison.models.map(m => `${m.autonomous_hours}h`)} highlight={0} />
                <CompRow label="Max Iterations" values={comparison.models.map(m => m.max_iterations || '—')} highlight={0} />
                <CompRow label="Self-Evolution" values={comparison.models.map(m => m.self_evolution ? '✓' : '✗')} highlight={0} />
                <CompRow label="Multi-Agent" values={comparison.models.map(m => m.multi_agent ? '✓' : '✗')} highlight={0} />
                <CompRow label="System Building" values={comparison.models.map(m => m.system_building ? '✓' : '✗')} highlight={0} />
                <CompRow label="License" values={comparison.models.map(m => m.license)} highlight={0} />
                <CompRow label="Availability" values={comparison.models.map(m => m.availability)} highlight={0} />
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Self-Evolution Panel */}
      <div style={{
        background: '#1e1e2e', border: '1px solid #45475a', borderRadius: 8,
        padding: '1.5rem', marginBottom: '2rem'
      }}>
        <h2 style={{ color: '#cdd6f4', marginBottom: '1rem' }}>
          Self-Evolving Agent (655+ Iterations)
        </h2>
        <p style={{ color: '#a6adc8', marginBottom: '1rem', fontSize: '0.9rem' }}>
          Inspired by GLM-5.1's ability to sustain 655 iterations and achieve 6.9x improvement
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
          <Input label="Task" value={evolutionForm.task}
            onChange={v => setEvolutionForm(f => ({ ...f, task: v }))} />
          <Input label="Goal" value={evolutionForm.goal}
            onChange={v => setEvolutionForm(f => ({ ...f, goal: v }))} />
          <Input label="Max Iterations" value={evolutionForm.max_iterations} type="number"
            onChange={v => setEvolutionForm(f => ({ ...f, max_iterations: parseInt(v) || 100 }))} />
          <Input label="Duration (hours)" value={evolutionForm.duration_hours} type="number"
            onChange={v => setEvolutionForm(f => ({ ...f, duration_hours: parseFloat(v) || 1 }))} />
        </div>
        <button onClick={startEvolution} disabled={loading.evolution}
          style={btnStyle}>{loading.evolution ? 'Evolving...' : 'Start Evolution'}</button>

        {evolutionResult && !evolutionResult.error && (
          <div style={{ marginTop: '1rem', background: '#181825', borderRadius: 6, padding: '1rem' }}>
            <h3 style={{ color: '#a6e3a1', marginBottom: '0.5rem' }}>Evolution Complete</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
              <MiniStat label="Iterations" value={evolutionResult.total_iterations} />
              <MiniStat label="Tool Calls" value={evolutionResult.total_tool_calls} />
              <MiniStat label="Duration" value={`${evolutionResult.metrics?.duration_hours?.toFixed(3)}h`} />
              <MiniStat label="Initial Score" value={evolutionResult.metrics?.initial_score?.toFixed(3)} />
              <MiniStat label="Final Score" value={evolutionResult.metrics?.final_score?.toFixed(3)} />
              <MiniStat label="Improvement" value={`${evolutionResult.metrics?.total_improvement?.toFixed(3)}`} />
              <MiniStat label="Success Rate"
                value={`${((evolutionResult.metrics?.successful_experiments / Math.max(evolutionResult.metrics?.experiments_run, 1)) * 100).toFixed(1)}%`} />
              <MiniStat label="Peak Score" value={evolutionResult.metrics?.peak_score?.toFixed(3)} />
              <MiniStat label="Goal Reached" value={evolutionResult.success ? 'Yes' : 'No'} />
            </div>
          </div>
        )}
      </div>

      {/* System Genesis Panel */}
      <div style={{
        background: '#1e1e2e', border: '1px solid #45475a', borderRadius: 8,
        padding: '1.5rem', marginBottom: '2rem'
      }}>
        <h2 style={{ color: '#cdd6f4', marginBottom: '1rem' }}>
          System Genesis Engine (Build Complete Systems)
        </h2>
        <p style={{ color: '#a6adc8', marginBottom: '1rem', fontSize: '0.9rem' }}>
          Build complete systems from specification — 1,200+ steps, 4.8MB output, equivalent to 4-person team
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
          <Input label="Specification" value={genesisForm.specification}
            onChange={v => setGenesisForm(f => ({ ...f, specification: v }))} />
          <Input label="Hours" value={genesisForm.hours} type="number"
            onChange={v => setGenesisForm(f => ({ ...f, hours: parseFloat(v) || 1 }))} />
          <Input label="Max Steps" value={genesisForm.max_steps} type="number"
            onChange={v => setGenesisForm(f => ({ ...f, max_steps: parseInt(v) || 200 }))} />
        </div>
        <button onClick={startGenesis} disabled={loading.genesis}
          style={btnStyle}>{loading.genesis ? 'Building...' : 'Build System'}</button>

        {genesisResult && !genesisResult.error && (
          <div style={{ marginTop: '1rem', background: '#181825', borderRadius: 6, padding: '1rem' }}>
            <h3 style={{ color: '#a6e3a1', marginBottom: '0.5rem' }}>Build Complete</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', marginBottom: '1rem' }}>
              <MiniStat label="Steps" value={genesisResult.metrics?.total_steps} />
              <MiniStat label="Components" value={genesisResult.metrics?.components_built} />
              <MiniStat label="Files Created" value={genesisResult.metrics?.files_created} />
              <MiniStat label="Size" value={`${genesisResult.metrics?.total_size_mb?.toFixed(2)} MB`} />
              <MiniStat label="Coverage" value={`${genesisResult.metrics?.test_coverage?.toFixed(1)}%`} />
              <MiniStat label="Deploy Ready" value={genesisResult.deployment_ready ? 'Yes' : 'No'} />
            </div>
            <h4 style={{ color: '#89b4fa', marginBottom: '0.5rem' }}>Components Built</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {genesisResult.components?.map((c, i) => (
                <span key={i} style={{
                  background: '#313244', padding: '0.25rem 0.75rem', borderRadius: 12,
                  color: '#cdd6f4', fontSize: '0.85rem'
                }}>
                  {c.name} ({c.type})
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Capabilities */}
      {status && (
        <div style={{
          background: '#1e1e2e', border: '1px solid #45475a', borderRadius: 8,
          padding: '1.5rem'
        }}>
          <h2 style={{ color: '#cdd6f4', marginBottom: '1rem' }}>Capabilities</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
            <CapCard title="8-Hour Autonomous Work" desc="Complete entire projects overnight — equivalent to 4-person team's week" />
            <CapCard title="655+ Iteration Self-Evolution" desc="Continuous improvement without human intervention — 6.9x demonstrated" />
            <CapCard title="System Building from Spec" desc="Build complete Linux Desktop in 8 hours (1,200 steps, 4.8MB)" />
            <CapCard title="202,752 Token Context" desc="World-leading context window for complex reasoning and planning" />
            <CapCard title="Tool Calling (6,000+)" desc="Multi-step task execution with thousands of tool interactions" />
            <CapCard title="Thinking Mode" desc="Step-by-step reasoning before output for higher accuracy" />
            <CapCard title="vLLM + SGLang Backends" desc="Dynamic switching: vLLM for heavy tasks, SGLang for real-time" />
            <CapCard title="MIT Open Source" desc="Full commercial use, modification, and redistribution" />
          </div>
        </div>
      )}
    </div>
  );
}

// --- Sub-components ---

function StatCard({ label, value, color = '#cdd6f4' }) {
  return (
    <div style={{ background: '#181825', borderRadius: 6, padding: '0.75rem' }}>
      <div style={{ color: '#a6adc8', fontSize: '0.75rem', marginBottom: '0.25rem' }}>{label}</div>
      <div style={{ color, fontSize: '1.1rem', fontWeight: 600 }}>{value}</div>
    </div>
  );
}

function MiniStat({ label, value }) {
  return (
    <div style={{ padding: '0.25rem' }}>
      <span style={{ color: '#a6adc8', fontSize: '0.75rem' }}>{label}: </span>
      <span style={{ color: '#cdd6f4', fontWeight: 500 }}>{value}</span>
    </div>
  );
}

function CapCard({ title, desc }) {
  return (
    <div style={{ background: '#181825', borderRadius: 6, padding: '1rem' }}>
      <div style={{ color: '#89b4fa', fontWeight: 600, marginBottom: '0.25rem' }}>{title}</div>
      <div style={{ color: '#a6adc8', fontSize: '0.85rem' }}>{desc}</div>
    </div>
  );
}

function CompRow({ label, values, highlight }) {
  return (
    <tr style={{ borderBottom: '1px solid #313244' }}>
      <td style={tdStyle}>{label}</td>
      {values.map((v, i) => (
        <td key={i} style={{ ...tdStyle, color: i === highlight ? '#a6e3a1' : '#cdd6f4' }}>{v}</td>
      ))}
    </tr>
  );
}

function Input({ label, value, onChange, type = 'text' }) {
  return (
    <div>
      <label style={{ color: '#a6adc8', fontSize: '0.8rem', display: 'block', marginBottom: '0.25rem' }}>{label}</label>
      <input type={type} value={value} onChange={e => onChange(e.target.value)}
        style={{
          width: '100%', background: '#181825', border: '1px solid #45475a',
          borderRadius: 4, padding: '0.5rem', color: '#cdd6f4', fontSize: '0.9rem'
        }}
      />
    </div>
  );
}

const thStyle = { textAlign: 'left', padding: '0.75rem 0.5rem', color: '#89b4fa', fontSize: '0.85rem' };
const tdStyle = { padding: '0.5rem', fontSize: '0.85rem' };
const btnStyle = {
  background: '#89b4fa', color: '#1e1e2e', border: 'none', borderRadius: 6,
  padding: '0.6rem 1.5rem', fontWeight: 600, cursor: 'pointer', fontSize: '0.9rem'
};
