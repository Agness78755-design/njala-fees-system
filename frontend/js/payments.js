// ════════════════════════════════════════════════════════════
// PAYMENTS.JS — Payment Processing & Integration
// ════════════════════════════════════════════════════════════

const API_URL = 'http://localhost:5000/api';

// ── Mobile Money Integration Mock ──
const MOBILE_MONEY = {
  ORANGE: 'orange_money',
  AFRICELL: 'africell_money',
  BANK: 'bank_transfer'
};

// ── Initiate Payment ──
async function initiatePayment(amount, method, phone) {
  try {
    const token = localStorage.getItem('access_token');
    const user = getCurrentUser();

    const response = await fetch(`${API_URL}/payments/initiate`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        amount: parseFloat(amount),
        payment_method: method,
        phone_number: phone,
        student_id: user.id
      })
    });

    const data = await response.json();

    if (response.ok) {
      return {
        success: true,
        transaction_id: data.transaction_id,
        message: data.message
      };
    } else {
      return {
        success: false,
        error: data.message || 'Payment initiation failed'
      };
    }
  } catch (error) {
    console.error('Payment error:', error);
    return {
      success: false,
      error: 'Network error. Please try again.'
    };
  }
}

// ── Verify Payment ──
async function verifyPayment(transactionId) {
  try {
    const response = await fetch(`${API_URL}/payments/verify/${transactionId}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Verification error:', error);
    return { success: false, error: 'Verification failed' };
  }
}

// ── Get Payment History ──
async function getPaymentHistory(limit = 10) {
  try {
    const response = await fetch(`${API_URL}/payments/history?limit=${limit}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    if (response.ok) {
      return await response.json();
    } else {
      console.error('Failed to fetch history');
      return [];
    }
  } catch (error) {
    console.error('History fetch error:', error);
    return [];
  }
}

// ── Get Fee Balance ──
async function getFeeBalance() {
  try {
    const response = await fetch(`${API_URL}/fees/balance`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    if (response.ok) {
      const data = await response.json();
      updateFeeDisplay(data);
      return data;
    }
  } catch (error) {
    console.error('Balance fetch error:', error);
  }
}

// ── Update Fee Display ──
function updateFeeDisplay(data) {
  if (document.getElementById('balanceAmount')) {
    document.getElementById('balanceAmount').textContent = data.outstanding?.toLocaleString() || '0';
    document.getElementById('feeProgressBar').style.width = (data.paid_percentage || 0) + '%';
  }
}

// ── Initialize Payment ──
async function initializePayment() {
  const amount = document.getElementById('modalAmount').value;
  const method = document.getElementById('modalMethod').value;
  const phone = document.getElementById('modalPhone').value;

  if (!amount || !phone) {
    showToast('Please enter amount and phone number', 'error');
    return;
  }

  showToast('Processing payment request...', 'success');

  const result = await initiatePayment(amount, method, phone);

  if (result.success) {
    showToast(`Payment initiated! Transaction ID: ${result.transaction_id}`, 'success');
    
    // Poll for payment confirmation
    pollPaymentStatus(result.transaction_id);
    
    closePayModal();
  } else {
    showToast(result.error || 'Payment failed', 'error');
  }
}

// ── Poll Payment Status ──
function pollPaymentStatus(transactionId, maxAttempts = 30) {
  let attempts = 0;

  const interval = setInterval(async () => {
    attempts++;
    
    const result = await verifyPayment(transactionId);

    if (result.status === 'completed') {
      clearInterval(interval);
      showToast('Payment confirmed! ✓', 'success');
      
      // Refresh balance
      setTimeout(() => {
        getFeeBalance();
        populateHistory();
      }, 500);
    } else if (result.status === 'failed') {
      clearInterval(interval);
      showToast('Payment failed. Please try again.', 'error');
    } else if (attempts >= maxAttempts) {
      clearInterval(interval);
      showToast('Payment verification timeout. Please check your status later.', 'warning');
    }
  }, 2000); // Poll every 2 seconds
}

// ── Download Receipt ──
async function downloadReceiptPDF(transactionId) {
  try {
    const response = await fetch(`${API_URL}/payments/receipt/${transactionId}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `receipt-${transactionId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
      showToast('Receipt downloaded!', 'success');
    } else {
      showToast('Failed to download receipt', 'error');
    }
  } catch (error) {
    console.error('Receipt download error:', error);
    showToast('Error downloading receipt', 'error');
  }
}

// ── Send Payment Reminder SMS ──
async function sendPaymentReminder() {
  try {
    const user = getCurrentUser();
    const response = await fetch(`${API_URL}/payments/send-reminder`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ student_id: user.id })
    });

    if (response.ok) {
      showToast('Payment reminder sent to your phone!', 'success');
    } else {
      showToast('Failed to send reminder', 'error');
    }
  } catch (error) {
    console.error('Reminder error:', error);
    showToast('Error sending reminder', 'error');
  }
}

// ── Validate Payment Amount ──
function validatePaymentAmount(amount, maxAmount) {
  amount = parseFloat(amount);
  maxAmount = parseFloat(maxAmount);

  if (isNaN(amount) || amount <= 0) {
    return { valid: false, error: 'Invalid amount' };
  }

  if (amount > maxAmount) {
    return { valid: false, error: 'Amount exceeds outstanding balance' };
  }

  if (amount < 10000) {
    return { valid: false, error: 'Minimum payment is SLL 10,000' };
  }

  return { valid: true };
}

// ── Format Currency ──
function formatCurrency(num) {
  return 'SLL ' + num?.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }) || '0';
}

// ── Payment Method Selector ──
function selectPaymentMethod(btn, method) {
  document.querySelectorAll('.payment-method-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  
  document.getElementById('selectedMethod').value = method;
  
  const methodInfo = {
    orange: 'Orange Money — USSD: *114*1#',
    africell: 'Africell Money — USSD: *185#',
    bank: 'Bank Transfer — SLCB Account'
  };
  
  if (document.getElementById('methodInfo')) {
    document.getElementById('methodInfo').textContent = methodInfo[method] || '';
  }
}

// ── Initialize on Load ──
document.addEventListener('DOMContentLoaded', () => {
  // Load fee balance
  if (document.getElementById('balanceAmount')) {
    getFeeBalance();
  }

  // Setup payment form
  const payForm = document.querySelector('[id$="paymentForm"]');
  if (payForm) {
    payForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const amount = document.getElementById('paymentAmount')?.value;
      const method = document.getElementById('selectedMethod')?.value;
      const phone = document.getElementById('paymentPhone')?.value;

      const validation = validatePaymentAmount(amount, 1260000);
      if (!validation.valid) {
        showToast(validation.error, 'error');
        return;
      }

      const result = await initiatePayment(amount, method, phone);
      if (result.success) {
        showToast('Payment processing...', 'success');
        pollPaymentStatus(result.transaction_id);
      } else {
        showToast(result.error, 'error');
      }
    });
  }
});

// Export functions for global use
window.initiatePayment = initiatePayment;
window.verifyPayment = verifyPayment;
window.getPaymentHistory = getPaymentHistory;
window.getFeeBalance = getFeeBalance;
window.downloadReceiptPDF = downloadReceiptPDF;
window.sendPaymentReminder = sendPaymentReminder;
window.validatePaymentAmount = validatePaymentAmount;
window.formatCurrency = formatCurrency;
window.selectPaymentMethod = selectPaymentMethod;
window.initializePayment = initializePayment;
