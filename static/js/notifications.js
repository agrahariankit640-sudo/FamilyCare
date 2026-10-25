document.addEventListener('DOMContentLoaded', async () => {
    let currentFilter = 'all';
    let allNotifications = [];

    const container = document.getElementById('notifications-container');
    const emptyState = document.getElementById('notifications-empty');
    const markAllBtn = document.getElementById('btn-mark-all-read');
    const tabLinks = document.querySelectorAll('#notification-tabs .tab-link');
    const unreadCountTab = document.getElementById('unread-count-tab');

    async function loadNotifications() {
        if (!container) return;

        try {
            const res = await API.notifications.list();
            allNotifications = Array.isArray(res) ? res : [];

            // Update unread count badge
            const unreadCount = allNotifications.filter(n => !n.is_read).length;
            if (unreadCountTab) {
                unreadCountTab.textContent = unreadCount;
                unreadCountTab.style.display = unreadCount > 0 ? 'inline-block' : 'none';
            }

            renderNotifications();
        } catch (err) {
            console.error('Error loading notifications:', err);
            container.innerHTML = '<div class="text-center py-6 text-danger">Failed to load notifications.</div>';
            App.toast.show('Error loading notifications', 'error');
        }
    }

    function renderNotifications() {
        if (!container) return;

        const filtered = currentFilter === 'unread'
            ? allNotifications.filter(n => !n.is_read)
            : allNotifications;

        if (filtered.length === 0) {
            container.innerHTML = '';
            if (emptyState) emptyState.classList.remove('hidden');
            return;
        }

        if (emptyState) emptyState.classList.add('hidden');

        const typeIcons = {
            reminder: 'bell',
            appointment: 'calendar',
            test: 'flask-conical',
            vaccination: 'syringe',
            general: 'info'
        };

        container.innerHTML = filtered.map(n => {
            const isUnread = !n.is_read;
            const icon = typeIcons[(n.type || '').toLowerCase()] || 'bell';
            const dateStr = n.created_at ? App.date.format(n.created_at) : '';

            return `
                <div class="notification-item flex items-start justify-between p-4 border-b border-border-color ${isUnread ? 'bg-primary-light bg-opacity-10' : ''} hover:bg-secondary-light transition-colors">
                    <div class="flex items-start gap-3 flex-1">
                        <div class="p-2 rounded-full ${isUnread ? 'bg-primary text-white' : 'bg-secondary-light text-secondary'} mt-1">
                            <i data-lucide="${icon}" size="16"></i>
                        </div>
                        <div class="flex-1">
                            <div class="flex items-center gap-2 mb-1">
                                <h4 class="font-bold text-main ${isUnread ? 'text-primary' : ''}">${n.title}</h4>
                                ${isUnread ? '<span class="badge badge-primary text-xs">New</span>' : ''}
                            </div>
                            <p class="text-sm text-secondary mb-1">${n.message || ''}</p>
                            <span class="text-xs text-secondary">${dateStr}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-2 ml-4">
                        ${isUnread ? `
                            <button class="btn btn-sm btn-outline-primary" title="Mark as Read" onclick="markNotificationRead(${n.id})">
                                <i data-lucide="check" size="14"></i>
                            </button>
                        ` : ''}
                        <button class="btn btn-sm btn-outline-danger p-2" title="Delete" onclick="deleteNotificationItem(${n.id})">
                            <i data-lucide="trash-2" size="14"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        if (window.lucide) lucide.createIcons();
    }

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
            currentFilter = link.dataset.filter || 'all';
            renderNotifications();
        });
    });

    // Mark all read
    markAllBtn?.addEventListener('click', async () => {
        try {
            await API.notifications.markAllRead();
            App.toast.show('All notifications marked as read', 'success');
            await loadNotifications();
        } catch (err) {
            console.error('Error marking all notifications read:', err);
            App.toast.show('Failed to update notifications', 'error');
        }
    });

    // Mark single notification read
    window.markNotificationRead = async (id) => {
        try {
            await API.notifications.markRead(id);
            await loadNotifications();
        } catch (err) {
            console.error('Error marking read:', err);
        }
    };

    // Delete single notification
    window.deleteNotificationItem = async (id) => {
        try {
            await API.notifications.delete(id);
            await loadNotifications();
        } catch (err) {
            console.error('Error deleting notification:', err);
            App.toast.show('Failed to delete notification', 'error');
        }
    };

    await loadNotifications();
});