// MedStock PRO — Interactive Pharmacy Inventory Client Script

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });

    // 2. Client-side fast search filter for inventory table if present
    const searchInput = document.querySelector('input[name="search"]');
    const table = document.getElementById('medicinesTable');

    if (searchInput && table) {
        searchInput.addEventListener('input', (e) => {
            const filter = e.target.value.toLowerCase().trim();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(filter)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // 3. Date validation helper for Add / Edit medicine forms
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
                alert('Warning: Expiry date must be after manufacturing date.');
            }
        });
    }
});

