// MedStock PRO — Enterprise Healthcare SaaS Dashboard Interactive Controller

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Navigation Drawer Toggle
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
    const appSidebar = document.getElementById('appSidebar');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');

    function openSidebar() {
        if (appSidebar) appSidebar.classList.add('sidebar-open');
        if (sidebarBackdrop) sidebarBackdrop.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        if (appSidebar) appSidebar.classList.remove('sidebar-open');
        if (sidebarBackdrop) sidebarBackdrop.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', openSidebar);
    }
    if (sidebarCloseBtn) {
        sidebarCloseBtn.addEventListener('click', closeSidebar);
    }
    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener('click', closeSidebar);
    }

    // 2. Global Keyboard Shortcut for Search (Cmd + K or Ctrl + K)
    const headerSearchInput = document.getElementById('globalSearchInput');
    window.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            if (headerSearchInput) {
                headerSearchInput.focus();
                headerSearchInput.select();
            }
        }
    });

    // 3. Fast In-Memory Search for Medicine Tables
    const tableSearchInput = document.getElementById('tableSearchInput') || headerSearchInput;
    const targetTable = document.getElementById('medicinesTable');

    if (tableSearchInput && targetTable) {
        tableSearchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const rows = targetTable.querySelectorAll('tbody tr');
            let matchCount = 0;

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = '';
                    matchCount++;
                } else {
                    row.style.display = 'none';
                }
            });

            const emptyNotice = document.getElementById('clientEmptyState');
            if (emptyNotice) {
                emptyNotice.style.display = (matchCount === 0 && rows.length > 0) ? 'block' : 'none';
            }
        });
    }

    // 4. Auto-dismiss Flash Alert Messages
    const alertElements = document.querySelectorAll('.alert-dismissible');
    alertElements.forEach(alertEl => {
        setTimeout(() => {
            if (window.bootstrap && bootstrap.Alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
                if (bsAlert) bsAlert.close();
            } else {
                alertEl.style.transition = 'opacity 0.4s ease';
                alertEl.style.opacity = '0';
                setTimeout(() => alertEl.remove(), 400);
            }
        }, 6000);
    });

    // 5. Date Sequence Integrity Helper (mfg_date < expiry_date)
    const mfgInput = document.querySelector('input[name="mfg_date"]');
    const expInput = document.querySelector('input[name="expiry_date"]');

    if (mfgInput && expInput) {
        mfgInput.addEventListener('change', () => {
            if (mfgInput.value) {
                expInput.min = mfgInput.value;
            }
        });

        expInput.addEventListener('change', () => {
            if (mfgInput.value && expInput.value && expInput.value <= mfgInput.value) {
                alert('Safety Warning: Expiry date must chronologically succeed the manufacturing date.');
            }
        });
    }
});
