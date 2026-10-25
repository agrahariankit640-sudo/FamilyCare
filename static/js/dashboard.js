document.addEventListener('DOMContentLoaded', async () => {
    async function loadDashboard() {
        try {
            // 1. Load summary stats
            const summary = await API.dashboard.summary();
            if (summary) {
                const totalFam = summary.total_family_members ?? summary.totalMembers ?? 0;
                const activeMeds = summary.active_medicines ?? summary.activeMedicines ?? 0;
                const upcomingVisits = summary.upcoming_appointments ?? summary.upcomingVisits ?? 0;
                const followups = summary.pending_followups ?? summary.pendingFollowups ?? 0;

                const famEl = document.querySelector('#stat-family-count');
                const medEl = document.querySelector('#stat-medicines-count');
                const apptEl = document.querySelector('#stat-appts-count');
                const fupEl = document.querySelector('#stat-followups-count');

                if (famEl) famEl.textContent = totalFam;
                if (medEl) medEl.textContent = activeMeds;
                if (apptEl) apptEl.textContent = upcomingVisits;
                if (fupEl) fupEl.textContent = followups;
            }

            // 2. Load recent activity
            const activityList = document.querySelector('#dashboard-activity-list') || document.querySelector('#recent-activity');
            if (activityList) {
                try {
                    const recentActivity = await API.dashboard.recentActivity();
                    const list = Array.isArray(recentActivity) ? recentActivity : (recentActivity && recentActivity.data ? recentActivity.data : []);
                    if (!list || list.length === 0) {
                        activityList.innerHTML = '<li class="text-secondary py-3 text-center">No recent activity</li>';
                    } else {
                        activityList.innerHTML = list.map(a => `
                            <li class="py-2 border-b border-border-color flex justify-between items-center text-sm">
                                <div>
                                    <span class="font-medium">${a.details || a.action || a.description || 'System Activity'}</span>
                                </div>
                                <span class="text-xs text-secondary">${App.date.formatRelativeTime(a.created_at || a.date)}</span>
                            </li>
                        `).join('');
                    }
                } catch (e) {
                    activityList.innerHTML = '<li class="text-secondary py-3 text-center">No activity found</li>';
                }
            }

            // 3. Load upcoming events
            const eventsList = document.querySelector('#dashboard-upcoming-events') || document.querySelector('#upcoming-events');
            if (eventsList) {
                try {
                    const upcomingEvents = await API.dashboard.upcoming();
                    const list = Array.isArray(upcomingEvents) ? upcomingEvents : (upcomingEvents && upcomingEvents.data ? upcomingEvents.data : []);
                    if (!list || list.length === 0) {
                        eventsList.innerHTML = '<div class="text-secondary py-4 text-center">No upcoming events scheduled</div>';
                    } else {
                        eventsList.innerHTML = list.map(e => `
                            <div class="py-2 border-b border-border-color flex justify-between items-center text-sm">
                                <div>
                                    <p class="font-medium mb-0">${e.title || 'Event'}</p>
                                    ${e.member ? `<span class="text-xs text-secondary">${e.member}</span>` : ''}
                                </div>
                                <span class="badge badge-primary text-xs">${App.date.format(e.date)}</span>
                            </div>
                        `).join('');
                    }
                } catch (e) {
                    eventsList.innerHTML = '<div class="text-secondary py-4 text-center">No upcoming events</div>';
                }
            }

            // 4. Render Charts if Chart.js is present
            if (window.Chart) {
                const vitalsCanvas = document.getElementById('healthTrendsChart');
                if (vitalsCanvas) {
                    new Chart(vitalsCanvas, {
                        type: 'line',
                        data: {
                            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                            datasets: [{
                                label: 'Systolic BP',
                                data: [120, 122, 118, 121, 119, 120, 118],
                                borderColor: '#0284c7',
                                backgroundColor: 'rgba(2, 132, 199, 0.1)',
                                tension: 0.3
                            }, {
                                label: 'Diastolic BP',
                                data: [80, 82, 79, 80, 78, 80, 79],
                                borderColor: '#0d9488',
                                backgroundColor: 'rgba(13, 148, 136, 0.1)',
                                tension: 0.3
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { position: 'bottom' } }
                        }
                    });
                }

                const expenseCanvas = document.getElementById('expenseChart');
                if (expenseCanvas) {
                    new Chart(expenseCanvas, {
                        type: 'doughnut',
                        data: {
                            labels: ['Doctor Visits', 'Medicines', 'Tests', 'Dental', 'Other'],
                            datasets: [{
                                data: [4500, 2200, 1800, 1200, 800],
                                backgroundColor: ['#0284c7', '#10b981', '#f59e0b', '#8b5cf6', '#64748b']
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { position: 'bottom' } }
                        }
                    });
                }
            }

            if (typeof lucide !== 'undefined' && lucide.createIcons) {
                lucide.createIcons();
            }

        } catch (error) {
            console.error('Failed to load dashboard:', error);
            App.toast.show('Failed to load dashboard summary', 'error');
        }
    }

    await loadDashboard();
});