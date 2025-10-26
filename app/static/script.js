// Enhanced frontend logic with theme toggle, copy/download, spinner, and richer formatting

function formatQuestions(data) {
  const lines = [];
  lines.push(`LANGUAGE: ${data.language?.toUpperCase?.() || 'UNKNOWN'}`);
  lines.push('='.repeat(60));
  lines.push('');

  const section = (title) => { lines.push(title); lines.push('-'.repeat(32)); };

  if (data.questions?.cloze?.length) {
    section('CLOZE');
    data.questions.cloze.forEach((q,i) => {
      lines.push(`${i+1}. ${q.question}`);
      lines.push(`   Answer: ${q.answer}`);
      lines.push('');
    });
  }
  if (data.questions?.short_answer?.length) {
    section('SHORT ANSWER');
    data.questions.short_answer.forEach((q,i)=>{
      lines.push(`${i+1}. ${q.question}`); lines.push('');
    });
  }
  if (data.questions?.mcq?.length) {
    section('MULTIPLE CHOICE');
    data.questions.mcq.forEach((q,i)=>{
      lines.push(`${i+1}. ${q.question}`);
      (q.choices||[]).forEach((c,j)=> lines.push(`   ${String.fromCharCode(65+j)}. ${c}`));
      lines.push(`   Correct: ${q.answer}`);
      lines.push('');
    });
  }
  if (data.evaluation) {
    section('EVALUATION');
    Object.entries(data.evaluation).forEach(([k,v]) => lines.push(`${k}: ${(v*100).toFixed(1)}%`));
    lines.push('');
  }
  if (data.counts) {
    section('COUNTS');
    Object.entries(data.counts).forEach(([k,v]) => lines.push(`${k}: ${v}`));
  }
  return lines.join('\n');
}

// UI helpers
const qs = (sel) => document.querySelector(sel);
const outputEl = qs('#output');
const spinnerEl = qs('#spinner');
const statusEl = qs('#status');
const langBadge = qs('#langDetected');

function setStatus(state, msg) {
  statusEl.className = `status ${state}`;
  statusEl.textContent = msg;
}

function showSpinner(show) { spinnerEl?.classList.toggle('hidden', !show); }

async function generate() {
  const text = qs('#inputText').value;
  const count = parseInt(qs('#count').value, 10) || 5;
  const lang = qs('#lang').value.trim() || null;
  const outputFormat = qs('#outputFormat').value;
  const targets = [];
  if (qs('#mcq').checked) targets.push('mcq');
  if (qs('#cloze').checked) targets.push('cloze');
  if (qs('#short').checked) targets.push('short_answer');

  if (!text.trim()) { outputEl.textContent = 'Please add input text.'; return; }
  if (!targets.length) { outputEl.textContent = 'Select at least one question type.'; return; }

  setStatus('busy','Generating');
  showSpinner(true);
  outputEl.textContent = '';

  try {
    const res = await fetch('/api/generate', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ text, targets, num_questions: count, language_hint: lang, output_format: outputFormat })
    });
    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || res.status);
    }
    if (outputFormat === 'text') {
      const txt = await res.text();
      outputEl.textContent = txt;
      // Try detect language from first line
      const first = txt.split('\n')[0];
      if (first.startsWith('LANGUAGE:')) langBadge.textContent = first.trim();
    } else {
      const data = await res.json();
      outputEl.textContent = formatQuestions(data);
      if (data.language) langBadge.textContent = 'Language: ' + data.language.toUpperCase();
    }
    setStatus('ok','Done');
    setTimeout(()=> setStatus('idle','Idle'), 2500);
  } catch (e) {
    console.error(e);
    outputEl.textContent = 'Error: ' + e.message;
    setStatus('error','Error');
  } finally {
    showSpinner(false);
  }
}

// Copy & download
function copyOutput() {
  const txt = outputEl.textContent || '';
  navigator.clipboard.writeText(txt).then(()=>{
    setStatus('ok','Copied');
    setTimeout(()=> setStatus('idle','Idle'), 1800);
  }).catch(()=> setStatus('error','Copy Failed'));
}

function downloadOutput() {
  const blob = new Blob([outputEl.textContent||''], {type:'text/plain'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'questions.txt';
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
  setStatus('ok','Downloaded');
  setTimeout(()=> setStatus('idle','Idle'), 1800);
}

// Theme toggle
function toggleTheme() {
  const dark = document.body.classList.toggle('dark');
  localStorage.setItem('theme', dark ? 'dark' : 'light');
  const btn = document.getElementById('themeToggle');
  if (btn) btn.textContent = dark ? '☀️' : '🌙';
}

function initTheme() {
  const saved = localStorage.getItem('theme');
  const prefers = window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (saved === 'dark' || (!saved && prefers)) document.body.classList.add('dark');
  const btn = document.getElementById('themeToggle');
  if (btn && document.body.classList.contains('dark')) btn.textContent = '☀️';
}

// Event wiring
window.addEventListener('DOMContentLoaded', () => {
  initTheme();
  qs('#generate').addEventListener('click', generate);
  qs('#copyOutput').addEventListener('click', copyOutput);
  qs('#downloadOutput').addEventListener('click', downloadOutput);
  qs('#themeToggle').addEventListener('click', toggleTheme);
  qs('#clearInput').addEventListener('click', () => { qs('#inputText').value=''; qs('#inputText').focus(); });
  const yearEl = document.getElementById('year'); if (yearEl) yearEl.textContent = new Date().getFullYear();
  setStatus('idle','Idle');
  statusEl.classList.add('idle');
});

console.log('Frontend loaded.');