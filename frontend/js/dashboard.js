// ════════════════════════════════════════════════════════════
// DASHBOARD.JS — Dashboard Page Logic
// ════════════════════════════════════════════════════════════

const API_URL = 'http://localhost:5000/api';

// ── Page Navigation ──
function showPage(pageId) {
  // Hide all pages
  document.querySelectorAll('[id^="page-"]').forEach(p => p.style.display = 'none');
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  
  // Show selected page
  const page = document.getElementById('page-' + pageId);
  if (page) {
    page.style.display = 'block';
    page.classList.add('animate-fadeup');
    
    // Update topbar
    const titles = {
      dashboard: 'Overview',
      fees: 'My Fees',
      payments: 'Make Payment',
      history: 'Payment History',
      receipts: 'My Receipts',
      profile: 'My Profile',
      notif: 'Notifications',
      settings: 'Settings'
    };
    document.getElementById('topbarTitle').textContent = titles[pageId] || 'Page';
    
    // Mark nav item active
    const navItem = document.getElementById('nav-' + pageId);
    if (navItem) navItem.classList.add('active');
    
    // Populate data if needed
    if (pageId === 'history') populateHistory();
    if (pageId === 'profile') initProfile();
  }
}

// ── Fee Tabs ──
function switchFeeTab(tab, btn) {
  document.querySelectorAll('[id^="fee-"]').forEach(f => f.style.display = 'none');
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  
  document.getElementById('fee-' + tab).style.display = 'block';
  btn.classList.add('active');
}

// ── Populate Payment Chart ──
function populatePaymentChart() {
  const chart = document.getElementById('paymentChart');
  const labels = document.getElementById('chartLabels');
  const months = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'];
  const paid = [450, 380, 520, 600, 700, 850, 940];
  const pending = [100, 150, 80, 120, 90, 60, 50];
  const maxVal = Math.max(...paid.map((v, i) => v + pending[i]));

  months.forEach((m, i) => {
    const col = document.createElement('div');
    col.className = 'bar-col';
    
    const paidBar = document.createElement('div');
    paidBar.className = 'bar-fill';
    paidBar.style.height = (paid[i] / maxVal * 100) + '%';
    paidBar.innerHTML = `<span class="tip">${paid[i]}</span>`;
    
    const pendingBar = document.createElement('div');
    pendingBar.className = 'bar-fill gold';
    pendingBar.style.height = (pending[i] / maxVal * 100) + '%';
    
    col.appendChild(paidBar);
    col.appendChild(pendingBar);
    
    const label = document.createElement('div');
    label.className = 'bar-label';
    label.textContent = m;
    col.appendChild(label);
    
    chart.appendChild(col);
  });

  labels.innerHTML = months.map(m => `<span style="flex:1;text-align:center;font-size:0.7rem;color:var(--gray-400)">${m}</span>`).join('');
}

// ── Populate Recent Transactions ──
function populateRecentTransactions() {
  const txList = document.getElementById('txList');
  const transactions = [
    { icon: 'paid', name: 'Tuition Fee Payment', date: '10 Sep 2024', amount: '1,500,000' },
    { icon: 'paid', name: 'Accommodation Fee', date: '05 Sep 2024', amount: '400,000' },
    { icon: 'paid', name: 'Lab Fees', date: '01 Sep 2024', amount: '150,000' },
    { icon: 'pending', name: 'Exam Fees (Pending)', date: 'Due: 31 Mar 2025', amount: '100,000' },
  ];

  txList.innerHTML = transactions.map(tx => `
    <div class="tx-item">
      <div class="tx-icon ${tx.icon}">
        ${tx.icon === 'paid' ? '<i class="fas fa-check-circle"></i>' : '<i class="fas fa-clock"></i>'}
      </div>
      <div class="tx-info">
        <div class="tx-name">${tx.name}</div>
        <div class="tx-meta">${tx.date}</div>
      </div>
      <div class="tx-amount">
        <div class="amount">SLL ${tx.amount}</div>
      </div>
    </div>
  `).join('');
}

// ── Populate History Table ──
function populateHistory() {
  const tbody = document.getElementById('historyTbody');
  const history = [
    ['TXN-2024-0142', 'Tuition Fee', 'Orange Money', '1,500,000', '10 Sep 2024', 'Paid', 'Receipt'],
    ['TXN-2024-0128', 'Accommodation', 'Africell Money', '400,000', '05 Sep 2024', 'Paid', 'Receipt'],
    ['TXN-2024-0115', 'Lab Fees', 'Bank Transfer', '150,000', '01 Sep 2024', 'Paid', 'Receipt'],
    ['TXN-2024-0089', 'Registration Fee', 'Orange Money', '100,000', '28 Aug 2024', 'Paid', 'Receipt'],
  ];

  tbody.innerHTML = history.map(h => `
    <tr>
      <td class="td-mono">${h[0]}</td>
      <td>${h[1]}</td>
      <td><span class="badge badge-gray">${h[2]}</span></td>
      <td class="td-mono"><strong>SLL ${h[3]}</strong></td>
      <td style="font-size:0.8rem;color:var(--gray-400)">${h[4]}</td>
      <td><span class="badge badge-green badge-dot">${h[5]}</span></td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="downloadReceipt('${h[0]}')">
          <i class="fas fa-download"></i> ${h[6]}
        </button>
      </td>
    </tr>
  `).join('');
}

