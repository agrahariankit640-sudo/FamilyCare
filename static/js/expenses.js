document.addEventListener('DOMContentLoaded', async () => {
    let familyMembers = [];
    let expensesList = [];
    let trendChartInstance = null;
    let catChartInstance = null;

    const memberFilter = document.getElementById('filter-member');
    const categoryFilter = document.getElementById('filter-category');
    const dateFromFilter = document.getElementById('filter-date-from');
    const dateToFilter = document.getElementById('filter-date-to');
    const expensesTableBody = document.getElementById('expenses-list');
    const emptyState = document.getElementById('expenses-empty');
    const modalMemberSelect = document.getElementById('member_id');
    const expenseForm = document.getElementById('expense-form');

    // Stat card elements
    const expenseMonthEl = document.getElementById('expense-month');
    const expenseTotalEl = document.getElementById('expense-total');
    const expenseTopCatEl = document.getElementById('expense-top-cat');

    // Load family members
    async function loadMembers() {
        try {
            const members = await API.familyMembers.list();
            familyMembers = Array.isArray(members) ? members : [];

            if (memberFilter) {
                memberFilter.innerHTML = '<option value="">All Family Members</option>' +
                    familyMembers.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
            }
            if (modalMemberSelect) {
                modalMemberSelect.innerHTML = '<option value="">Select Member</option>' +
                    familyMembers.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
            }
        } catch (err) {
            console.error('Error loading members in expenses:', err);
        }
    }

    // Load summary and render charts
    async function loadSummary() {
        try {
            const activeCurr = App.currency.get();
            const res = await API.expenses.summary({ currency: activeCurr });
            const summary = res.data || res || {};

            if (expenseMonthEl) expenseMonthEl.textContent = App.currency.format(summary.thisMonth || 0, null, activeCurr);
            if (expenseTotalEl) expenseTotalEl.textContent = App.currency.format(summary.total || 0, null, activeCurr);
            if (expenseTopCatEl) expenseTopCatEl.textContent = summary.topCategory || '-';

            // Trend Chart
            const trendCanvas = document.getElementById('expenseTrendChart');
            if (trendCanvas && summary.trendData && typeof Chart !== 'undefined') {
                if (trendChartInstance) trendChartInstance.destroy();
                trendChartInstance = new Chart(trendCanvas.getContext('2d'), {
                    type: 'bar',
                    data: summary.trendData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: { y: { beginAtZero: true } }
                    }
                });
            }

            // Category Chart
            const catCanvas = document.getElementById('expenseCategoryChart');
            if (catCanvas && summary.categoryData && typeof Chart !== 'undefined') {
                if (catChartInstance) catChartInstance.destroy();
                catChartInstance = new Chart(catCanvas.getContext('2d'), {
                    type: 'doughnut',
                    data: summary.categoryData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });
            }
            if (window.lucide) lucide.createIcons();
        } catch (err) {
            console.error('Error loading expense summary:', err);
        }
    }

    // Load expenses table
    async function loadExpenses() {
        if (!expensesTableBody) return;
        expensesTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-6 text-secondary"><i data-lucide="loader" class="spin mb-2"></i><p>Loading expenses...</p></td></tr>';
        if (window.lucide) lucide.createIcons();

        try {
            const params = { currency: App.currency.get() };
            if (memberFilter && memberFilter.value) params.family_member_id = memberFilter.value;
            if (categoryFilter && categoryFilter.value) params.category = categoryFilter.value;
            if (dateFromFilter && dateFromFilter.value) params.date_from = dateFromFilter.value;
            if (dateToFilter && dateToFilter.value) params.date_to = dateToFilter.value;

            const res = await API.expenses.list(params);
            expensesList = Array.isArray(res) ? res : (res.data || []);

            renderTable();
        } catch (err) {
            console.error('Error loading expenses list:', err);
            expensesTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-6 text-danger">Failed to load expenses.</td></tr>';
            App.toast.show('Error loading expenses', 'error');
        }
    }

    function renderTable() {
        if (expensesList.length === 0) {
            expensesTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-secondary">No expenses found matching filters.</td></tr>';
            if (emptyState) emptyState.classList.remove('hidden');
            return;
        }

        if (emptyState) emptyState.classList.add('hidden');

        const activeCurr = App.currency.get().toUpperCase();

        expensesTableBody.innerHTML = expensesList.map(e => {
            const expDate = e.expense_date ? App.date.format(e.expense_date) : '-';
            const memberName = e.member_name || (familyMembers.find(m => m.id === e.family_member_id)?.name || 'Member');
            const origCurr = (e.currency || 'USD').toUpperCase();
            const isDiff = origCurr !== activeCurr;
            const formattedConverted = App.currency.format(e.amount, origCurr, activeCurr);
            const origFormatted = `${App.currency.getSymbol(origCurr)}${parseFloat(e.amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

            return `
                <tr>
                    <td>${expDate}</td>
                    <td><span class="badge badge-info">${memberName}</span></td>
                    <td>
                        <div class="font-semibold text-main">${e.category || 'Expense'}</div>
                        ${e.description ? `<span class="text-xs text-secondary truncate max-w-xs block">${e.description}</span>` : ''}
                    </td>
                    <td>${e.hospital || '<span class="text-secondary">-</span>'}</td>
                    <td class="font-bold text-main">
                        <div>${formattedConverted}</div>
                        ${isDiff ? `<span class="text-xs text-secondary font-normal">Orig: ${origFormatted}</span>` : ''}
                    </td>
                    <td><span class="badge badge-secondary">${e.payment_method || 'Other'}</span></td>
                    <td>
                        <div class="flex items-center gap-2">
                            <button class="btn btn-sm btn-outline-primary p-2" title="Edit" onclick="editExpenseItem(${e.id})">
                                <i data-lucide="edit-2" size="14"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger p-2" title="Delete" onclick="deleteExpenseItem(${e.id})">
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
    memberFilter?.addEventListener('change', loadExpenses);
    categoryFilter?.addEventListener('change', loadExpenses);
    dateFromFilter?.addEventListener('change', loadExpenses);
    dateToFilter?.addEventListener('change', loadExpenses);

    // Update currency symbol in modal when opened
    function updateModalCurrency(curr = null) {
        const symbolEl = document.getElementById('expense-modal-currency-symbol');
        const hiddenCurr = document.getElementById('expense_currency');
        const c = curr || (hiddenCurr ? hiddenCurr.value : null) || App.currency.get();
        if (symbolEl) symbolEl.textContent = App.currency.getSymbol(c);
        if (hiddenCurr) hiddenCurr.value = c;
    }

    window.addEventListener('currencyChanged', () => {
        loadSummary();
        renderTable();
        updateModalCurrency();
    });

    // Add buttons
    document.querySelectorAll('#btn-add-expense, .btn-add-expense').forEach(btn => {
        btn.addEventListener('click', () => {
            if (expenseForm) {
                expenseForm.reset();
                document.getElementById('expense_id').value = '';
                document.getElementById('modal-title').textContent = 'Add Medical Expense';
                document.getElementById('expense_date').value = new Date().toISOString().split('T')[0];
                updateModalCurrency(App.currency.get());
            }
            App.modal.open('expense-modal');
        });
    });

    // Form submit
    if (expenseForm) {
        expenseForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('expense_id').value;
            const payload = {
                family_member_id: parseInt(document.getElementById('member_id').value),
                amount: parseFloat(document.getElementById('amount').value),
                currency: document.getElementById('expense_currency')?.value || App.currency.get(),
                category: document.getElementById('category').value,
                expense_date: document.getElementById('expense_date').value,
                hospital: document.getElementById('hospital')?.value?.trim() || '',
                payment_method: document.getElementById('payment_method')?.value || 'Cash',
                description: document.getElementById('description')?.value?.trim() || ''
            };

            if (!payload.family_member_id || isNaN(payload.amount) || !payload.category || !payload.expense_date) {
                App.toast.show('Please fill in required fields', 'warning');
                return;
            }

            try {
                if (id) {
                    await API.expenses.update(id, payload);
                    App.toast.show('Expense updated successfully', 'success');
                } else {
                    await API.expenses.create(payload);
                    App.toast.show('Expense recorded successfully', 'success');
                }
                App.modal.close('expense-modal');
                await loadSummary();
                await loadExpenses();
            } catch (err) {
                console.error('Error saving expense:', err);
                App.toast.show(err.message || 'Error saving expense', 'error');
            }
        });
    }

    // Edit expense
    window.editExpenseItem = async (id) => {
        try {
            const res = await API.expenses.get(id);
            const ex = res.data || res;
            if (!ex) return;

            document.getElementById('expense_id').value = ex.id;
            document.getElementById('member_id').value = ex.family_member_id || '';
            document.getElementById('amount').value = ex.amount || '';
            document.getElementById('category').value = ex.category || 'Consultation';
            document.getElementById('expense_date').value = ex.expense_date || '';
            document.getElementById('hospital').value = ex.hospital || '';
            document.getElementById('payment_method').value = ex.payment_method || 'Cash';
            document.getElementById('description').value = ex.description || '';
            document.getElementById('modal-title').textContent = 'Edit Medical Expense';
            updateModalCurrency(ex.currency || 'USD');

            App.modal.open('expense-modal');
        } catch (err) {
            console.error('Error fetching expense:', err);
            App.toast.show('Failed to load expense details', 'error');
        }
    };

    // Delete expense
    window.deleteExpenseItem = async (id) => {
        if (await App.confirm('Are you sure you want to delete this expense record?')) {
            try {
                await API.expenses.delete(id);
                App.toast.show('Expense deleted', 'success');
                await loadSummary();
                await loadExpenses();
            } catch (err) {
                console.error('Error deleting expense:', err);
                App.toast.show('Failed to delete expense', 'error');
            }
        }
    };

    await loadMembers();
    await loadSummary();
    await loadExpenses();
});
