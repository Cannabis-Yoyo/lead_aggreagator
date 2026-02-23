document.addEventListener('DOMContentLoaded', function () {
    const triggerBtn = document.querySelector('form[action="/trigger-lead"] button');
    if (triggerBtn) {
        triggerBtn.addEventListener('click', function () {
            triggerBtn.textContent = 'Firing...';
            setTimeout(() => triggerBtn.textContent = 'Trigger Lead', 2000);
        });
    }
});