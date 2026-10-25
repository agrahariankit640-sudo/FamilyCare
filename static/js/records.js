document.addEventListener('DOMContentLoaded', async () => {
    const tableBody = document.querySelector('#records-list') || document.querySelector('#records-table tbody');
    const emptyEl = document.querySelector('#records-empty');
    const filterMember = document.querySelector('#filter-member');
    const filterType = document.querySelector('#filter-type');
    const filterSearch = document.querySelector('#filter-search');
    const modalMember = document.querySelector('#member_id');
    const form = document.querySelector('#record-form');
    const modalTitle = document.querySelector('#modal-title');
    let currentFilters = {};

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

    async function loadRecords() {
        if (!tableBody) return;
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center py-4"><div class="spinner mb-2" style="margin: 0 auto;"></div>Loading records...</td></tr>';

        try {
            const res = await API.records.list(currentFilters);
            let records = Array.isArray(res) ? res : (res && res.data ? res.data : []);

            // Client-side search filter if search term entered
            if (filterSearch && filterSearch.value.trim()) {
                const q = filterSearch.value.toLowerCase();
                records = records.filter(r => 
                    (r.title && r.title.toLowerCase().includes(q)) ||
                    (r.doctor_name && r.doctor_name.toLowerCase().includes(q)) ||
                    (r.hospital && r.hospital.toLowerCase().includes(q)) ||
                    (r.member_name && r.member_name.toLowerCase().includes(q))
                );
            }

            if (records.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" class="text-center py-6 text-secondary">No records found matching filters.</td></tr>';
                if (emptyEl && Object.keys(currentFilters).length === 0) emptyEl.classList.remove('hidden');
                return;
            }

            if (emptyEl) emptyEl.classList.add('hidden');

            tableBody.innerHTML = records.map(r => {
                const date = r.record_date ? App.date.format(r.record_date) : '-';
                const member = r.member_name || 'Member';
                const type = r.record_type || 'General';
                const doctor = r.doctor_name || r.hospital || '-';

                return `
                    <tr>
                        <td class="font-medium">${date}</td>
                        <td>
                            <div class="font-bold text-sm">${r.title || 'Untitled Record'}</div>
                            <span class="badge badge-primary text-xs">${type}</span>
                        </td>
                        <td><i data-lucide="user" style="width:14px;height:14px;display:inline;"></i> ${member}</td>
                        <td class="text-secondary">${doctor}</td>
                        <td>
                            <div class="flex gap-2">
                                <button class="btn btn-sm btn-secondary" onclick="window.editRecord(${JSON.stringify(r).replace(/"/g, '&quot;')})">Edit</button>
                                <button class="btn btn-sm btn-danger" onclick="window.deleteRecord(${r.id})">Delete</button>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');

            if (typeof lucide !== 'undefined' && lucide.createIcons) {
                lucide.createIcons();
            }

        } catch (e) {
            console.error('Error loading records:', e);
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-danger">Failed to load records.</td></tr>';
            App.toast.show('Failed to load records', 'error');
        }
    }

    // Filter listeners
    filterMember?.addEventListener('change', (e) => {
        if (e.target.value) currentFilters.member_id = e.target.value;
        else delete currentFilters.member_id;
        loadRecords();
    });

    filterType?.addEventListener('change', (e) => {
        if (e.target.value) currentFilters.record_type = e.target.value;
        else delete currentFilters.record_type;
        loadRecords();
    });

    filterSearch?.addEventListener('input', App.search.debounce(() => {
        loadRecords();
    }, 300));

    // Open Modal
    function openAddModal() {
        if (!form) return;
        form.reset();
        document.querySelector('#record_id').value = '';
        if (modalTitle) modalTitle.textContent = 'Add Medical Record';
        App.modal.open('record-modal');
    }

    document.querySelector('#btn-add-record')?.addEventListener('click', openAddModal);
    document.querySelector('.btn-add-record')?.addEventListener('click', openAddModal);

    // Form submit
    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.querySelector('#btn-save-record');
        App.loading.showBtn(submitBtn);

        try {
            const formData = new FormData(form);
            const payload = {
                family_member_id: formData.get('family_member_id'),
                title: formData.get('title'),
                record_type: formData.get('record_type'),
                record_date: formData.get('record_date'),
                doctor_name: formData.get('doctor_name'),
                hospital: formData.get('hospital'),
                notes: formData.get('notes')
            };

            const recordId = document.querySelector('#record_id').value;
            if (recordId) {
                await API.records.update(recordId, payload);
                App.toast.show('Record updated successfully', 'success');
            } else {
                await API.records.create(payload);
                App.toast.show('Record added successfully', 'success');
            }

            App.modal.close('record-modal');
            loadRecords();
        } catch (err) {
            console.error(err);
            App.toast.show(err.message || 'Failed to save record', 'error');
        } finally {
            App.loading.hideBtn(submitBtn);
        }
    });

    window.editRecord = (r) => {
        if (!form) return;
        form.reset();
        document.querySelector('#record_id').value = r.id;
        if (modalTitle) modalTitle.textContent = 'Edit Medical Record';

        if (document.querySelector('#member_id')) document.querySelector('#member_id').value = r.family_member_id || '';
        if (document.querySelector('#title')) document.querySelector('#title').value = r.title || '';
        if (document.querySelector('#record_type')) document.querySelector('#record_type').value = r.record_type || 'Prescription';
        if (document.querySelector('#record_date')) document.querySelector('#record_date').value = r.record_date || '';
        if (document.querySelector('#doctor_name')) document.querySelector('#doctor_name').value = r.doctor_name || '';
        if (document.querySelector('#hospital_name')) document.querySelector('#hospital_name').value = r.hospital || '';
        if (document.querySelector('#notes')) document.querySelector('#notes').value = r.notes || '';

        App.modal.open('record-modal');
    };

    window.deleteRecord = async (id) => {
        const confirmed = await App.confirm('Delete Record', 'Are you sure you want to delete this medical record?');
        if (confirmed) {
            try {
                await API.records.delete(id);
                App.toast.show('Record deleted', 'success');
                loadRecords();
            } catch (e) {
                App.toast.show('Failed to delete record', 'error');
            }
        }
    };

    await loadFamilyMembers();
    await loadRecords();
});