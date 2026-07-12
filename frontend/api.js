const dashboardForRole = {
  student: 'studentDashboard.html',
  lecturer: 'lecturerDashboard.html',
  admin: 'adminDashboard.html',
};

async function apiRequest(path, options = {}) {
  const response = await fetch(`/api/${path}`, {
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || 'Something went wrong.');
  return body;
}

function showAuthMessage(message, isError = true) {
  const element = document.getElementById('auth-message');
  if (element) {
    element.textContent = message;
    element.style.color = isError ? '#ffd1d1' : '#d4ffd4';
  }
}

async function populateCurrentUser() {
  const nameElements = document.querySelectorAll('[data-current-user]');
  if (!nameElements.length) return;
  try {
    const { user } = await apiRequest('me/');
    nameElements.forEach(element => { element.textContent = user.name; });
  } catch (_) {
    // Keep the existing label if this is a public or signed-out page.
  }
}

document.addEventListener('DOMContentLoaded', populateCurrentUser);
