document.addEventListener('DOMContentLoaded', () => {
  const health = document.querySelector('[data-health]');
  if (health) fetch('/api/health').then(r => r.json()).then(d => health.textContent = d.status);
});
