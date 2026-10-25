document.addEventListener('DOMContentLoaded', async () => {
    let familyMembers = [];
    let vaccinationsList = [];

    const vaccinationsTableBody = document.getElementById('vaccinations-list');
    const emptyState = document.getElementById('vaccinations-empty');
    const memberFilter = document.getElementById('filter-member');
    const modalMemberSelect = document.getElementById('member_id');
    const vaxForm = document.getElementById('vaccination-form');

    // Load family members
    async function loadMembers() {
        try {
            const members = await API.familyMembers.list();
            familyMembers = Array.isArray(members) ? members : [];

            if (memberFilter) {
                memberFilter.innerHTML = '<option value="">All Family Members</option>' +
                    familyMembers.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
            }
            if (modalMemberSelect) {
                modalMemberSelect.innerHTML = '<option value="">Select Member</option>' +
                    familyMembers.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
            }
        } catch (err) {
            console.error('Error loading members:', err);
        }
    }

    // Load vaccinations
    async function loadVaccinations() {
        if (!vaccinationsTableBody) return;
        vaccinationsTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-6 text-secondary"><i data-lucide="loader" class="spin mb-2"></i><p>Loading vaccinations...</p></td></tr>';
        if (window.lucide) lucide.createIcons();

        try {
            const params = {};
            if (memberFilter && memberFilter.value) {
                params.family_member_id = memberFilter.value;
            }

            const data = await API.vaccinations.list(params);
            vaccinationsList = Array.isArray(data) ? data : [];

            renderTable();
        } catch (err) {
            console.error('Error loading vaccinations:', err);
            vaccinationsTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-6 text-danger">Failed to load vaccinations.</td></tr>';
            App.toast.show('Error loading vaccinations', 'error');
        }
    }

    function renderTable() {
        if (vaccinationsList.length === 0) {
            vaccinationsTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-secondary">No vaccinations found.</td></tr>';
            if (emptyState) {
                emptyState.classList.remove('hidden');
                document.querySelector('.table-container')?.classList.add('hidden');
            }
            return;
        }

        if (emptyState) emptyState.classList.add('hidden');
        document.querySelector('.table-container')?.classList.remove('hidden');

        const now = new Date();
        const oneWeekAhead = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

        vaccinationsTableBody.innerHTML = vaccinationsList.map(v => {
            const vaxDate = v.vaccination_date ? App.date.format(v.vaccination_date) : '-';
            const nextDue = v.next_dose_date ? App.date.format(v.next_dose_date) : '-';
            const memberName = v.member_name || (familyMembers.find(m => m.id === v.family_member_id)?.name || 'Member');

            let nextDueClass = 'text-main';
            let nextDueBadge = '';
            if (v.next_dose_date) {
                const nextDateObj = new Date(v.next_dose_date);
                if (nextDateObj < now) {
                    nextDueClass = 'text-danger font-semibold';
                    nextDueBadge = ' <span class="badge badge-danger text-xs">Overdue</span>';
                } else if (nextDateObj <= oneWeekAhead) {
                    nextDueClass = 'text-warning font-semibold';
                    nextDueBadge = ' <span class="badge badge-warning text-xs">Due Soon</span>';
                }
            }

            return `
                <tr>
                    <td>
                        <div class="font-semibold text-main">${v.vaccine_name || 'Vaccine'}</div>
                        ${v.notes ? `<span class="text-xs text-secondary truncate max-w-xs block">${v.notes}</span>` : ''}
                    </td>
                    <td>
                        <span class="badge badge-info">${memberName}</span>
                    </td>
                    <td>${vaxDate}</td>
                    <td>
                        <span class="badge badge-secondary">${v.dose_number ? (String(v.dose_number).toLowerCase().startsWith('dose') ? v.dose_number : 'Dose ' + v.dose_number) : '1st Dose'}</span>
                    </td>
                    <td class="${nextDueClass}">
                        ${v.next_dose_date ? `${nextDue}${nextDueBadge}` : '<span class="text-secondary">Completed</span>'}
                    </td>
                    <td>${v.hospital || '<span class="text-secondary">-</span>'}</td>
                    <td>
                        <div class="flex items-center gap-2">
                            <button class="btn btn-sm btn-outline-primary p-2" title="Edit" onclick="editVaccinationItem(${v.id})">
                                <i data-lucide="edit-2" size="14"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger p-2" title="Delete" onclick="deleteVaccinationItem(${v.id})">
                                <i data-lucide="trash-2" size="14"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        if (window.lucide) lucide.createIcons();
    }

    memberFilter?.addEventListener('change', loadVaccinations);

    // Add buttons
    document.querySelectorAll('#btn-add-vaccination, .btn-add-vaccination').forEach(btn => {
        btn.addEventListener('click', () => {
            if (vaxForm) {
                vaxForm.reset();
                document.getElementById('vaccination_id').value = '';
                document.getElementById('modal-title').textContent = 'Add Vaccination';
                document.getElementById('vaccination_date').value = new Date().toISOString().split('T')[0];
            }
            App.modal.open('vaccination-modal');
        });
    });

    // Form submit
    if (vaxForm) {
        vaxForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('vaccination_id').value;
            const payload = {
                family_member_id: parseInt(document.getElementById('member_id').value),
                vaccine_name: document.getElementById('vaccine_name').value.trim(),
                vaccination_date: document.getElementById('vaccination_date').value,
                dose_number: document.getElementById('dose_number')?.value?.trim() || null,
                hospital: document.getElementById('hospital')?.value?.trim() || '',
                next_dose_date: document.getElementById('next_dose_date')?.value || null,
                notes: document.getElementById('notes')?.value?.trim() || ''
            };

            if (!payload.family_member_id || !payload.vaccine_name || !payload.vaccination_date) {
                App.toast.show('Please fill in required fields', 'warning');
                return;
            }

            try {
                if (id) {
                    await API.vaccinations.update(id, payload);
                    App.toast.show('Vaccination updated successfully', 'success');
                } else {
                    await API.vaccinations.create(payload);
                    App.toast.show('Vaccination recorded successfully', 'success');
                }
                App.modal.close('vaccination-modal');
                loadVaccinations();
            } catch (err) {
                console.error('Error saving vaccination:', err);
                App.toast.show(err.message || 'Error saving vaccination', 'error');
            }
        });
    }

    // Edit vaccination
    window.editVaccinationItem = async (id) => {
        try {
            const res = await API.vaccinations.get(id);
            const v = res.data || res;
            if (!v) return;

            document.getElementById('vaccination_id').value = v.id;
            document.getElementById('member_id').value = v.family_member_id || '';
            document.getElementById('vaccine_name').value = v.vaccine_name || '';
            document.getElementById('vaccination_date').value = v.vaccination_date || '';
            document.getElementById('dose_number').value = v.dose_number || '';
            document.getElementById('hospital').value = v.hospital || '';
            document.getElementById('next_dose_date').value = v.next_dose_date || '';
            document.getElementById('notes').value = v.notes || '';
            document.getElementById('modal-title').textContent = 'Edit Vaccination';

            App.modal.open('vaccination-modal');
        } catch (err) {
            console.error('Error fetching vaccination:', err);
            App.toast.show('Failed to load vaccination details', 'error');
        }
    };

    // Delete vaccination
    window.deleteVaccinationItem = async (id) => {
        if (await App.confirm('Are you sure you want to delete this vaccination record?')) {
            try {
                await API.vaccinations.delete(id);
                App.toast.show('Vaccination record deleted', 'success');
                loadVaccinations();
            } catch (err) {
                console.error('Error deleting vaccination:', err);
                App.toast.show('Failed to delete vaccination', 'error');
            }
        }
    };

    await loadMembers();
    await loadVaccinations();
});