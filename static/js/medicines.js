document.addEventListener('DOMContentLoaded', async () => {
    let currentStatus = 'active';
    let currentMember = '';
    const tableBody = document.querySelector('#medicines-list') || document.querySelector('#medicines-table tbody');
    const emptyEl = document.querySelector('#medicines-empty');
    const filterMember = document.querySelector('#filter-member');
    const modalMember = document.querySelector('#member_id');
    const form = document.querySelector('#medicine-form');
    const modalTitle = document.querySelector('#modal-title');

    async function loadFamilyMembers() {
        try {
            const members = await API.familyMembers.list();
            if (members && members.length) {
                const options = members.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
                if (filterMember) filterMember.innerHTML = '<option value="">All Family Members</option>' + options;
                if (modalMember) modalMember.innerHTML = '<option value="">Select Family Member</option>' + options;
            }
        } catch (e) {
            console.error('Error loading members:', e);
        }
    }

    async function loadMedicines() {
        if (!tableBody) return;
        tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4"><div class="spinner mb-2" style="margin: 0 auto;"></div>Loading medicines...</td></tr>';

        try {
            const params = {};
            if (currentStatus) params.status = currentStatus;
            if (currentMember) params.family_member_id = currentMember;

            const res = await API.medicines.list(params);
            const medicines = Array.isArray(res) ? res : (res && res.data ? res.data : []);

            if (medicines.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-6 text-secondary">No medicines found.</td></tr>';
                if (emptyEl && !currentStatus && !currentMember) emptyEl.classList.remove('hidden');
                return;
            }

            if (emptyEl) emptyEl.classList.add('hidden');

            tableBody.innerHTML = medicines.map(m => {
                const status = (m.status || 'active').toLowerCase();
                let statusBadge = 'badge-primary';
                if (status === 'completed') statusBadge = 'badge-success';
                else if (status === 'stopped') statusBadge = 'badge-danger';

                const member = m.member_name || 'Member';
                const duration = `${m.start_date ? App.date.format(m.start_date) : '-'} to ${m.end_date ? App.date.format(m.end_date) : 'Ongoing'}`;

                return `
                    <tr>
                        <td>
                            <div class="font-bold text-sm">${m.name || 'Medicine'}</div>
                            <span class="text-xs text-secondary">${m.instructions || ''}</span>
                        </td>
                        <td><i data-lucide="user" style="width:14px;height:14px;display:inline;"></i> ${member}</td>
                        <td>
                            <div>${m.dosage || ''}</div>
                            <span class="text-xs text-secondary">${m.frequency || ''}</span>
                        </td>
                        <td class="text-xs text-secondary">${duration}</td>
                        <td><span class="badge ${statusBadge}" style="text-transform:capitalize;">${status}</span></td>
                        <td>
                            <div class="flex gap-2">
                                ${status === 'active' ? `
                                    <button class="btn btn-sm btn-success" title="Mark Completed" onclick="window.updateMedicineStatus(${m.id}, 'completed')">
                                        <i data-lucide="check" style="width:14px;height:14px;"></i> Done
                                    </button>
                                    <button class="btn btn-sm btn-outline-primary" style="color:var(--color-danger);border-color:var(--color-danger);" title="Stop" onclick="window.updateMedicineStatus(${m.id}, 'stopped')">
                                        Stop
                                    </button>
                                ` : ''}
                                <button class="btn btn-sm btn-secondary" onclick="window.editMedicine(${JSON.stringify(m).replace(/"/g, '&quot;')})">Edit</button>
                                <button class="btn btn-sm btn-danger" onclick="window.deleteMedicine(${m.id})">Delete</button>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');

            if (typeof lucide !== 'undefined' && lucide.createIcons) {
                lucide.createIcons();
            }

        } catch (e) {
            console.error('Error loading medicines:', e);
            tableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-danger">Failed to load medicines.</td></tr>';
            App.toast.show('Failed to load medicines', 'error');
        }
    }

    // Tabs
    document.querySelectorAll('#medicine-tabs .tab-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('#medicine-tabs .tab-link').forEach(l => {
                l.classList.remove('active', 'border-b-2', 'border-primary');
                l.classList.add('text-secondary');
            });
            link.classList.add('active', 'border-b-2', 'border-primary');
            link.classList.remove('text-secondary');

            currentStatus = (link.dataset.status || '').toLowerCase();
            loadMedicines();
        });
    });

    // Member filter
    filterMember?.addEventListener('change', (e) => {
        currentMember = e.target.value;
        loadMedicines();
    });

    // Open Modal
    function openAddModal() {
        if (!form) return;
        form.reset();
        document.querySelector('#medicine_id').value = '';
        if (modalTitle) modalTitle.textContent = 'Add Medicine';
        App.modal.open('medicine-modal');
    }

    document.querySelector('#btn-add-medicine')?.addEventListener('click', openAddModal);
    document.querySelector('.btn-add-medicine')?.addEventListener('click', openAddModal);

    // Form submit
    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.querySelector('#btn-save-medicine');
        App.loading.showBtn(submitBtn);

        try {
            const formData = new FormData(form);
            const payload = {
                family_member_id: formData.get('family_member_id'),
                name: formData.get('name'),
                dosage: formData.get('dosage'),
                frequency: formData.get('frequency'),
                start_date: formData.get('start_date'),
                end_date: formData.get('end_date') || null,
                instructions: formData.get('instructions'),
                status: (formData.get('status') || 'active').toLowerCase()
            };

            const medId = document.querySelector('#medicine_id').value;
            if (medId) {
                await API.medicines.update(medId, payload);
                App.toast.show('Medicine updated successfully', 'success');
            } else {
                await API.medicines.create(payload);
                App.toast.show('Medicine added successfully', 'success');
            }

            App.modal.close('medicine-modal');
            loadMedicines();
        } catch (err) {
            console.error(err);
            App.toast.show(err.message || 'Failed to save medicine', 'error');
        } finally {
            App.loading.hideBtn(submitBtn);
        }
    });

    window.editMedicine = (m) => {
        if (!form) return;
        form.reset();
        document.querySelector('#medicine_id').value = m.id;
        if (modalTitle) modalTitle.textContent = 'Edit Medicine';

        if (document.querySelector('#member_id')) document.querySelector('#member_id').value = m.family_member_id || '';
        if (document.querySelector('#name')) document.querySelector('#name').value = m.name || '';
        if (document.querySelector('#dosage')) document.querySelector('#dosage').value = m.dosage || '';
        if (document.querySelector('#frequency')) document.querySelector('#frequency').value = m.frequency || 'Once Daily';
        if (document.querySelector('#start_date')) document.querySelector('#start_date').value = m.start_date || '';
        if (document.querySelector('#end_date')) document.querySelector('#end_date').value = m.end_date || '';
        if (document.querySelector('#instructions')) document.querySelector('#instructions').value = m.instructions || 'After Food';
        if (document.querySelector('#status')) document.querySelector('#status').value = (m.status || 'active').toLowerCase();

        App.modal.open('medicine-modal');
    };

    window.updateMedicineStatus = async (id, status) => {
        try {
            await API.medicines.updateStatus(id, status);
            App.toast.show(`Medicine marked as ${status}`, 'success');
            loadMedicines();
        } catch (e) {
            App.toast.show('Failed to update status', 'error');
        }
    };

    window.deleteMedicine = async (id) => {
        const confirmed = await App.confirm('Delete Medicine', 'Are you sure you want to delete this medicine?');
        if (confirmed) {
            try {
                await API.medicines.delete(id);
                App.toast.show('Medicine deleted', 'success');
                loadMedicines();
            } catch (e) {
                App.toast.show('Failed to delete medicine', 'error');
            }
        }
    };

    await loadFamilyMembers();
    await loadMedicines();
});