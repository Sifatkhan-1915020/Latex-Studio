// Auth Manager & Global Toast Helper

function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const iconName = type === 'success' ? 'check-circle' : (type === 'error' ? 'alert-triangle' : 'info');
  toast.innerHTML = `
    <i data-lucide="${iconName}" style="width: 18px; height: 18px; flex-shrink: 0;"></i>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  if (window.lucide) lucide.createIcons();

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px) scale(0.9)';
    toast.style.transition = 'all 0.25s ease';
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}

// Register Form Handler
async function handleRegister(e) {
  e.preventDefault();
  const form = e.target;
  const username = form.username.value.trim();
  const email = form.email.value.trim();
  const full_name = form.full_name ? form.full_name.value.trim() : '';
  const password = form.password.value;
  const confirm = form.confirm_password ? form.confirm_password.value : password;

  if (password !== confirm) {
    showToast('Passwords do not match', 'error');
    return;
  }

  const btn = form.querySelector('button[type="submit"]');
  const origText = btn.innerHTML;
  btn.innerHTML = '<div class="spinner"></div> Creating account...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password, full_name })
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || 'Registration failed');
    }

    showToast('Account created successfully! Redirecting...', 'success');
    setTimeout(() => {
      window.location.href = '/dashboard';
    }, 800);
  } catch (err) {
    showToast(err.message, 'error');
    btn.innerHTML = origText;
    btn.disabled = false;
  }
}

// Login Form Handler
async function handleLogin(e) {
  e.preventDefault();
  const form = e.target;
  const username_or_email = form.username_or_email.value.trim();
  const password = form.password.value;

  const btn = form.querySelector('button[type="submit"]');
  const origText = btn.innerHTML;
  btn.innerHTML = '<div class="spinner"></div> Signing in...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username_or_email, password })
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || 'Login failed');
    }

    showToast('Welcome back! Redirecting...', 'success');
    const urlParams = new URLSearchParams(window.location.search);
    const nextUrl = urlParams.get('next') || '/dashboard';
    setTimeout(() => {
      window.location.href = nextUrl;
    }, 600);
  } catch (err) {
    showToast(err.message, 'error');
    btn.innerHTML = origText;
    btn.disabled = false;
  }
}

// Logout Handler
async function handleLogout() {
  try {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/login';
  } catch (err) {
    window.location.href = '/login';
  }
}