// ── Download Receipt ──
function downloadReceipt(refNo) {
  showToast(`Receipt ${refNo} download started.`, 'success');
  // In real app, fetch PDF from backend
}

// ── Edit Profile ──
function toggleEditProfile() {
  const btn = document.getElementById('editProfileBtn');
  const inputs = ['pFirst', 'pLast', 'pEmail', 'pPhone'];
  const isEditing = inputs[0] && !document.getElementById(inputs[0]).disabled;
  
  inputs.forEach(id => {
    if (document.getElementById(id)) {
      document.getElementById(id).disabled = isEditing;
    }
  });
  
  if (isEditing) {
    btn.innerHTML = '<i class="fas fa-edit"></i> Edit Profile';
    document.getElementById('saveProfileBtn').style.display = 'none';
  } else {
    btn.innerHTML = '<i class="fas fa-times"></i> Cancel';
    document.getElementById('saveProfileBtn').style.display = 'block';
  }
}

// ── Save Profile ──
function saveProfile() {
  const data = {
    first_name: document.getElementById('pFirst').value,
    last_name: document.getElementById('pLast').value,
    email: document.getElementById('pEmail').value,
    phone: document.getElementById('pPhone').value
  };
  
  // Simulate save
  showToast('Profile updated successfully!', 'success');
  toggleEditProfile();
}

// ── Payment Page Interactions ──
function selectPaymentMethod(element) {
  const payMethods = document.querySelectorAll('.pay-method');
  payMethods.forEach(pm => pm.classList.remove('selected'));
  element.classList.add('selected');
  
  const method = element.getAttribute('data-method') || element.querySelector('.pay-method-info .name').textContent;
  document.getElementById('summaryMethod').textContent = method;
}

document.getElementById('payFeeCategory')?.addEventListener('change', (e) => {
  const val = e.target.value;
  const customGroup = document.getElementById('customAmountGroup');
  
  if (val === 'custom') {
    customGroup.style.display = 'block';
  } else {
    customGroup.style.display = 'none';
    if (val) {
      const amount = val.match(/\d+/)?.[0] || val;
      updatePaymentSummary(e.target.options[e.target.selectedIndex].text.split('—')[1]?.trim() || val, val);
    }
  }
});

function updatePaymentSummary(label, amount) {
  document.getElementById('summaryCategory').textContent = label.split('—')[0]?.trim() || label;
  document.getElementById('summaryAmount').textContent = amount ? `SLL ${amount}` : 'SLL —';
  document.getElementById('summaryTotal').textContent = amount ? `SLL ${amount}` : 'SLL —';
}

function selectMethod(el, method) {
  document.querySelectorAll('.pay-method').forEach(m => m.classList.remove('selected'));
  el.classList.add('selected');
  document.getElementById('summaryMethod').textContent = el.querySelector('.pay-method-info .name').textContent;
}

function processPayment() {
  const amount = document.getElementById('customAmount')?.value || document.getElementById('payFeeCategory').value;
  const method = document.querySelector('.pay-method.selected .pay-method-info .name')?.textContent;
  const phone = document.getElementById('payPhone').value;

  if (!amount || !method || !phone) {
    showToast('Please fill all payment fields.', 'error');
    return;
  }

  showToast('Processing payment of SLL ' + amount + '...', 'success');
  // Simulate payment
  setTimeout(() => {
    showToast('Payment initiated. Check your phone for prompt.', 'success');
  }, 1500);
}

// ── Modal Interactions ──
function openPayModal() {
  document.getElementById('payModal').classList.add('open');
}

function closePayModal() {
  document.getElementById('payModal').classList.remove('open');
}

function submitModalPayment() {
  const amount = document.getElementById('modalAmount').value;
  const method = document.getElementById('modalMethod').value;
  const phone = document.getElementById('modalPhone').value;

  if (!amount || !phone) {
    showToast('Please fill all fields.', 'error');
    return;
  }

  showToast(`Payment of SLL ${amount} via ${method} initiated to ${phone}.`, 'success');
  closePayModal();
}

// ── Toast Notification ──
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  const icons = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle'
  };
  
  toast.innerHTML = `<i class="fas ${icons[type]}"></i> ${message}`;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'toastIn 0.3s ease reverse';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ── Initialize on Load ──
document.addEventListener('DOMContentLoaded', () => {
  checkAuth();
  populatePaymentChart();
  populateRecentTransactions();
  
  // Hide all pages except dashboard
  document.querySelectorAll('[id^="page-"]').forEach(p => {
    if (p.id !== 'page-dashboard') p.style.display = 'none';
  });
  
  // Close modals on background click
  document.getElementById('payModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'payModal') closePayModal();
  });
});
