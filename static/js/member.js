document.addEventListener('DOMContentLoaded', async () => {
    // Resolve memberId from path (/member/123) or query string (?id=123)
    let memberId = null;
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    const lastPart = pathParts[pathParts.length - 1];
    if (lastPart && /^\d+$/.test(lastPart)) {
        memberId = lastPart;
    } else {
        const urlParams = new URLSearchParams(window.location.search);
        memberId = urlParams.get('id') || urlParams.get('member_id');
    }

    if (!memberId) {
        // Fallback: fetch first family member
        try {
            const members = await API.familyMembers.list();
            if (Array.isArray(members) && members.length > 0) {
                memberId = members[0].id;
            } else {
                document.getElementById('member-name').textContent = 'No Family Member Found';
                return;
            }
        } catch (err) {
            console.error('Error fetching members:', err);
            return;
        }
    }

    async function loadMemberDetails() {
        try {
            const [memberRes, summaryRes] = await Promise.all([
                API.familyMembers.get(memberId),
                API.familyMembers.summary(memberId)
            ]);

            const member = memberRes.data || memberRes;
            const summary = summaryRes.data || summaryRes || {};

            if (!member) {
                document.getElementById('member-name').textContent = 'Member Not Found';
                return;
            }

            // Calculate age
            let ageStr = '-';
            if (member.date_of_birth) {
                const dob = new Date(member.date_of_birth);
                const diff = Date.now() - dob.getTime();
                const ageDate = new Date(diff);
                ageStr = Math.abs(ageDate.getUTCFullYear() - 1970);
            }

            // Set info
            const nameEl = document.getElementById('member-name');
            if (nameEl) nameEl.textContent = member.name || 'Family Member';

            const pageTitleEl = document.getElementById('member-page-title');
            if (pageTitleEl) pageTitleEl.textContent = `${member.name || 'Member'}'s Health Profile`;

            const avatarEl = document.getElementById('member-avatar-initial');
            if (avatarEl) avatarEl.textContent = (member.name ? member.name.charAt(0) : 'M').toUpperCase();

            const relEl = document.getElementById('member-relationship');
            if (relEl) relEl.textContent = member.relationship || 'Member';

            const ageEl = document.getElementById('member-age');
            if (ageEl) ageEl.textContent = ageStr;

            const bloodEl = document.getElementById('member-blood');
            if (bloodEl) bloodEl.textContent = member.blood_group || member.bloodGroup || 'Unknown';

            const allergiesEl = document.getElementById('member-allergies');
            if (allergiesEl) allergiesEl.textContent = member.allergies || 'None reported';

            const condEl = document.getElementById('member-conditions');
            if (condEl) condEl.textContent = member.existing_conditions || member.conditions || 'None reported';

            // Summary metrics
            const bpEl = document.getElementById('summary-bp');
            if (bpEl) bpEl.textContent = summary.bp || '--/--';

            const medsEl = document.getElementById('summary-meds');
            if (medsEl) medsEl.textContent = `${summary.active_medicines || 0} active`;

            const apptEl = document.getElementById('summary-appt');
            if (apptEl) apptEl.textContent = summary.next_appointment || 'None scheduled';

            const testsEl = document.getElementById('summary-tests');
            if (testsEl) testsEl.textContent = `${summary.tests_count || 0} recorded`;

            // Update module navigation links to pass member filter
            const linkMap = {
                'link-records': `/records?family_member_id=${memberId}`,
                'link-medicines': `/medicines?family_member_id=${memberId}`,
                'link-appointments': `/appointments?family_member_id=${memberId}`,
                'link-tests': `/tests?family_member_id=${memberId}`,
                'link-vaccinations': `/vaccinations?family_member_id=${memberId}`,
                'link-tracker': `/health-tracker?family_member_id=${memberId}`,
                'link-timeline': `/timeline?family_member_id=${memberId}`,
                'link-expenses': `/expenses?family_member_id=${memberId}`,
                'link-insurance': `/insurance?family_member_id=${memberId}`
            };

            for (const [id, url] of Object.entries(linkMap)) {
                const el = document.getElementById(id);
                if (el) el.href = url;
            }

            if (window.lucide) lucide.createIcons();
        } catch (err) {
            console.error('Error loading member profile:', err);
            App.toast.show('Failed to load member profile', 'error');
        }
    }

    document.getElementById('btn-edit-profile')?.addEventListener('click', () => {
        window.location.href = `/family`;
    });

    await loadMemberDetails();
});