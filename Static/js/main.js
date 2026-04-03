// ─── MODAL HELPERS ───────────────────────────

function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('show');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('show');
}

// Close modals on Escape key
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.show')
      .forEach(m => m.classList.remove('show'));
  }
});

// ─── TOPBAR DATE ─────────────────────────────

function updateDate() {
  const el = document.getElementById('currentDate');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleDateString('en-IN', {
    weekday: 'short', day: '2-digit', month: 'short', year: 'numeric'
  });
}
updateDate();

// ─── AUTO-DISMISS FLASH MESSAGES ─────────────

document.querySelectorAll('.flash').forEach(flash => {
  setTimeout(() => {
    flash.style.transition = 'opacity 0.4s, transform 0.4s';
    flash.style.opacity = '0';
    flash.style.transform = 'translateY(-8px)';
    setTimeout(() => flash.remove(), 400);
  }, 3500);
});

// ─── ANIMATE STAT VALUES ──────────────────────

function animateNumber(el) {
  const raw = el.textContent.replace(/[^0-9]/g, '');
  const target = parseInt(raw);
  if (!target || target > 99999) return;
  const prefix = el.textContent.includes('₹') ? '₹' : '';
  let current = 0;
  const step = Math.ceil(target / 40);
  const interval = setInterval(() => {
    current = Math.min(current + step, target);
    el.textContent = prefix + current.toLocaleString('en-IN');
    if (current >= target) clearInterval(interval);
  }, 20);
}

document.querySelectorAll('.stat-value').forEach(animateNumber);
