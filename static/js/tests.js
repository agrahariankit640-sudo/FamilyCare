document.addEventListener('DOMContentLoaded', async () => {
    let currentFilter = 'All';
    let familyMembers = [];
    let testsList = [];

    const testsTableBody = document.getElementById('tests-list');
    const emptyState = document.getElementById('tests-empty');
    const memberFilter = document.getElementById('filter-member');
    const dateFromFilter = document.getElementById('filter-date-from');
    const dateToFilter = document.getElementById('filter-date-to');
    const tabLinks = document.querySelectorAll('#test-tabs .tab-link');
    const testModalMemberSelect = document.getElementById('member_id');
    const testForm = document.getElementById('test-form');

    // Load family members for selects
    async function loadMembers() {
        try {
            const members = await API.familyMembers.list();
            familyMembers = Array.isArray(members) ? members : [];

            if (memberFilter) {
                memberFilter.innerHTML = '<option value="">All Family Members</option>' +
                    familyMembers.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
            }
            if (testModalMemberSelect) {
                testModalMemberSelect.innerHTML = '<option value="">Select Member</option>' +
                    familyMembers.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
            }
        } catch (err) {
            console.error('Error loading members:', err);
        }
    }

    // Load tests
    async function loadTests() {
        if (!testsTableBody) return;
        testsTableBody.innerHTML = '<tr><td colspan="6" class="text-center py-6 text-secondary"><i data-lucide="loader" class="spin mb-2"></i><p>Loading lab tests...</p></td></tr>';
        if (window.lucide) lucide.createIcons();

        try {
            const params = {};
            if (currentFilter && currentFilter !== 'All') {
                params.filter = currentFilter;
            }
            if (memberFilter && memberFilter.value) {
                params.family_member_id = memberFilter.value;
            }

            const data = await API.tests.list(params);
            testsList = Array.isArray(data) ? data : [];

            renderTable();
        } catch (err) {
            console.error('Error loading tests:', err);
            testsTableBody.innerHTML = '<tr><td colspan="6" class="text-center py-6 text-danger">Failed to load tests.</td></tr>';
            App.toast.show('Error loading tests', 'error');
        }
    }

    // Filter and render table
    function renderTable() {
        const fromDate = dateFromFilter ? dateFromFilter.value : null;
        const toDate = dateToFilter ? dateToFilter.value : null;

        let filtered = testsList.filter(t => {
            if (fromDate && t.test_date && t.test_date < fromDate) return false;
            if (toDate && t.test_date && t.test_date > toDate) return false;
            return true;
        });

        if (filtered.length === 0) {
            testsTableBody.innerHTML = '<tr><td colspan="6" class="text-center py-8 text-secondary">No tests found matching criteria.</td></tr>';
            if (emptyState && testsList.length === 0) {
                emptyState.classList.remove('hidden');
                document.querySelector('.table-container')?.classList.add('hidden');
            }
            return;
        }

        if (emptyState) emptyState.classList.add('hidden');
        document.querySelector('.table-container')?.classList.remove('hidden');

        testsTableBody.innerHTML = filtered.map(t => {
            const formattedDate = t.test_date ? App.date.format(t.test_date) : '-';
            const followUpDate = t.follow_up_date ? App.date.format(t.follow_up_date) : '-';
            const isFollowUpOverdue = t.follow_up_date && new Date(t.follow_up_date) < new Date();
            const memberName = t.member_name || (familyMembers.find(m => m.id === t.family_member_id)?.name || 'Member');

            return `
                <tr>
                    <td class="font-medium">
                        <div class="font-semibold text-main">${t.test_name || 'Lab Test'}</div>
                        ${t.doctor ? `<span class="text-xs text-secondary">By: ${t.doctor}</span>` : ''}
                    </td>
                    <td>
                        <span class="badge badge-info">${memberName}</span>
                    </td>
                    <td>${formattedDate}</td>
                    <td class="max-w-xs truncate" title="${t.result_summary || ''}">${t.result_summary || '<span class="text-secondary">-</span>'}</td>
                    <td>
                        ${t.follow_up_date ? `
                            <span class="${isFollowUpOverdue ? 'text-danger font-medium' : 'text-main'}">
                                ${followUpDate} ${isFollowUpOverdue ? '(Due)' : ''}
                            </span>
                        ` : '<span class="text-secondary">None</span>'}
                    </td>
                    <td>
                        <div class="flex items-center gap-2">
                            <button class="btn btn-sm btn-outline-primary p-2" title="Edit" onclick="editTestItem(${t.id})">
                                <i data-lucide="edit-2" size="14"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger p-2" title="Delete" onclick="deleteTestItem(${t.id})">
                                <i data-lucide="trash-2" size="14"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        if (window.lucide) lucide.createIcons();
    }

    // Filter listeners
    memberFilter?.addEventListener('change', loadTests);
    dateFromFilter?.addEventListener('change', renderTable);
    dateToFilter?.addEventListener('change', renderTable);

    // Tab buttons
    tabLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            tabLinks.forEach(l => {
                l.classList.remove('active', 'border-b-2', 'border-primary');
                l.classList.add('text-secondary');
            });
            link.classList.add('active', 'border-b-2', 'border-primary');
            link.classList.remove('text-secondary');
            currentFilter = link.dataset.filter;
            loadTests();
        });
    });

    // Add buttons
    document.querySelectorAll('#btn-add-test, .btn-add-test').forEach(btn => {
        btn.addEventListener('click', () => {
            if (testForm) {
                testForm.reset();
                document.getElementById('test_id').value = '';
                document.getElementById('modal-title').textContent = 'Add Test/Follow-up';
                document.getElementById('test_date').value = new Date().toISOString().split('T')[0];
            }
            App.modal.open('test-modal');
        });
    });

    // Form submit
    if (testForm) {
        testForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('test_id').value;
            const payload = {
                family_member_id: parseInt(document.getElementById('member_id').value),
                test_name: document.getElementById('test_name').value.trim(),
                test_date: document.getElementById('test_date').value,
                doctor: document.getElementById('doctor')?.value?.trim() || '',
                result_summary: document.getElementById('result_summary')?.value?.trim() || '',
                follow_up_date: document.getElementById('follow_up_date')?.value || null,
                notes: document.getElementById('notes')?.value?.trim() || ''
            };

            if (!payload.family_member_id || !payload.test_name || !payload.test_date) {
                App.toast.show('Please fill in all required fields', 'warning');
                return;
            }

            try {
                if (id) {
                    await API.tests.update(id, payload);
                    App.toast.show('Test updated successfully', 'success');
                } else {
                    await API.tests.create(payload);
                    App.toast.show('Test recorded successfully', 'success');
                }
                App.modal.close('test-modal');
                loadTests();
            } catch (err) {
                console.error('Error saving test:', err);
                App.toast.show(err.message || 'Error saving test', 'error');
            }
        });
    }

    // Edit test
    window.editTestItem = async (id) => {
        try {
            const res = await API.tests.get(id);
            const t = res.data || res;
            if (!t) return;

            document.getElementById('test_id').value = t.id;
            document.getElementById('member_id').value = t.family_member_id || '';
            document.getElementById('test_name').value = t.test_name || '';
            document.getElementById('test_date').value = t.test_date || '';
            document.getElementById('doctor').value = t.doctor || '';
            document.getElementById('result_summary').value = t.result_summary || '';
            document.getElementById('follow_up_date').value = t.follow_up_date || '';
            document.getElementById('notes').value = t.notes || '';
            document.getElementById('modal-title').textContent = 'Edit Test/Follow-up';

            App.modal.open('test-modal');
        } catch (err) {
            console.error('Error fetching test:', err);
            App.toast.show('Failed to load test details', 'error');
        }
    };

    // Delete test
    window.deleteTestItem = async (id) => {
        if (await App.confirm('Are you sure you want to delete this lab test?')) {
            try {
                await API.tests.delete(id);
                App.toast.show('Test deleted', 'success');
                loadTests();
            } catch (err) {
                console.error('Error deleting test:', err);
                App.toast.show('Failed to delete test', 'error');
            }
        }
    };

    await loadMembers();
    await loadTests();
});