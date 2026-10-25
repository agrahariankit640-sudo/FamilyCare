document.addEventListener('DOMContentLoaded', async () => {
    let allMembers = [];
    const container = document.getElementById('emergency-cards-container');
    const emptyState = document.getElementById('emergency-empty');
    const memberFilter = document.getElementById('filter-member');

    async function loadEmergencyData() {
        if (!container) return;
        container.innerHTML = `
            <div class="loading-state text-center py-8">
                <i data-lucide="loader" class="spin mb-2"></i>
                <p>Loading emergency profiles...</p>
            </div>
        `;
        if (window.lucide) lucide.createIcons();

        try {
            const res = await API.emergency.getAll();
            allMembers = Array.isArray(res) ? res : [];

            if (memberFilter) {
                memberFilter.innerHTML = '<option value="all">Show All Family Members</option>' +
                    allMembers.map(m => `<option value="${m.id}">${m.name} (${m.relationship || 'Member'})</option>`).join('');
            }

            renderCards();
        } catch (err) {
            console.error('Error loading emergency info:', err);
            container.innerHTML = '<div class="text-center py-8 text-danger">Failed to load emergency profiles.</div>';
            App.toast.show('Error loading emergency data', 'error');
        }
    }

    function renderCards() {
        if (!container) return;

        const selectedId = memberFilter ? memberFilter.value : 'all';
        const filtered = selectedId === 'all' 
            ? allMembers 
            : allMembers.filter(m => String(m.id) === String(selectedId));

        if (filtered.length === 0) {
            container.innerHTML = '';
            if (emptyState) emptyState.classList.remove('hidden');
            return;
        }

        if (emptyState) emptyState.classList.add('hidden');

        container.innerHTML = filtered.map(m => {
            const blood = m.blood_group || m.bloodGroup || 'Unknown';
            const phone = m.emergency_contact_phone || m.emergencyPhone || m.phone || '';
            const contactName = m.emergency_contact || m.emergencyContact || 'Not specified';
            const allergies = m.allergies || 'None reported';
            const conditions = m.existing_conditions || m.conditions || 'None reported';
            const notes = m.important_notes || m.notes || '';

            return `
                <div class="card p-6 border-l-4 border-danger shadow-md mb-4 bg-white">
                    <div class="flex flex-wrap justify-between items-start gap-4 mb-4">
                        <div class="flex items-center gap-3">
                            <div class="w-12 h-12 rounded-full bg-danger-light text-danger flex items-center justify-center font-bold text-xl">
                                ${m.name ? m.name.charAt(0).toUpperCase() : 'F'}
                            </div>
                            <div>
                                <h3 class="text-xl font-bold text-main">${m.name}</h3>
                                <p class="text-sm text-secondary">${m.relationship || 'Family Member'} ${m.gender ? '• ' + m.gender : ''}</p>
                            </div>
                        </div>
                        <div class="flex items-center gap-2">
                            <div class="text-center px-4 py-2 bg-danger-light rounded-lg">
                                <span class="text-xs uppercase font-bold text-danger block">Blood Group</span>
                                <span class="text-xl font-extrabold text-danger">${blood}</span>
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md-cols-2 gap-4 my-4 p-4 bg-secondary-light rounded-lg">
                        <div>
                            <div class="flex items-center gap-2 mb-1">
                                <i data-lucide="alert-circle" size="18" class="text-danger"></i>
                                <span class="font-bold text-sm text-danger">Allergies & Reactions:</span>
                            </div>
                            <p class="text-sm text-main font-medium pl-6">${allergies}</p>
                        </div>
                        <div>
                            <div class="flex items-center gap-2 mb-1">
                                <i data-lucide="activity" size="18" class="text-warning"></i>
                                <span class="font-bold text-sm text-warning">Chronic Conditions:</span>
                            </div>
                            <p class="text-sm text-main font-medium pl-6">${conditions}</p>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md-cols-2 gap-4 mt-4 pt-4 border-t border-border-color">
                        <div>
                            <span class="text-xs text-secondary uppercase font-semibold block mb-1">Emergency Contact</span>
                            <div class="flex items-center gap-2">
                                <i data-lucide="phone-call" size="16" class="text-success"></i>
                                <span class="font-bold text-main">${contactName}</span>
                                ${phone ? `
                                    <a href="tel:${phone}" class="btn btn-sm btn-outline-success ml-2">
                                        <i data-lucide="phone" size="14"></i> ${phone}
                                    </a>
                                ` : '<span class="text-xs text-secondary">(No phone)</span>'}
                            </div>
                        </div>
                        <div>
                            ${notes ? `
                                <span class="text-xs text-secondary uppercase font-semibold block mb-1">Critical Notes</span>
                                <p class="text-sm text-secondary">${notes}</p>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        if (window.lucide) lucide.createIcons();
    }

    memberFilter?.addEventListener('change', renderCards);

    await loadEmergencyData();
});