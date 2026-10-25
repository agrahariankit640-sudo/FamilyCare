document.addEventListener('DOMContentLoaded', async () => {
    let currentTab = 'policies';
    let familyMembers = [];
    let policiesList = [];
    let claimsList = [];

    const tabLinks = document.querySelectorAll('#insurance-tabs .tab-link');
    const policiesSection = document.getElementById('policies-section');
    const claimsSection = document.getElementById('claims-section');
    const policiesContainer = document.getElementById('policies-list');
    const policiesEmpty = document.getElementById('policies-empty');
    const claimsTableBody = document.getElementById('claims-list');
    const claimsEmpty = document.getElementById('claims-empty');

    const policyForm = document.getElementById('policy-form');
    const claimForm = document.getElementById('claim-form');
    const memberSelect = document.getElementById('member_id');
    const claimPolicySelect = document.getElementById('claim_policy_id');

    // Load members
    async function loadMembers() {
        try {
            const members = await API.familyMembers.list();
            familyMembers = Array.isArray(members) ? members : [];
            if (memberSelect) {
                memberSelect.innerHTML = '<option value="">-- Select Member --</option>' +
                    familyMembers.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
            }
        } catch (err) {
            console.error('Error loading members in insurance:', err);
        }
    }

    // Load policies and claims
    async function loadData() {
        if (currentTab === 'policies') {
            if (policiesSection) policiesSection.classList.remove('hidden');
            if (claimsSection) claimsSection.classList.add('hidden');
            await loadPolicies();
        } else {
            if (policiesSection) policiesSection.classList.add('hidden');
            if (claimsSection) claimsSection.classList.remove('hidden');
            await loadClaims();
        }
    }

    async function loadPolicies() {
        if (!policiesContainer) return;
        policiesContainer.innerHTML = `
            <div class="loading-state col-span-full text-center py-8">
                <i data-lucide="loader" class="spin mb-2"></i>
                <p>Loading policies...</p>
            </div>
        `;
        if (window.lucide) lucide.createIcons();

        try {
            const res = await API.insurance.listPolicies();
            policiesList = Array.isArray(res) ? res : [];

            // Also update claim policy dropdown
            if (claimPolicySelect) {
                claimPolicySelect.innerHTML = '<option value="">-- Select Policy --</option>' +
                    policiesList.map(p => `<option value="${p.id}">${p.provider} (${p.policy_number})</option>`).join('');
            }

            if (policiesList.length === 0) {
                policiesContainer.innerHTML = '';
                if (policiesEmpty) policiesEmpty.classList.remove('hidden');
                return;
            }

            if (policiesEmpty) policiesEmpty.classList.add('hidden');

            const now = new Date();
            policiesContainer.innerHTML = policiesList.map(p => {
                const expiryDateObj = p.expiry_date ? new Date(p.expiry_date) : null;
                const isExpired = expiryDateObj && expiryDateObj < now;
                const daysLeft = expiryDateObj ? Math.ceil((expiryDateObj - now) / (1000 * 60 * 60 * 24)) : null;
                const isExpiringSoon = daysLeft !== null && daysLeft >= 0 && daysLeft <= 30;

                const memberName = p.member_name || (familyMembers.find(m => m.id === p.family_member_id)?.name || 'General Family');
                const coverageAmt = p.coverage_amount ? App.currency.format(p.coverage_amount, 'USD') : 'N/A';
                const premiumAmt = p.premium ? `${App.currency.format(p.premium, 'USD')}/yr` : 'N/A';

                return `
                    <div class="card p-5 flex flex-col justify-between hover-shadow transition-shadow">
                        <div>
                            <div class="flex justify-between items-start mb-3">
                                <div>
                                    <h4 class="font-bold text-lg text-primary">${p.provider}</h4>
                                    <span class="text-xs font-mono text-secondary">${p.policy_number}</span>
                                </div>
                                ${isExpired ? '<span class="badge badge-danger text-xs">Expired</span>' : 
                                  isExpiringSoon ? `<span class="badge badge-warning text-xs">Expires in ${daysLeft}d</span>` : 
                                  '<span class="badge badge-success text-xs">Active</span>'}
                            </div>

                            <div class="space-y-2 text-sm text-secondary my-4">
                                <div class="flex justify-between">
                                    <span>Insured Member:</span>
                                    <strong class="text-main">${memberName}</strong>
                                </div>
                                <div class="flex justify-between">
                                    <span>Coverage:</span>
                                    <strong class="text-success font-semibold">${coverageAmt}</strong>
                                </div>
                                <div class="flex justify-between">
                                    <span>Premium:</span>
                                    <strong class="text-main">${premiumAmt}</strong>
                                </div>
                                <div class="flex justify-between text-xs">
                                    <span>Valid:</span>
                                    <span>${p.start_date || '-'} to ${p.expiry_date || '-'}</span>
                                </div>
                            </div>
                        </div>

                        <div class="border-t border-border-color pt-3 flex justify-end gap-2">
                            <button class="btn btn-sm btn-outline-primary p-2" title="Edit" onclick="editPolicyItem(${p.id})">
                                <i data-lucide="edit-2" size="14"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger p-2" title="Delete" onclick="deletePolicyItem(${p.id})">
                                <i data-lucide="trash-2" size="14"></i>
                            </button>
                        </div>
                    </div>
                `;
            }).join('');

            if (window.lucide) lucide.createIcons();
        } catch (err) {
            console.error('Error loading policies:', err);
            policiesContainer.innerHTML = '<div class="col-span-full text-center py-6 text-danger">Failed to load policies.</div>';
            App.toast.show('Error loading policies', 'error');
        }
    }

    async function loadClaims() {
        if (!claimsTableBody) return;
        claimsTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-6 text-secondary"><i data-lucide="loader" class="spin mb-2"></i><p>Loading claims...</p></td></tr>';
        if (window.lucide) lucide.createIcons();

        try {
            const res = await API.insurance.listClaims();
            claimsList = Array.isArray(res) ? res : [];

            if (claimsList.length === 0) {
                claimsTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-secondary">No claims recorded yet.</td></tr>';
                if (claimsEmpty) {
                    claimsEmpty.classList.remove('hidden');
                    document.querySelector('#claims-section .table-container')?.classList.add('hidden');
                }
                return;
            }

            if (claimsEmpty) claimsEmpty.classList.add('hidden');
            document.querySelector('#claims-section .table-container')?.classList.remove('hidden');

            const statusColors = {
                submitted: 'badge-info',
                pending: 'badge-warning',
                approved: 'badge-success',
                rejected: 'badge-danger',
                settled: 'badge-success'
            };

            claimsTableBody.innerHTML = claimsList.map(c => {
                const statusLower = (c.status || 'pending').toLowerCase();
                const badgeClass = statusColors[statusLower] || 'badge-secondary';
                const formattedDate = c.claim_date ? App.date.format(c.claim_date) : '-';
                const amount = parseFloat(c.amount || 0).toFixed(2);

                return `
                    <tr>
                        <td class="font-mono font-semibold">${c.claim_number || '-'}</td>
                        <td>${formattedDate}</td>
                        <td class="font-bold text-main">${App.currency.format(c.amount, 'USD')}</td>
                        <td>${c.hospital || '<span class="text-secondary">-</span>'}</td>
                        <td>${c.policy_name || 'Policy'} <span class="text-xs text-secondary">(${c.policy_number || ''})</span></td>
                        <td><span class="badge ${badgeClass} text-xs uppercase">${c.status || 'Submitted'}</span></td>
                        <td>
                            <div class="flex items-center gap-2">
                                <button class="btn btn-sm btn-outline-primary p-2" title="Edit" onclick="editClaimItem(${c.id})">
                                    <i data-lucide="edit-2" size="14"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger p-2" title="Delete" onclick="deleteClaimItem(${c.id})">
                                    <i data-lucide="trash-2" size="14"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');

            if (window.lucide) lucide.createIcons();
        } catch (err) {
            console.error('Error loading claims:', err);
            claimsTableBody.innerHTML = '<tr><td colspan="7" class="text-center py-6 text-danger">Failed to load claims.</td></tr>';
            App.toast.show('Error loading claims', 'error');
        }
    }

    // Tabs
    tabLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            tabLinks.forEach(l => {
                l.classList.remove('active', 'border-b-2', 'border-primary');
                l.classList.add('text-secondary');
            });
            link.classList.add('active', 'border-b-2', 'border-primary');
            link.classList.remove('text-secondary');
            currentTab = link.dataset.tab.toLowerCase();
            loadData();
        });
    });

    // Add buttons
    document.querySelectorAll('#btn-add-policy, .btn-add-policy').forEach(btn => {
        btn.addEventListener('click', () => {
            if (policyForm) {
                policyForm.reset();
                document.getElementById('policy_id').value = '';
                document.getElementById('policy-modal-title').textContent = 'Add Insurance Policy';
                document.getElementById('valid_from').value = new Date().toISOString().split('T')[0];
            }
            App.modal.open('policy-modal');
        });
    });

    document.querySelectorAll('#btn-add-claim, .btn-add-claim').forEach(btn => {
        btn.addEventListener('click', () => {
            if (claimForm) {
                claimForm.reset();
                document.getElementById('claim_id').value = '';
                document.getElementById('claim-modal-title').textContent = 'Add Claim';
                document.getElementById('claim_date').value = new Date().toISOString().split('T')[0];
            }
            App.modal.open('claim-modal');
        });
    });

    // Policy submit
    if (policyForm) {
        policyForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('policy_id').value;
            const payload = {
                family_member_id: parseInt(document.getElementById('member_id').value),
                provider: document.getElementById('provider_name').value.trim(),
                policy_number: document.getElementById('policy_number').value.trim(),
                policy_holder: document.getElementById('policy_holder')?.value?.trim() || '',
                start_date: document.getElementById('valid_from').value,
                expiry_date: document.getElementById('valid_till').value,
                coverage_amount: parseFloat(document.getElementById('coverage_amount')?.value || 0) || null,
                premium: parseFloat(document.getElementById('premium_amount')?.value || 0) || null
            };

            if (!payload.family_member_id || !payload.provider || !payload.policy_number || !payload.start_date || !payload.expiry_date) {
                App.toast.show('Please fill in required fields', 'warning');
                return;
            }

            try {
                if (id) {
                    await API.insurance.updatePolicy(id, payload);
                    App.toast.show('Policy updated', 'success');
                } else {
                    await API.insurance.createPolicy(payload);
                    App.toast.show('Policy added', 'success');
                }
                App.modal.close('policy-modal');
                loadPolicies();
            } catch (err) {
                console.error('Error saving policy:', err);
                App.toast.show(err.message || 'Error saving policy', 'error');
            }
        });
    }

    // Claim submit
    if (claimForm) {
        claimForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('claim_id').value;
            const payload = {
                policy_id: parseInt(document.getElementById('claim_policy_id').value),
                claim_number: document.getElementById('claim_number').value.trim(),
                claim_date: document.getElementById('claim_date').value,
                amount: parseFloat(document.getElementById('claim_amount').value),
                hospital: document.getElementById('claim_hospital')?.value?.trim() || '',
                status: document.getElementById('claim_status').value,
                description: document.getElementById('claim_description')?.value?.trim() || ''
            };

            if (!payload.policy_id || !payload.claim_number || !payload.claim_date || isNaN(payload.amount)) {
                App.toast.show('Please fill in required fields', 'warning');
                return;
            }

            try {
                if (id) {
                    await API.insurance.updateClaim(id, payload);
                    App.toast.show('Claim updated', 'success');
                } else {
                    await API.insurance.createClaim(payload);
                    App.toast.show('Claim submitted', 'success');
                }
                App.modal.close('claim-modal');
                loadClaims();
            } catch (err) {
                console.error('Error saving claim:', err);
                App.toast.show(err.message || 'Error saving claim', 'error');
            }
        });
    }

    // Policy edit/delete
    window.editPolicyItem = async (id) => {
        try {
            const res = await API.insurance.getPolicy(id);
            const p = res.data || res;
            if (!p) return;

            document.getElementById('policy_id').value = p.id;
            document.getElementById('provider_name').value = p.provider || '';
            document.getElementById('policy_number').value = p.policy_number || '';
            document.getElementById('policy_holder').value = p.policy_holder || '';
            document.getElementById('member_id').value = p.family_member_id || '';
            document.getElementById('valid_from').value = p.start_date || '';
            document.getElementById('valid_till').value = p.expiry_date || '';
            document.getElementById('coverage_amount').value = p.coverage_amount || '';
            document.getElementById('premium_amount').value = p.premium || '';
            document.getElementById('policy-modal-title').textContent = 'Edit Insurance Policy';

            App.modal.open('policy-modal');
        } catch (err) {
            console.error('Error fetching policy:', err);
            App.toast.show('Failed to load policy details', 'error');
        }
    };

    window.deletePolicyItem = async (id) => {
        if (await App.confirm('Are you sure you want to delete this insurance policy?')) {
            try {
                await API.insurance.deletePolicy(id);
                App.toast.show('Policy deleted', 'success');
                loadPolicies();
            } catch (err) {
                console.error('Error deleting policy:', err);
                App.toast.show('Failed to delete policy', 'error');
            }
        }
    };

    // Claim edit/delete
    window.editClaimItem = async (id) => {
        try {
            const res = await API.insurance.getClaim(id);
            const c = res.data || res;
            if (!c) return;

            document.getElementById('claim_id').value = c.id;
            document.getElementById('claim_policy_id').value = c.policy_id || '';
            document.getElementById('claim_number').value = c.claim_number || '';
            document.getElementById('claim_date').value = c.claim_date || '';
            document.getElementById('claim_amount').value = c.amount || '';
            document.getElementById('claim_hospital').value = c.hospital || '';
            document.getElementById('claim_status').value = c.status || 'Submitted';
            document.getElementById('claim_description').value = c.description || '';
            document.getElementById('claim-modal-title').textContent = 'Edit Claim';

            App.modal.open('claim-modal');
        } catch (err) {
            console.error('Error fetching claim:', err);
            App.toast.show('Failed to load claim details', 'error');
        }
    };

    window.deleteClaimItem = async (id) => {
        if (await App.confirm('Are you sure you want to delete this claim?')) {
            try {
                await API.insurance.deleteClaim(id);
                App.toast.show('Claim deleted', 'success');
                loadClaims();
            } catch (err) {
                console.error('Error deleting claim:', err);
                App.toast.show('Failed to delete claim', 'error');
            }
        }
    };

    await loadMembers();
    await loadData();
});
window.addEventListener('currencyChanged', () => { renderPolicies(); renderClaims(); });
