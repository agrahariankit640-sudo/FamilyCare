document.addEventListener('DOMContentLoaded', async () => {
    let familyMembers = [];
    const timelineEvents = document.getElementById('timeline-events');
    const timelineEmpty = document.getElementById('timeline-empty');
    const memberFilter = document.getElementById('filter-member');
    const typeFilter = document.getElementById('filter-type');
    const dateFromFilter = document.getElementById('filter-date-from');
    const dateToFilter = document.getElementById('filter-date-to');

    // Load family members
    async function loadMembers() {
        try {
            const members = await API.familyMembers.list();
            familyMembers = Array.isArray(members) ? members : [];
            if (memberFilter) {
                memberFilter.innerHTML = '<option value="">All Family Members</option>' +
                    familyMembers.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
            }
        } catch (err) {
            console.error('Error loading members for timeline:', err);
        }
    }

    // Load timeline events
    async function loadTimeline() {
        if (!timelineEvents) return;
        timelineEvents.innerHTML = `
            <div class="loading-state text-center py-8">
                <i data-lucide="loader" class="spin mb-2"></i>
                <p>Building timeline...</p>
            </div>
        `;
        if (window.lucide) lucide.createIcons();

        try {
            const params = {};
            if (memberFilter && memberFilter.value) {
                params.family_member_id = memberFilter.value;
            }
            if (typeFilter && typeFilter.value) {
                params.type = typeFilter.value;
            }
            if (dateFromFilter && dateFromFilter.value) {
                params.date_from = dateFromFilter.value;
            }
            if (dateToFilter && dateToFilter.value) {
                params.date_to = dateToFilter.value;
            }

            const res = await API.timeline.get(params);
            const events = Array.isArray(res) ? res : [];

            if (events.length === 0) {
                timelineEvents.innerHTML = '';
                if (timelineEmpty) timelineEmpty.classList.remove('hidden');
                return;
            }

            if (timelineEmpty) timelineEmpty.classList.add('hidden');

            const typeMeta = {
                record: { icon: 'file-text', color: 'badge-info', label: 'Record' },
                medicine: { icon: 'pill', color: 'badge-primary', label: 'Medicine' },
                appointment: { icon: 'calendar', color: 'badge-warning', label: 'Visit' },
                test: { icon: 'flask-conical', color: 'badge-success', label: 'Lab Test' },
                vaccination: { icon: 'syringe', color: 'badge-danger', label: 'Vaccine' }
            };

            timelineEvents.innerHTML = events.map(e => {
                const meta = typeMeta[e.type] || { icon: 'activity', color: 'badge-secondary', label: e.type };
                const formattedDate = e.date ? App.date.format(e.date) : 'Undated';

                return `
                    <div class="timeline-item mb-6 relative md:pl-16 pl-6 cursor-pointer" onclick="window.location.href='${e.link}'">
                        <div class="timeline-badge absolute left-0 md:left-5 top-1 bg-white border-2 border-primary rounded-full p-2 shadow-sm text-primary">
                            <i data-lucide="${meta.icon}" size="18"></i>
                        </div>
                        <div class="card p-4 hover-shadow transition-shadow">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <h4 class="font-bold text-main text-base">${e.title}</h4>
                                    <span class="text-xs text-secondary">For: <strong>${e.member_name}</strong></span>
                                </div>
                                <div class="flex items-center gap-2">
                                    <span class="badge ${meta.color} text-xs uppercase">${meta.label}</span>
                                    <span class="text-xs text-secondary font-medium">${formattedDate}</span>
                                </div>
                            </div>
                            <p class="text-sm text-secondary mb-2">${e.description || ''}</p>
                            ${e.doctor ? `<div class="text-xs text-secondary flex items-center gap-1"><i data-lucide="user" size="12"></i> ${e.doctor}</div>` : ''}
                        </div>
                    </div>
                `;
            }).join('');

            if (window.lucide) lucide.createIcons();
        } catch (err) {
            console.error('Error loading timeline:', err);
            timelineEvents.innerHTML = `
                <div class="text-center py-8 text-danger">
                    <p>Failed to load timeline events. Please try again.</p>
                </div>
            `;
            App.toast.show('Error loading timeline', 'error');
        }
    }

    // Event listeners
    memberFilter?.addEventListener('change', loadTimeline);
    typeFilter?.addEventListener('change', loadTimeline);
    dateFromFilter?.addEventListener('change', loadTimeline);
    dateToFilter?.addEventListener('change', loadTimeline);

    await loadMembers();
    await loadTimeline();
});