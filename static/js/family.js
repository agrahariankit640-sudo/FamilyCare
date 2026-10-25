document.addEventListener('DOMContentLoaded', async () => {
    const listEl = document.querySelector('#members-container') || document.querySelector('#family-list');
    const emptyEl = document.querySelector('#empty-state');
    const modal = document.querySelector('#member-modal');
    const form = document.querySelector('#member-form');
    const modalTitle = document.querySelector('#modal-title');

    function calculateAge(dob) {
        if (!dob) return 'N/A';
        const birthDate = new Date(dob);
        const today = new Date();
        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age > 0 ? `${age} yrs` : 'Infant';
    }

    async function loadMembers() {
        if (!listEl) return;
        listEl.innerHTML = `
            <div class="loading-state col-span-full text-center py-8">
                <div class="spinner mb-2" style="margin: 0 auto;"></div>
                <p>Loading family members...</p>
            </div>
        `;

        try {
            const res = await API.familyMembers.list();
            const members = Array.isArray(res) ? res : (res && res.data ? res.data : []);

            if (!members || members.length === 0) {
                listEl.innerHTML = '';
                if (emptyEl) emptyEl.classList.remove('hidden');
                return;
            }

            if (emptyEl) emptyEl.classList.add('hidden');

            listEl.innerHTML = members.map(m => {
                const age = calculateAge(m.date_of_birth || m.dob);
                const blood = m.blood_group || m.bloodGroup || 'Unknown';
                const initial = (m.name ? m.name[0] : 'F').toUpperCase();
                const allergies = m.allergies ? `<p class="text-xs text-danger mb-1"><i data-lucide="alert-circle" style="width:14px;height:14px;display:inline;"></i> <strong>Allergies:</strong> ${m.allergies}</p>` : '';
                const conditions = m.chronic_conditions ? `<p class="text-xs text-secondary mb-1"><i data-lucide="activity" style="width:14px;height:14px;display:inline;"></i> <strong>Conditions:</strong> ${m.chronic_conditions}</p>` : '';

                return `
                    <div class="card p-4 flex flex-col justify-between" style="border:1px solid var(--color-border); border-radius:var(--radius-lg); background:var(--color-surface);">
                        <div>
                            <div class="flex items-center gap-3 mb-3">
                                <div class="user-avatar" style="width:48px;height:48px;font-size:18px;">
                                    ${initial}
                                </div>
                                <div class="flex-1">
                                    <div class="flex justify-between items-start">
                                        <h3 class="font-bold text-lg mb-0">${m.name}</h3>
                                        <span class="badge badge-primary text-xs">${m.relationship || 'Member'}</span>
                                    </div>
                                    <span class="text-xs text-secondary">${m.gender || 'Not specified'} • ${age}</span>
                                </div>
                            </div>

                            <div class="flex gap-2 mb-3">
                                <span class="badge badge-outline text-xs" style="border:1px solid var(--color-border);">Blood: ${blood}</span>
                                ${m.emergency_contact_phone ? `<span class="badge badge-outline text-xs" style="border:1px solid var(--color-border);"><i data-lucide="phone" style="width:12px;height:12px;display:inline;"></i> ${m.emergency_contact_phone}</span>` : ''}
                            </div>

                            ${allergies}
                            ${conditions}
                        </div>

                        <div class="border-t border-border-color pt-3 mt-4 flex justify-between items-center gap-2">
                            <a href="/member/${m.id}" class="btn btn-sm btn-outline-primary" style="display:inline-flex;align-items:center;gap:4px;">
                                <i data-lucide="eye" style="width:14px;height:14px;"></i> View Records
                            </a>
                            <div class="flex gap-2">
                                <button class="btn btn-sm btn-secondary" onclick="window.editMember(${JSON.stringify(m).replace(/"/g, '&quot;')})">Edit</button>
                                <button class="btn btn-sm btn-danger" onclick="window.deleteMember(${m.id})">Delete</button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            if (typeof lucide !== 'undefined' && lucide.createIcons) {
                lucide.createIcons();
            }

        } catch (e) {
            console.error('Error loading members:', e);
            listEl.innerHTML = '<div class="col-span-full text-center text-danger py-4">Error loading family members. Please refresh.</div>';
            App.toast.show('Failed to load family members', 'error');
        }
    }

    // Modal Add
    function openAddModal() {
        if (!form) return;
        form.reset();
        document.querySelector('#member_id').value = '';
        if (modalTitle) modalTitle.textContent = 'Add Family Member';
        App.modal.open('member-modal');
    }

    document.querySelector('#btn-add-member')?.addEventListener('click', openAddModal);
    document.querySelector('.btn-add-member')?.addEventListener('click', openAddModal);
    document.querySelector('#add-member-btn')?.addEventListener('click', openAddModal);

    // Form Submit
    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.querySelector('#btn-save-member');
        App.loading.showBtn(submitBtn);

        try {
            const formData = new FormData(form);
            const payload = {
                name: formData.get('name'),
                relationship: formData.get('relationship'),
                date_of_birth: formData.get('date_of_birth'),
                gender: formData.get('gender'),
                blood_group: formData.get('blood_group'),
                allergies: formData.get('allergies'),
                chronic_conditions: formData.get('chronic_conditions')
            };

            const memberId = document.querySelector('#member_id').value;
            if (memberId) {
                await API.familyMembers.update(memberId, payload);
                App.toast.show('Member updated successfully', 'success');
            } else {
                await API.familyMembers.create(payload);
                App.toast.show('Member added successfully', 'success');
            }

            App.modal.close('member-modal');
            loadMembers();
        } catch (err) {
            console.error(err);
            App.toast.show(err.message || 'Failed to save family member', 'error');
        } finally {
            App.loading.hideBtn(submitBtn);
        }
    });

    window.editMember = (m) => {
        if (!form) return;
        form.reset();
        document.querySelector('#member_id').value = m.id;
        if (modalTitle) modalTitle.textContent = 'Edit Family Member';

        if (document.querySelector('#name')) document.querySelector('#name').value = m.name || '';
        if (document.querySelector('#relationship')) document.querySelector('#relationship').value = m.relationship || 'Self';
        if (document.querySelector('#date_of_birth')) document.querySelector('#date_of_birth').value = m.date_of_birth || m.dob || '';
        if (document.querySelector('#gender')) document.querySelector('#gender').value = m.gender || 'Male';
        if (document.querySelector('#blood_group')) document.querySelector('#blood_group').value = m.blood_group || m.bloodGroup || '';
        if (document.querySelector('#allergies')) document.querySelector('#allergies').value = m.allergies || '';
        if (document.querySelector('#chronic_conditions')) document.querySelector('#chronic_conditions').value = m.chronic_conditions || '';

        App.modal.open('member-modal');
    };

    window.deleteMember = async (id) => {
        const confirmed = await App.confirm('Delete Member', 'Are you sure you want to remove this family member? All associated records will remain archived.');
        if (confirmed) {
            try {
                await API.familyMembers.delete(id);
                App.toast.show('Family member removed', 'success');
                loadMembers();
            } catch (e) {
                App.toast.show('Failed to remove member', 'error');
            }
        }
    };

    await loadMembers();
});