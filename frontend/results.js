function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[character]));
}

function gradePoint(grade) {
  return { 'A+': 10, A: 9, 'A-': 8, 'B+': 7, B: 6, 'B-': 5, C: 4, F: 0 }[grade] ?? null;
}

async function loadResults() {
  const message = document.getElementById('results-message');
  const body = document.getElementById('results-body');
  try {
    const { results } = await apiRequest('results/');
    if (!results.length) {
      body.innerHTML = '<tr><td colspan="5">No published results are available yet.</td></tr>';
      document.getElementById('result-courses').textContent = '0';
      document.getElementById('result-average').textContent = '—';
      document.getElementById('result-gpa').textContent = '—';
      return;
    }
    const totals = results
      .filter(result => result.total_marks !== null && result.total_marks !== '')
      .map(result => Number(result.total_marks))
      .filter(Number.isFinite);
    const points = results.map(result => gradePoint(result.grade)).filter(Number.isFinite);
    document.getElementById('result-courses').textContent = results.length;
    document.getElementById('result-average').textContent = totals.length ? `${(totals.reduce((sum, total) => sum + total, 0) / totals.length).toFixed(1)}%` : '—';
    document.getElementById('result-gpa').textContent = points.length ? (points.reduce((sum, point) => sum + point, 0) / points.length).toFixed(1) : '—';
    body.innerHTML = results.map(result => `
      <tr>
        <td>${escapeHtml(result.course)} — ${escapeHtml(result.exam)}</td>
        <td>${result.internal_marks ?? '—'}</td>
        <td>${result.exam_marks ?? '—'}</td>
        <td>${result.total_marks ?? '—'}</td>
        <td>${escapeHtml(result.grade || '—')}</td>
      </tr>`).join('');
  } catch (error) {
    message.textContent = error.message === 'Authentication required.' ? 'Please log in to view your results.' : error.message;
    body.innerHTML = '<tr><td colspan="5">Unable to load results.</td></tr>';
  }
}

document.addEventListener('DOMContentLoaded', loadResults);
