document.addEventListener('DOMContentLoaded', () => {
    let allUsers = [];
    let allLogs = [];

    // Elements
    const statUsers = document.getElementById('admin-stat-users');
    const statProfiles = document.getElementById('admin-stat-profiles');
    const statRecords = document.getElementById('admin-stat-records');
    const statDocs = document.getElementById('admin-stat-docs');

    const usersList = document.getElementById('admin-users-list');
    const auditList = document.getElementById('admin-audit-list');
    const searchUserInput = document.getElementById('admin-search-user');
    const filterActionSelect = document.getElementById('admin-filter-action');
    const adminTabs = document.querySelectorAll('#admin-tabs .tab-link');

    // Tab switching
    if (adminTabs.length > 0) {
        adminTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const targetTab = tab.getAttribute('data-tab');
                
                adminTabs.forEach(t => {
                    t.classList.remove('active', 'border-b-2', 'border-primary', 'text-primary');
                    t.classList.add('text-secondary');
                });
                tab.classList.add('active', 'border-b-2', 'border-primary', 'text-primary');
                tab.classList.remove('text-secondary');

                const usersSec = document.getElementById('users-section');
                const auditSec = document.getElementById('audit-section');
                if (targetTab === 'users') {
                    if (usersSec) usersSec.classList.remove('hidden');
                    if (auditSec) auditSec.classList.add('hidden');
                } else if (targetTab === 'audit') {
                    if (usersSec) usersSec.classList.add('hidden');
                    if (auditSec) auditSec.classList.remove('hidden');
                    loadAuditLogs();
                }
            });
        });
    }

    async function loadStats() {
        try {
            const res = await API.admin.stats();
            const data = (res && res.data) ? res.data : (res || {});
            if (statUsers) statUsers.textContent = data.users !== undefined ? data.users : (data.totalUsers || 0);
            if (statProfiles) statProfiles.textContent = data.profiles !== undefined ? data.profiles : 0;
            if (statRecords) statRecords.textContent = data.records !== undefined ? data.records : 0;
            if (statDocs) statDocs.textContent = data.docs !== undefined ? data.docs : 0;
        } catch (err) {
            console.error('Failed to load stats:', err);
        }
    }

    async function loadUsers() {
        if (!usersList) return;
        usersList.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-secondary">Loading users...</td></tr>';
        try {
            const res = await API.admin.users();
            allUsers = Array.isArray(res) ? res : (res && res.data ? res.data : []);
            renderUsers(allUsers);
        } catch (err) {
            console.error('Failed to load users:', err);
            usersList.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-danger">Failed to load users or access denied.</td></tr>';
        }
    }

    function renderUsers(users) {
        if (!usersList) return;
        if (!users || users.length === 0) {
            usersList.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-secondary">No users found.</td></tr>';
            return;
        }

        usersList.innerHTML = users.map(u => {
            const isActive = (u.is_active === 1 || u.is_active === true || u.status === 'Active');
            const statusBadge = isActive 
                ? '<span class="badge badge-success text-xs">Active</span>' 
                : '<span class="badge badge-danger text-xs">Disabled</span>';
            const roleBadge = u.role === 'admin' 
                ? '<span class="badge badge-primary text-xs font-semibold">Admin</span>' 
                : '<span class="badge text-xs">User</span>';
            const dateStr = u.created_at ? App.date.format(u.created_at) : '-';

            return `
                <tr>
                    <td class="font-mono text-xs text-secondary">#${u.id}</td>
                    <td class="font-medium">${App.utils.escapeHtml(u.name || '')}</td>
                    <td class="text-secondary">${App.utils.escapeHtml(u.email || '')}</td>
                    <td>${roleBadge}</td>
                    <td class="text-secondary text-sm">${dateStr}</td>
                    <td>${statusBadge}</td>
                    <td>
                        <button type="button" class="btn btn-sm ${isActive ? 'btn-outline-danger' : 'btn-outline-success'}" 
                                onclick="toggleUserStatus(${u.id}, ${isActive})">
                            ${isActive ? 'Disable' : 'Enable'}
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    async function loadAuditLogs(action = '') {
        if (!auditList) return;
        auditList.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-secondary">Loading audit logs...</td></tr>';
        try {
            let res;
            if (action) {
                res = await API.get(`/admin/activity-log?action=${encodeURIComponent(action)}`);
            } else {
                res = await API.admin.activityLog();
            }
            allLogs = Array.isArray(res) ? res : (res && res.data ? res.data : []);
            renderAuditLogs(allLogs);
        } catch (err) {
            console.error('Failed to load audit logs:', err);
            auditList.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-danger">Failed to load audit logs.</td></tr>';
        }
    }

    function renderAuditLogs(logs) {
        if (!auditList) return;
        if (!logs || logs.length === 0) {
            auditList.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-secondary">No activity logs recorded.</td></tr>';
            return;
        }

        auditList.innerHTML = logs.map(l => {
            const timeStr = l.created_at ? App.date.format(l.created_at, 'MMM D, YYYY HH:mm') : '-';
            const actionClass = l.action.includes('delete') ? 'badge-danger' 
                : (l.action.includes('create') ? 'badge-success' 
                : (l.action.includes('update') ? 'badge-warning' : 'badge-info'));
            return `
                <tr>
                    <td class="text-xs text-secondary whitespace-nowrap">${timeStr}</td>
                    <td class="font-mono text-xs">User #${l.user_id || 'System'}</td>
                    <td><span class="badge ${actionClass} text-xs">${App.utils.escapeHtml(l.action || '')}</span></td>
                    <td class="font-mono text-xs text-secondary">${App.utils.escapeHtml(l.entity_type || '-')}</td>
                    <td class="text-xs">${l.entity_id ? '#' + l.entity_id : '-'}</td>
                    <td class="font-mono text-xs text-secondary">${App.utils.escapeHtml(l.ip_address || '-')}</td>
                </tr>
            `;
        }).join('');
    }

    // Search filter for users
    if (searchUserInput) {
        searchUserInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            if (!query) {
                renderUsers(allUsers);
                return;
            }
            const filtered = allUsers.filter(u => 
                (u.name && u.name.toLowerCase().includes(query)) ||
                (u.email && u.email.toLowerCase().includes(query)) ||
                (u.role && u.role.toLowerCase().includes(query))
            );
            renderUsers(filtered);
        });
    }

    // Action filter for audit logs
    if (filterActionSelect) {
        filterActionSelect.addEventListener('change', (e) => {
            loadAuditLogs(e.target.value);
        });
    }

    // Global toggle function
    window.toggleUserStatus = async (id, currentlyActive) => {
        const actionStr = currentlyActive ? 'disable' : 'enable';
        if (await App.confirm(`Are you sure you want to ${actionStr} this user account?`)) {
            try {
                App.loading.show();
                await API.admin.setUserStatus(id, !currentlyActive);
                App.toast.show(`User successfully ${currentlyActive ? 'disabled' : 'enabled'}.`, 'success');
                await loadUsers();
            } catch (err) {
                App.toast.show(err.message || 'Failed to update user status.', 'error');
            } finally {
                App.loading.hide();
            }
        }
    };

    // Initialize
    loadStats();
    loadUsers();
    if (window.lucide) lucide.createIcons();
});