const API_BASE = 'http://127.0.0.1:8000/api/';
const dashboardForRole = { STUDENT: 'studentDashboard.html', LECTURER: 'lecturerDashboard.html', ADMIN: 'adminDashboard.html' };

async function apiRequest(path, options = {}) {
  const headers = { ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }), ...(options.headers || {}) };
  const token = localStorage.getItem('access_token');
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(Object.values(body).flat().join(' ') || body.detail || 'Request failed.');
  return body;
}

const text = value => String(value ?? '—').replace(/[&<>'"]/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;' }[c]));
const dateTime = exam => `${exam.exam_date} ${exam.start_time}`;
function rows(items, markup, columns, empty = 'No records are available yet.') { return items.length ? items.map(markup).join('') : `<tr><td colspan="${columns}">${empty}</td></tr>`; }

async function currentUser() {
  const user = await apiRequest('profile/');
  document.querySelectorAll('[data-current-user]').forEach(node => node.textContent = `${user.first_name || ''} ${user.last_name || user.username}`.trim());
  return user;
}

async function renderPage() {
  const page = decodeURIComponent(location.pathname.split('/').pop()).toLowerCase();
  if (!['studentdashboard.html','my exams.html','results.html','notifications.html','profile.html','lecturerdashboard.html','lecturerexams.html','lecturergrading.html','lecturernotifications.html','lecturerprofile.html','admindashboard.html'].includes(page)) return;
  try {
    const user = await currentUser();
    if (page.includes('dashboard')) {
      const data = await apiRequest('dashboard/');
      const cards = Object.entries(data).map(([label, value]) => `<article class="portal-card"><p>${text(label.replaceAll('_',' '))}</p><strong>${text(value)}</strong></article>`).join('');
      const container = document.querySelector('.portal-cards, .dashboardcontent'); if (container) container.innerHTML = cards;
    }
    if (page === 'lecturerexams.html' || page === 'my exams.html') {
      const exams = await apiRequest('exams/');
      const body = document.querySelector('tbody');
      if (body) body.innerHTML = page === 'my exams.html'
        ? rows(exams, e => `<tr><td>${text(e.course_name)}</td><td>${text(dateTime(e))}</td><td>—</td><td>${text(e.duration)} minutes</td><td><span class="student-status">${text(e.status)}</span></td></tr>`, 5)
        : rows(exams, e => `<tr><td>${text(e.title)}</td><td>${text(dateTime(e))}</td><td>${text(e.course_name)}</td><td><span class="portal-badge">${text(e.status)}</span></td></tr>`, 4);
      const instructions = document.querySelector('[data-exam-instructions]');
      if (instructions) instructions.textContent = exams[0]?.instructions || 'No examination instructions have been published yet.';
    }
    if (page === 'admindashboard.html') {
      const exams = await apiRequest('exams/'); const body = document.querySelector('tbody');
      if (body) body.innerHTML = rows(exams, e => `<tr><td>${text(e.title)}</td><td>${text(e.course)}</td><td>${text(e.exam_date)}</td><td><span class="portal-badge">${text(e.status)}</span></td></tr>`, 4);
    }
    if (page === 'lecturerdashboard.html') {
      const exams = await apiRequest('exams/'); const list = document.querySelector('.portal-list');
      if (list) list.innerHTML = exams.length ? exams.map(e => `<li><strong>${text(e.title)}</strong><small>${text(dateTime(e))} · ${text(e.duration)} minutes · ${text(e.status)}</small></li>`).join('') : '<li>No upcoming examinations.</li>';
    }
    if (page === 'lecturergrading.html') {
      const attempts = await apiRequest('student-exams/'); const body = document.querySelector('tbody');
      if (body) body.innerHTML = rows(attempts.filter(a => a.status !== 'IN_PROGRESS'), a => `<tr><td>${text(a.student_name)}</td><td>${text(a.exam_title)}</td><td>${text(a.submitted_at)}</td><td><a class="portal-button" href="lecturerGrading.html?attempt=${a.id}">Grade</a></td></tr>`, 4, 'No submitted examinations are awaiting review.');
    }
    if (page.includes('result')) {
      const results = await apiRequest('results/'); const body = document.querySelector('#results-body, tbody');
      if (body) body.innerHTML = rows(results, r => `<tr><td>${text(r.course_name || r.exam_title)}</td><td>${text(r.total_marks)}</td><td>${text(r.percentage)}%</td><td>${text(r.grade)}</td><td>${r.passed ? 'Pass' : 'Fail'}</td></tr>`, 5, 'No published results are available yet.');
    }
    if (page.includes('notification')) {
      const notices = await apiRequest('notifications/'); const list = document.querySelector('.portal-list, .student-panel');
      if (list) list.innerHTML = notices.length ? notices.map(n => `<li><strong>${text(n.title)}</strong><small>${text(n.message)}</small></li>`).join('') : '<p>No notifications yet.</p>';
    }
    if (page.includes('profile')) {
      const table = document.querySelector('table tbody');
      if (table) table.innerHTML = [['Username',user.username],['Email',user.email],['Role',user.role],['Registration number',user.registration_number],['Staff number',user.staff_number],['Phone',user.phone]].filter(([,v]) => v).map(([k,v]) => `<tr><th>${k}</th><td>${text(v)}</td></tr>`).join('');
    }
  } catch (error) { console.error(error); document.querySelectorAll('[data-current-user]').forEach(node => node.textContent = 'Sign in required'); }
}
document.addEventListener('DOMContentLoaded', renderPage);
