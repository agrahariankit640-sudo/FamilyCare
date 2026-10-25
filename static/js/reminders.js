document.addEventListener('DOMContentLoaded', async () => {
    let currentStatus = 'Today';
    let medicinesList = [];

    const remindersList = document.getElementById('reminders-list');
    const emptyState = document.getElementById('reminders-empty');
    const tabLinks = document.querySelectorAll('#reminder-tabs .tab-link');
    const medicineSelect = document.getElementById('medicine_id');
    const reminderForm = document.getElementById('reminder-form');

    // Load active medicines to populate medicine dropdown
    async function loadMedicines() {
        try {
            const meds = await API.medicines.list({ status: 'active' });
            medicinesList = Array.isArray(meds) ? meds : [];
            if (medicineSelect) {
                if (medicinesList.length === 0) {
                    medicineSelect.innerHTML = '<option value="">No active medicines found</option>';
                } else {
                    medicineSelect.innerHTML = '<option value="">Select Medicine</option>' +
                        medicinesList.map(m => `
                            <option value="${m.id}" data-member="${m.family_member_id || ''}">
                                ${m.name} (${m.member_name || 'Member'}) - ${m.dosage || ''}
                            </option>
                        `).join('');
                }
            }
        } catch (err) {
            console.error('Error loading medicines for reminders:', err);
        }
    }

    // Render reminders
    async function loadReminders() {
        if (!remindersList) return;
        remindersList.innerHTML = `
            <div class="loading-state col-span-full text-center py-8">
                <i data-lucide="loader" class="spin mb-2"></i>
                <p>Loading reminders...</p>
            </div>
        `;
        if (window.lucide) lucide.createIcons();

        try {
            const params = {};
            if (currentStatus) {
                params.status = currentStatus;
            }
            const res = await API.reminders.list(params);
            const reminders = Array.isArray(res) ? res : [];

            if (reminders.length === 0) {
                remindersList.innerHTML = '';
                if (emptyState) emptyState.classList.remove('hidden');
                return;
            }

            if (emptyState) emptyState.classList.add('hidden');

            const statusColors = {
                pending: 'badge-warning',
                taken: 'badge-success',
                skipped: 'badge-danger'
            };

            remindersList.innerHTML = reminders.map(r => {
                const status = (r.status || 'pending').toLowerCase();
                const badgeClass = statusColors[status] || 'badge-secondary';
                const formattedTime = r.reminder_time ? r.reminder_time.substring(0, 5) : '--:--';
                const formattedDate = r.reminder_date || 'Today';

                return `
                    <div class="card p-4 flex flex-col justify-between hover-shadow transition-shadow">
                        <div>
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <h4 class="font-bold text-lg text-primary">${r.medicine_name || 'Medication'}</h4>
                                    <span class="text-sm text-secondary">${r.member_name ? 'For: ' + r.member_name : 'General'}</span>
                                </div>
                                <span class="badge ${badgeClass} text-xs uppercase font-semibold">${r.status || 'Pending'}</span>
                            </div>
                            <div class="mt-3 space-y-1 text-sm text-secondary">
                                <div class="flex items-center gap-2">
                                    <i data-lucide="clock" size="16"></i>
                                    <span>Time: <strong class="text-main">${formattedTime}</strong></span>
                                </div>
                                <div class="flex items-center gap-2">
                                    <i data-lucide="calendar" size="16"></i>
                                    <span>Date: ${formattedDate}</span>
                                </div>
                                ${r.frequency ? `
                                <div class="flex items-center gap-2">
                                    <i data-lucide="repeat" size="16"></i>
                                    <span>Freq: ${r.frequency}</span>
                                </div>` : ''}
                            </div>
                        </div>

                        <div class="border-t border-border-color pt-3 mt-4 flex items-center justify-between gap-2">
                            <div class="flex items-center gap-2">
                                ${status === 'pending' ? `
                                    <button class="btn btn-sm btn-outline-success" onclick="updateReminderStatus(${r.id}, 'taken')">
                                        <i data-lucide="check" size="14"></i> Take
                                    </button>
                                    <button class="btn btn-sm btn-outline-secondary" onclick="updateReminderStatus(${r.id}, 'skipped')">
                                        <i data-lucide="x" size="14"></i> Skip
                                    </button>
                                ` : `
                                    <button class="btn btn-sm btn-outline-warning" onclick="updateReminderStatus(${r.id}, 'pending')">
                                        <i data-lucide="rotate-ccw" size="14"></i> Reset
                                    </button>
                                `}
                            </div>
                            <button class="btn btn-sm btn-outline-danger p-2" title="Delete Reminder" onclick="deleteReminderItem(${r.id})">
                                <i data-lucide="trash-2" size="14"></i>
                            </button>
                        </div>
                    </div>
                `;
            }).join('');

            if (window.lucide) lucide.createIcons();
        } catch (err) {
            console.error('Error loading reminders:', err);
            remindersList.innerHTML = `
                <div class="col-span-full text-center py-8 text-danger">
                    <p>Failed to load reminders. Please try again.</p>
                </div>
            `;
            App.toast.show('Error loading reminders', 'error');
        }
    }

    // Tabs
    tabLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            tabLinks.forEach(l => {
                l.classList.remove('active', 'border-b-2', 'border-primary');
                l.classList.add('text-secondary');
            });
            link.classList.add('active', 'border-b-2', 'border-primary');
            link.classList.remove('text-secondary');
            currentStatus = link.dataset.status;
            loadReminders();
        });
    });

    // Add buttons
    document.querySelectorAll('#btn-add-reminder, .btn-add-reminder').forEach(btn => {
        btn.addEventListener('click', () => {
            if (reminderForm) {
                reminderForm.reset();
                document.getElementById('reminder_id').value = '';
                document.getElementById('modal-title').textContent = 'Add Reminder';
                const now = new Date();
                const hours = String(now.getHours()).padStart(2, '0');
                const minutes = String(now.getMinutes()).padStart(2, '0');
                document.getElementById('reminder_time').value = `${hours}:${minutes}`;
            }
            App.modal.open('reminder-modal');
        });
    });

    // Form submit
    if (reminderForm) {
        reminderForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const medicineId = document.getElementById('medicine_id').value;
            const reminderTime = document.getElementById('reminder_time').value;
            const status = document.getElementById('status').value || 'pending';
            const selectedOpt = medicineSelect?.selectedOptions[0];
            const memberId = selectedOpt?.dataset.member || null;

            if (!medicineId || !reminderTime) {
                App.toast.show('Please fill in required fields', 'warning');
                return;
            }

            const payload = {
                medicine_id: parseInt(medicineId),
                family_member_id: memberId ? parseInt(memberId) : null,
                reminder_time: reminderTime,
                status: status
            };

            try {
                await API.reminders.create(payload);
                App.modal.close('reminder-modal');
                App.toast.show('Reminder saved successfully', 'success');
                loadReminders();
            } catch (err) {
                console.error('Error saving reminder:', err);
                App.toast.show(err.message || 'Error saving reminder', 'error');
            }
        });
    }

    // Global action helpers
    window.updateReminderStatus = async (id, status) => {
        try {
            await API.reminders.updateStatus(id, status);
            App.toast.show(`Reminder marked as ${status}`, 'success');
            loadReminders();
        } catch (err) {
            console.error('Error updating reminder status:', err);
            App.toast.show('Failed to update status', 'error');
        }
    };

    window.deleteReminderItem = async (id) => {
        if (await App.confirm('Are you sure you want to delete this reminder?')) {
            try {
                await API.reminders.delete(id);
                App.toast.show('Reminder deleted', 'success');
                loadReminders();
            } catch (err) {
                console.error('Error deleting reminder:', err);
                App.toast.show('Failed to delete reminder', 'error');
            }
        }
    };

    // Initial load
    await loadMedicines();
    await loadReminders();
});