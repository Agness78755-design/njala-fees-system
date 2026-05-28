// ════════════════════════════════════════════════════════════
// AUTH.JS — Authentication & Session Management
// ════════════════════════════════════════════════════════════

const API_URL = 'http://localhost:5000/api';

// ── Tab Switching ──
function switchTab(tab) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  
  document.getElementById(tab + 'Panel').classList.add('active');
  event.target.classList.add('active');
}

// ── Password Toggle ──
function togglePw(inputId, btn) {
  const input = document.getElementById(inputId);
  const isPassword = input.type === 'password';
  input.type = isPassword ? 'text' : 'password';
  btn.innerHTML = `<i class="fas fa-eye${isPassword ? '-slash' : ''}"></i>`;
}

// ── Login Form Handler ──
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const id = document.getElementById('loginId').value.trim();
  const pw = document.getElementById('loginPw').value;
  const alertEl = document.getElementById('loginAlert');
  const btn = document.getElementById('loginBtn');
  
  if (!id || !pw) {
    alertEl.classList.remove('hidden');
    document.getElementById('loginAlertMsg').textContent = 'Please fill all fields.';
    return;
  }

  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Signing in...</span>';
  btn.disabled = true;

  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: id, password: pw })
    });

    const data = await response.json();

    if (response.ok && data.access_token) {
      // Save token
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      // Redirect
      setTimeout(() => {
        window.location.href = 'dashboard.html';
      }, 500);
    } else {
      alertEl.classList.remove('hidden');
      document.getElementById('loginAlertMsg').textContent = data.message || 'Invalid credentials. Please try again.';
      btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> <span>Sign In</span>';
      btn.disabled = false;
    }
  } catch (error) {
    console.error('Login error:', error);
    alertEl.classList.remove('hidden');
    document.getElementById('loginAlertMsg').textContent = 'Connection error. Please try again.';
    btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> <span>Sign In</span>';
    btn.disabled = false;
  }
});

// ── Register Form Handler ──
document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const first = document.getElementById('regFirst').value.trim();
  const last = document.getElementById('regLast').value.trim();
  const studentId = document.getElementById('regStudentId').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const phone = document.getElementById('regPhone').value.trim();
  const faculty = document.getElementById('regFaculty').value;
  const pw = document.getElementById('regPw').value;
  const agree = document.getElementById('agreeTerms').checked;
  const alertEl = document.getElementById('registerAlert');
  const btn = document.getElementById('registerBtn');

  if (!first || !last || !studentId || !email || !phone || !faculty || !pw || !agree) {
    alertEl.classList.remove('hidden');
    document.getElementById('registerAlertMsg').textContent = 'Please fill all fields and agree to terms.';
    return;
  }

  if (pw.length < 8) {
    alertEl.classList.remove('hidden');
    document.getElementById('registerAlertMsg').textContent = 'Password must be at least 8 characters.';
    return;
  }

  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Creating Account...</span>';
  btn.disabled = true;

  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        first_name: first,
        last_name: last,
        student_id: studentId,
        email: email,
        phone: phone,
        faculty: faculty,
        password: pw
      })
    });

    const data = await response.json();

    if (response.ok) {
      alertEl.classList.add('hidden');
      // Auto-login
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      setTimeout(() => {
        window.location.href = 'dashboard.html';
      }, 500);
    } else {
      alertEl.classList.remove('hidden');
      document.getElementById('registerAlertMsg').textContent = data.message || 'Registration failed. Please try again.';
      btn.innerHTML = '<i class="fas fa-user-plus"></i> <span>Create Account</span>';
      btn.disabled = false;
    }
  } catch (error) {
    console.error('Register error:', error);
    alertEl.classList.remove('hidden');
    document.getElementById('registerAlertMsg').textContent = 'Connection error. Please try again.';
    btn.innerHTML = '<i class="fas fa-user-plus"></i> <span>Create Account</span>';
    btn.disabled = false;
  }
});

// ── Check Auth on Protected Pages ──
function checkAuth() {
  const token = localStorage.getItem('access_token');
  const user = localStorage.getItem('user');
  
  // If on dashboard and no auth, redirect to login
  if (!token && (window.location.pathname.includes('dashboard') || window.location.pathname.includes('admin'))) {
    window.location.href = 'login.html';
    return false;
  }
  
  return token && user;
}

// ── Logout ──
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = 'login.html';
}

// ── Get Current User ──
function getCurrentUser() {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
}

// ── Get Auth Header ──
function getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

// ── Initialize Auth State ──
document.addEventListener('DOMContentLoaded', () => {
  const user = getCurrentUser();
  
  if (user && document.getElementById('sidebarName')) {
    // Update sidebar with user info
    document.getElementById('sidebarName').textContent = `${user.first_name} ${user.last_name}`;
    document.getElementById('sidebarRole').textContent = user.student_id;
    document.getElementById('sidebarAvatar').textContent = `${user.first_name[0]}${user.last_name[0]}`;
  }
  
  // Auto-logout if no token
  if (window.location.pathname.includes('dashboard') || window.location.pathname.includes('admin')) {
    checkAuth();
  }
});
