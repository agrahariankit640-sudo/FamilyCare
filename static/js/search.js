document.addEventListener('DOMContentLoaded', async () => {
    let timeoutId;
    let familyMembers = [];

    const searchInput = document.getElementById('global-search-input');
    const clearBtn = document.getElementById('btn-clear-search');
    const resultsContainer = document.getElementById('search-results-container');
    const countEl = document.getElementById('search-results-count');
    const memberFilter = document.getElementById('filter-member');
    const applyFiltersBtn = document.getElementById('btn-apply-filters');
    const resetFiltersBtn = document.getElementById('btn-reset-filters');
    const sortSelect = document.getElementById('sort-results');
    const dateRangeSelect = document.getElementById('filter-date-range');
    const customDateFields = document.getElementById('custom-date-fields');

    // Load family members for filter
    async function loadMembers() {
        try {
            const members = await API.familyMembers.list();
            familyMembers = Array.isArray(members) ? members : [];
            if (memberFilter) {
                memberFilter.innerHTML = '<option value="">All Members</option>' +
                    familyMembers.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
            }
        } catch (err) {
            console.error('Error loading members for search:', err);
        }
    }

    // Toggle custom date range inputs
    dateRangeSelect?.addEventListener('change', () => {
        if (customDateFields) {
            if (dateRangeSelect.value === 'custom') {
                customDateFields.classList.remove('hidden');
            } else {
                customDateFields.classList.add('hidden');
            }
        }
    });

    async function performSearch(force = false) {
        if (!resultsContainer) return;
        const query = searchInput ? searchInput.value.trim() : '';

        if (clearBtn) {
            if (query) clearBtn.classList.remove('hidden');
            else clearBtn.classList.add('hidden');
        }

        const selectedMemberId = memberFilter ? memberFilter.value : '';
        const selectedDateRange = dateRangeSelect ? dateRangeSelect.value : '';

        // If no query and user hasn't explicitly clicked Apply Filters / selected a member, show initial guide
        if (!query && !selectedMemberId && !force && !selectedDateRange) {
            resultsContainer.innerHTML = `
                <div class="card p-12 text-center text-secondary">
                    <i data-lucide="search" size="48" class="mx-auto mb-4 opacity-40"></i>
                    <h4 class="font-semibold text-lg text-main mb-1">Search Your Health Records</h4>
                    <p>Type keywords above or use the filters on the left to browse records.</p>
                </div>
            `;
            if (countEl) countEl.textContent = 'Search Results';
            if (window.lucide) lucide.createIcons();
            return;
        }

        resultsContainer.innerHTML = `
            <div class="card p-10 text-center text-secondary">
                <i data-lucide="loader" class="spin mb-3 mx-auto" size="32"></i>
                <p class="font-medium">Searching records...</p>
            </div>
        `;
        if (window.lucide) lucide.createIcons();

        try {
            const params = {};
            if (query) params.q = query;
            if (selectedMemberId) params.family_member_id = selectedMemberId;

            const res = await API.search.query(params);
            const data = (res && res.data) ? res.data : (res || {});

            let allItems = [];

            // Module metadata mapping
            const metaMap = {
                medical_records: { label: 'Medical Record', badge: 'badge-info', link: '/records', icon: 'file-text', iconClass: 'record-icon' },
                records: { label: 'Medical Record', badge: 'badge-info', link: '/records', icon: 'file-text', iconClass: 'record-icon' },
                medicines: { label: 'Medicine', badge: 'badge-primary', link: '/medicines', icon: 'pill', iconClass: 'medicine-icon' },
                appointments: { label: 'Appointment', badge: 'badge-warning', link: '/appointments', icon: 'calendar', iconClass: 'appointment-icon' },
                tests: { label: 'Lab Test', badge: 'badge-success', link: '/tests', icon: 'flask-conical', iconClass: 'test-icon' },
                vaccinations: { label: 'Vaccination', badge: 'badge-danger', link: '/vaccinations', icon: 'syringe', iconClass: 'vaccination-icon' }
            };

            // Selected type filters
            const checkedBoxes = Array.from(document.querySelectorAll('input[name="type_filter"]:checked')).map(cb => cb.value);
            const activeTypes = new Set();
            checkedBoxes.forEach(v => {
                activeTypes.add(v);
                if (v === 'medical_records') activeTypes.add('records');
                if (v === 'records') activeTypes.add('medical_records');
            });

            for (const [key, items] of Object.entries(data)) {
                if (activeTypes.size > 0 && !activeTypes.has(key)) continue;
                if (Array.isArray(items)) {
                    items.forEach(item => {
                        allItems.push({
                            ...item,
                            categoryKey: key,
                            meta: metaMap[key] || { label: key, badge: 'badge-secondary', link: '#', icon: 'circle', iconClass: 'record-icon' }
                        });
                    });
                }
            }

            // Client-side member filter safety check
            if (selectedMemberId) {
                const selMember = familyMembers.find(m => String(m.id) === String(selectedMemberId));
                if (selMember) {
                    allItems = allItems.filter(item => 
                        String(item.family_member_id) === String(selMember.id) ||
                        item.member_name === selMember.name
                    );
                }
            }

            // Date Range filter
            if (selectedDateRange) {
                const now = new Date();
                let minDate = null;
                let maxDate = null;

                if (selectedDateRange === 'last_30_days') {
                    minDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                } else if (selectedDateRange === 'last_6_months') {
                    minDate = new Date(now.getFullYear(), now.getMonth() - 6, now.getDate());
                } else if (selectedDateRange === 'this_year') {
                    minDate = new Date(now.getFullYear(), 0, 1);
                } else if (selectedDateRange === 'custom') {
                    const fromVal = document.getElementById('filter-date-from')?.value;
                    const toVal = document.getElementById('filter-date-to')?.value;
                    if (fromVal) minDate = new Date(fromVal);
                    if (toVal) maxDate = new Date(toVal + 'T23:59:59');
                }

                if (minDate || maxDate) {
                    allItems = allItems.filter(item => {
                        if (!item.date) return false;
                        const itemDate = new Date(item.date);
                        if (isNaN(itemDate.getTime())) return true;
                        if (minDate && itemDate < minDate) return false;
                        if (maxDate && itemDate > maxDate) return false;
                        return true;
                    });
                }
            }

            // Sorting
            const sortVal = sortSelect ? sortSelect.value : 'newest';
            if (sortVal === 'oldest') {
                allItems.sort((a, b) => (a.date || '').localeCompare(b.date || ''));
            } else if (sortVal === 'newest') {
                allItems.sort((a, b) => (b.date || '').localeCompare(a.date || ''));
            } else if (sortVal === 'title') {
                allItems.sort((a, b) => (a.title || a.name || '').localeCompare(b.title || b.name || ''));
            }

            if (countEl) countEl.textContent = `Search Results (${allItems.length})`;

            if (allItems.length === 0) {
                const queryText = query ? `matching "${query}"` : 'matching your selected filters';
                resultsContainer.innerHTML = `
                    <div class="card p-12 text-center text-secondary">
                        <i data-lucide="search-x" size="48" class="mx-auto mb-4 text-warning"></i>
                        <h4 class="font-bold text-lg mb-1 text-main">No records found</h4>
                        <p>No health records ${queryText}. Try different keywords or adjust the filters on the left.</p>
                    </div>
                `;
                if (window.lucide) lucide.createIcons();
                return;
            }

            resultsContainer.innerHTML = allItems.map(item => {
                const dateStr = item.date ? App.date.format(item.date) : '';
                const title = item.title || item.name || item.vaccine_name || item.doctor_name || 'Health Entry';
                const desc = item.description || item.reason || item.instructions || item.dosage || item.notes || '';
                return `
                    <div class="search-result-item">
                        <div class="search-result-icon ${item.meta.iconClass}">
                            <i data-lucide="${item.meta.icon}" size="20"></i>
                        </div>
                        <div class="flex-1" style="min-width: 0;">
                            <div class="flex items-center justify-between gap-2 mb-1">
                                <a href="${item.meta.link}" class="font-bold text-base text-primary hover:underline">
                                    ${title}
                                </a>
                                <span class="badge ${item.meta.badge} text-xs font-semibold uppercase">${item.meta.label}</span>
                            </div>
                            ${desc ? `<p class="text-sm text-secondary mb-2 truncate" title="${desc}">${desc}</p>` : ''}
                            <div class="flex flex-wrap items-center gap-4 text-xs text-secondary mt-2">
                                ${item.member_name ? `<span>Member: <strong class="text-main">${item.member_name}</strong></span>` : ''}
                                ${dateStr ? `<span>Date: <strong class="text-main">${dateStr}</strong></span>` : ''}
                                ${item.hospital ? `<span>Hospital: <strong class="text-main">${item.hospital}</strong></span>` : ''}
                                ${item.doctor ? `<span>Doctor: <strong class="text-main">${item.doctor}</strong></span>` : ''}
                                ${item.dose_number ? `<span>Dose: <strong class="text-main">${item.dose_number}</strong></span>` : ''}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            if (window.lucide) lucide.createIcons();
        } catch (err) {
            console.error('Error during search:', err);
            resultsContainer.innerHTML = '<div class="card p-8 text-center text-danger">Search request failed. Please try again.</div>';
        }
    }

    // Input handlers
    searchInput?.addEventListener('input', () => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => performSearch(false), 300);
    });

    searchInput?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            clearTimeout(timeoutId);
            performSearch(true);
        }
    });

    clearBtn?.addEventListener('click', () => {
        if (searchInput) searchInput.value = '';
        performSearch(false);
    });

    applyFiltersBtn?.addEventListener('click', () => {
        performSearch(true);
    });

    resetFiltersBtn?.addEventListener('click', () => {
        if (searchInput) searchInput.value = '';
        if (memberFilter) memberFilter.value = '';
        if (dateRangeSelect) dateRangeSelect.value = '';
        if (customDateFields) customDateFields.classList.add('hidden');
        document.querySelectorAll('input[name="type_filter"]').forEach(cb => cb.checked = true);
        performSearch(false);
    });

    sortSelect?.addEventListener('change', () => performSearch(true));

    await loadMembers();

    // Check URL param ?q=
    const urlParams = new URLSearchParams(window.location.search);
    const initialQuery = urlParams.get('q');
    if (initialQuery && searchInput) {
        searchInput.value = initialQuery;
        performSearch(true);
    }

    if (window.lucide) lucide.createIcons();
});
