document.addEventListener('DOMContentLoaded', async () => {
    let currentParam = 'Blood Pressure';
    let currentMember = null;
    let chartInstance = null;
    let familyMembers = [];

    const memberSelect = document.getElementById('filter-member');
    const modalMemberSelect = document.getElementById('member_id');
    const paramButtons = document.querySelectorAll('#parameter-tabs button');
    const chartTitle = document.getElementById('chart-title');
    const chartEmpty = document.getElementById('chart-empty');
    const chartCanvas = document.getElementById('healthChart');
    const readingsList = document.getElementById('readings-list');
    const readingForm = document.getElementById('reading-form');
    const addReadingBtn = document.getElementById('btn-add-reading');

    // Load family members
    async function loadMembers() {
        try {
            const members = await API.familyMembers.list();
            familyMembers = Array.isArray(members) ? members : [];

            if (memberSelect) {
                if (familyMembers.length === 0) {
                    memberSelect.innerHTML = '<option value="">No family members found</option>';
                } else {
                    memberSelect.innerHTML = familyMembers.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
                    currentMember = familyMembers[0].id;
                }
            }

            if (modalMemberSelect) {
                modalMemberSelect.innerHTML = familyMembers.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
            }

            if (currentMember) {
                await loadData();
            } else {
                if (readingsList) {
                    readingsList.innerHTML = '<tr><td colspan="2" class="text-center py-4 text-secondary">Please add a family member first.</td></tr>';
                }
                showEmptyChart(true);
            }
        } catch (err) {
            console.error('Error loading members in health tracker:', err);
        }
    }

    // Load data and trends
    async function loadData() {
        if (!currentMember) return;

        if (readingsList) {
            readingsList.innerHTML = '<tr><td colspan="2" class="text-center py-4 text-secondary">Loading readings...</td></tr>';
        }

        try {
            const [readingsRes, trendsRes] = await Promise.all([
                API.healthParams.list({ member_id: currentMember, parameter: currentParam }),
                API.healthParams.trends({ member_id: currentMember, parameter: currentParam })
            ]);

            const readings = Array.isArray(readingsRes) ? readingsRes : [];
            const trends = Array.isArray(trendsRes) ? trendsRes : [];

            renderReadings(readings);
            renderChart(trends);
        } catch (err) {
            console.error('Error loading health tracker data:', err);
            if (readingsList) {
                readingsList.innerHTML = '<tr><td colspan="2" class="text-center py-4 text-danger">Failed to load readings</td></tr>';
            }
            showEmptyChart(true);
        }
    }

    function renderReadings(readings) {
        if (!readingsList) return;

        if (readings.length === 0) {
            readingsList.innerHTML = '<tr><td colspan="2" class="text-center py-6 text-secondary">No readings recorded yet.</td></tr>';
            return;
        }

        readingsList.innerHTML = readings.map(r => {
            const formattedDate = r.record_date ? App.date.format(r.record_date) : '';
            const timeStr = r.record_time ? ` <span class="text-xs text-secondary">${r.record_time.substring(0, 5)}</span>` : '';
            return `
                <tr>
                    <td>
                        <div>${formattedDate}${timeStr}</div>
                        ${r.notes ? `<div class="text-xs text-secondary truncate max-w-xs">${r.notes}</div>` : ''}
                    </td>
                    <td class="text-right">
                        <span class="font-bold text-main">${r.value}</span>
                        <span class="text-xs text-secondary">${r.unit || ''}</span>
                        <button class="btn btn-sm text-danger ml-2 p-1" title="Delete" onclick="deleteReadingItem(${r.id})">
                            &times;
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    function showEmptyChart(show) {
        if (show) {
            if (chartEmpty) chartEmpty.classList.remove('hidden');
            if (chartCanvas) chartCanvas.style.display = 'none';
        } else {
            if (chartEmpty) chartEmpty.classList.add('hidden');
            if (chartCanvas) chartCanvas.style.display = 'block';
        }
    }

    function renderChart(trends) {
        if (!chartCanvas || typeof Chart === 'undefined') return;

        if (chartTitle) {
            chartTitle.textContent = `${currentParam} Trends`;
        }

        if (trends.length === 0) {
            if (chartInstance) {
                chartInstance.destroy();
                chartInstance = null;
            }
            showEmptyChart(true);
            return;
        }

        showEmptyChart(false);

        const labels = trends.map(t => t.record_date || '');

        let datasets = [];

        if (currentParam === 'Blood Pressure') {
            const systolic = [];
            const diastolic = [];

            trends.forEach(t => {
                const parts = String(t.value).split('/');
                if (parts.length === 2) {
                    systolic.push(parseFloat(parts[0]) || null);
                    diastolic.push(parseFloat(parts[1]) || null);
                } else {
                    systolic.push(parseFloat(t.value) || null);
                    diastolic.push(null);
                }
            });

            datasets = [
                {
                    label: 'Systolic (mmHg)',
                    data: systolic,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.3,
                    fill: false
                },
                {
                    label: 'Diastolic (mmHg)',
                    data: diastolic,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.3,
                    fill: false
                }
            ];
        } else {
            const values = trends.map(t => parseFloat(t.value) || 0);
            const unit = trends[0]?.unit || '';
            datasets = [
                {
                    label: `${currentParam} (${unit})`,
                    data: values,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.15)',
                    tension: 0.3,
                    fill: true
                }
            ];
        }

        if (chartInstance) {
            chartInstance.destroy();
        }

        const ctx = chartCanvas.getContext('2d');
        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }

    // Member change
    memberSelect?.addEventListener('change', (e) => {
        currentMember = e.target.value;
        loadData();
    });

    // Param buttons
    paramButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            paramButtons.forEach(b => {
                b.classList.remove('btn-primary');
                b.classList.add('btn-outline');
            });
            btn.classList.remove('btn-outline');
            btn.classList.add('btn-primary');
            currentParam = btn.dataset.param;

            // Also sync parameter type select inside modal
            const modalParamType = document.getElementById('parameter_type');
            if (modalParamType) {
                modalParamType.value = currentParam;
            }

            loadData();
        });
    });

    // Add reading
    addReadingBtn?.addEventListener('click', () => {
        if (readingForm) {
            readingForm.reset();
            if (modalMemberSelect && currentMember) {
                modalMemberSelect.value = currentMember;
            }
            const modalParamType = document.getElementById('parameter_type');
            if (modalParamType) {
                modalParamType.value = currentParam;
            }

            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            document.getElementById('reading_date').value = `${year}-${month}-${day}T${hours}:${minutes}`;
        }
        App.modal.open('reading-modal');
    });

    // Form submit
    if (readingForm) {
        readingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const memberId = document.getElementById('member_id').value;
            const paramType = document.getElementById('parameter_type').value;
            const val = document.getElementById('value').value.trim();
            const readingDate = document.getElementById('reading_date').value;
            const notes = document.getElementById('notes').value.trim();

            if (!memberId || !paramType || !val || !readingDate) {
                App.toast.show('Please fill in required fields', 'warning');
                return;
            }

            const payload = {
                family_member_id: parseInt(memberId),
                parameter_name: paramType,
                value: val,
                reading_date: readingDate,
                notes: notes
            };

            try {
                await API.healthParams.create(payload);
                App.toast.show('Health parameter recorded', 'success');
                App.modal.close('reading-modal');
                currentMember = memberId;
                if (memberSelect) memberSelect.value = currentMember;
                currentParam = paramType;
                paramButtons.forEach(b => {
                    if (b.dataset.param === currentParam) {
                        b.classList.remove('btn-outline');
                        b.classList.add('btn-primary');
                    } else {
                        b.classList.remove('btn-primary');
                        b.classList.add('btn-outline');
                    }
                });
                loadData();
            } catch (err) {
                console.error('Error saving reading:', err);
                App.toast.show(err.message || 'Error saving reading', 'error');
            }
        });
    }

    // Delete reading
    window.deleteReadingItem = async (id) => {
        if (await App.confirm('Are you sure you want to delete this reading?')) {
            try {
                await API.healthParams.delete(id);
                App.toast.show('Reading deleted', 'success');
                loadData();
            } catch (err) {
                console.error('Error deleting reading:', err);
                App.toast.show('Failed to delete reading', 'error');
            }
        }
    };

    await loadMembers();
});