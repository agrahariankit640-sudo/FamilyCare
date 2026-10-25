document.addEventListener('DOMContentLoaded', async () => {
    let currentTab = 'upcoming';
    let currentMember = '';
    const listEl = document.querySelector('#appointments-list');
    const emptyEl = document.querySelector('#appointments-empty');
    const filterMemberSelect = document.querySelector('#filter-member');
    const modalMemberSelect = document.querySelector('#member_id');
    const modal = document.querySelector('#appointment-modal');
    const form = document.querySelector('#appointment-form');
    const modalTitle = document.querySelector('#modal-title');

    // 1. Load family members into select dropdowns
    async function initFamilyMembers() {
        try {
            const members = await API.familyMembers.list();
            if (members && members.length) {
                const options = members.map(m => `<option value="${m.id}">${m.name} (${m.relationship || 'Self'})</option>`).join('');
                if (filterMemberSelect) {
                    filterMemberSelect.innerHTML = '<option value="">All Family Members</option>' + options;
                }
                if (modalMemberSelect) {
                    modalMemberSelect.innerHTML = '<option value="">Select Family Member</option>' + options;
                }
            }
        } catch (e) {
            console.error('Error loading family members:', e);
        }
    }

    // 2. Load and render appointments
    async function loadAppointments() {
        if (!listEl) return;
        listEl.innerHTML = `
            <div class="loading-state col-span-full text-center py-8">
                <div class="spinner mb-2" style="margin: 0 auto;"></div>
                <p>Loading appointments...</p>
            </div>
        `;

        try {
            const params = {};
            if (currentTab) params.status = currentTab;
            if (currentMember) params.family_member_id = currentMember;

            const res = await API.appointments.list(params);
            const appointments = Array.isArray(res) ? res : (res && res.data ? res.data : []);

            if (appointments.length === 0) {
                listEl.innerHTML = '';
                if (emptyEl) emptyEl.classList.remove('hidden');
                return;
            }

            if (emptyEl) emptyEl.classList.add('hidden');

            listEl.innerHTML = appointments.map(a => {
                const status = (a.status || 'upcoming').toLowerCase();
                let statusBadge = 'badge-primary';
                if (status === 'completed') statusBadge = 'badge-success';
                else if (status === 'cancelled') statusBadge = 'badge-danger';

                const visitDate = a.visit_date ? App.date.format(a.visit_date) : 'Not specified';
                const visitTime = a.visit_time ? a.visit_time : '';
                const memberName = a.member_name || 'Family Member';
                const hospital = a.hospital ? `<p class="text-sm text-secondary mb-1"><i data-lucide="building-2" style="width:14px;height:14px;display:inline;"></i> ${a.hospital}</p>` : '';
                const reason = a.reason ? `<p class="text-sm mt-2 mb-2 font-medium">${a.reason}</p>` : '';
                const notes = a.notes ? `<p class="text-xs text-secondary mt-1 p-2 bg-bg-secondary rounded" style="background:var(--color-background);">${a.notes}</p>` : '';
                const followUp = a.follow_up_date ? `<p class="text-xs text-primary mt-2"><strong>Follow-up:</strong> ${App.date.format(a.follow_up_date)}</p>` : '';

                return `
                    <div class="card p-4 flex flex-col justify-between" style="border:1px solid var(--color-border); border-radius:var(--radius-lg); background:var(--color-surface);">
                        <div>
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <h4 class="font-bold text-lg mb-0">${a.doctor_name || 'Doctor Consultation'}</h4>
                                    <span class="text-xs text-primary font-medium">${a.specialization || 'General Physician'}</span>
                                </div>
                                <span class="badge ${statusBadge}" style="text-transform:capitalize;">${status}</span>
                            </div>
                            
                            ${hospital}
                            
                            <div class="text-sm text-secondary mb-2 flex items-center gap-2">
                                <span><i data-lucide="user" style="width:14px;height:14px;display:inline;"></i> ${memberName}</span>
                                <span>•</span>
                                <span><i data-lucide="calendar" style="width:14px;height:14px;display:inline;"></i> ${visitDate} ${visitTime}</span>
                            </div>

                            ${reason}
                            ${notes}
                            ${followUp}
                        </div>

                        <div class="border-t border-border-color pt-3 mt-4 flex justify-between items-center gap-2 flex-wrap">
                            <div class="flex gap-2">
                                ${status === 'upcoming' ? `
                                    <button class="btn btn-sm btn-success" onclick="window.updateApptStatus(${a.id}, 'completed')">
                                        <i data-lucide="check" style="width:14px;height:14px;"></i> Done
                                    </button>
                                    <button class="btn btn-sm btn-outline-primary" style="color:var(--color-danger);border-color:var(--color-danger);" onclick="window.updateApptStatus(${a.id}, 'cancelled')">
                                        Cancel
                                    </button>
                                ` : ''}
                            </div>
                            <div class="flex gap-2">
                                <button class="btn btn-sm btn-secondary" onclick="window.editAppt(${JSON.stringify(a).replace(/"/g, '&quot;')})">Edit</button>
                                <button class="btn btn-sm btn-danger" onclick="window.deleteAppt(${a.id})">Delete</button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            if (typeof lucide !== 'undefined' && lucide.createIcons) {
                lucide.createIcons();
            }

        } catch (e) {
            console.error('Error loading appointments:', e);
            listEl.innerHTML = '<div class="col-span-full text-center text-danger py-4">Error loading appointments. Please refresh.</div>';
            App.toast.show('Failed to load doctor visits', 'error');
        }
    }

    // 3. Tab switching
    document.querySelectorAll('#appointment-tabs .tab-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('#appointment-tabs .tab-link').forEach(l => {
                l.classList.remove('active', 'border-b-2', 'border-primary');
                l.classList.add('text-secondary');
            });
            link.classList.add('active', 'border-b-2', 'border-primary');
            link.classList.remove('text-secondary');

            currentTab = link.dataset.status || '';
            loadAppointments();
        });
    });

    // 4. Family Member filter
    filterMemberSelect?.addEventListener('change', (e) => {
        currentMember = e.target.value;
        loadAppointments();
    });

    // 5. Open Add Modal
    function openAddModal() {
        if (!form) return;
        form.reset();
        document.querySelector('#appointment_id').value = '';
        if (modalTitle) modalTitle.textContent = 'Add Doctor Appointment';
        App.modal.open('appointment-modal');
    }

    document.querySelector('#btn-add-appointment')?.addEventListener('click', openAddModal);
    document.querySelector('.btn-add-appointment')?.addEventListener('click', openAddModal);

    // 6. Form Submission
    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.querySelector('#btn-save-appointment');
        App.loading.showBtn(submitBtn);

        try {
            const formData = new FormData(form);
            const payload = {
                family_member_id: formData.get('family_member_id'),
                doctor_name: formData.get('doctor_name'),
                specialization: formData.get('specialization'),
                hospital: formData.get('hospital'),
                visit_date: formData.get('visit_date'),
                visit_time: formData.get('visit_time'),
                reason: formData.get('reason'),
                status: formData.get('status') || 'upcoming',
                follow_up_date: formData.get('follow_up_date') || null,
                notes: formData.get('notes')
            };

            const apptId = document.querySelector('#appointment_id').value;
            if (apptId) {
                await API.appointments.update(apptId, payload);
                App.toast.show('Appointment updated successfully', 'success');
            } else {
                await API.appointments.create(payload);
                App.toast.show('Appointment scheduled successfully', 'success');
            }

            App.modal.close('appointment-modal');
            loadAppointments();
        } catch (err) {
            console.error(err);
            App.toast.show(err.message || 'Failed to save appointment', 'error');
        } finally {
            App.loading.hideBtn(submitBtn);
        }
    });

    // 7. Global action helpers
    window.updateApptStatus = async (id, newStatus) => {
        try {
            await API.appointments.update(id, { status: newStatus });
            App.toast.show(`Appointment marked as ${newStatus}`, 'success');
            loadAppointments();
        } catch (e) {
            App.toast.show('Failed to update status', 'error');
        }
    };

    window.editAppt = (a) => {
        if (!form) return;
        form.reset();
        document.querySelector('#appointment_id').value = a.id;
        if (modalTitle) modalTitle.textContent = 'Edit Doctor Appointment';

        if (document.querySelector('#member_id')) document.querySelector('#member_id').value = a.family_member_id || '';
        if (document.querySelector('#doctor_name')) document.querySelector('#doctor_name').value = a.doctor_name || '';
        if (document.querySelector('#specialization')) document.querySelector('#specialization').value = a.specialization || '';
        if (document.querySelector('#hospital_name')) document.querySelector('#hospital_name').value = a.hospital || '';
        if (document.querySelector('#appointment_date')) document.querySelector('#appointment_date').value = a.visit_date || '';
        if (document.querySelector('#appointment_time')) document.querySelector('#appointment_time').value = a.visit_time || '';
        if (document.querySelector('#reason')) document.querySelector('#reason').value = a.reason || '';
        if (document.querySelector('#status')) document.querySelector('#status').value = (a.status || 'upcoming').toLowerCase();
        if (document.querySelector('#follow_up_date')) document.querySelector('#follow_up_date').value = a.follow_up_date || '';
        if (document.querySelector('#notes')) document.querySelector('#notes').value = a.notes || '';

        App.modal.open('appointment-modal');
    };

    window.deleteAppt = async (id) => {
        const confirmed = await App.confirm('Delete Appointment', 'Are you sure you want to delete this doctor visit record?');
        if (confirmed) {
            try {
                await API.appointments.delete(id);
                App.toast.show('Appointment deleted', 'success');
                loadAppointments();
            } catch (e) {
                App.toast.show('Failed to delete appointment', 'error');
            }
        }
    };

    // Initialize
    await initFamilyMembers();
    await loadAppointments();
});