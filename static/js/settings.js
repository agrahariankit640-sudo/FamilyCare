document.addEventListener('DOMContentLoaded', async () => {
    const navLinks = document.querySelectorAll('#settings-nav a');
    const sections = document.querySelectorAll('.settings-section');
    const profileForm = document.getElementById('profile-form');
    const passwordForm = document.getElementById('password-form');
    const btnExportCsv = document.getElementById('btn-export-csv');
    const btnExportJson = document.getElementById('btn-export-json');
    const btnDeleteAccount = document.getElementById('btn-delete-account');

    const avatarFileInput = document.getElementById('avatar-file-input');
    const btnChangeAvatar = document.getElementById('btn-change-avatar');
    const btnUploadAvatarText = document.getElementById('btn-upload-avatar-text');
    const btnRemoveAvatar = document.getElementById('btn-remove-avatar');
    const settingsAvatar = document.getElementById('settings-avatar');
    const currencySelect = document.getElementById('setting-currency');

    // Sidebar navigation tabs
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);

            navLinks.forEach(l => {
                l.classList.remove('bg-bg-secondary', 'font-medium', 'text-primary', 'active-tab');
                l.classList.add('text-secondary');
            });
            link.classList.add('bg-bg-secondary', 'font-medium', 'text-primary', 'active-tab');
            link.classList.remove('text-secondary');

            sections.forEach(sec => {
                if (sec.id === targetId) {
                    sec.classList.remove('hidden');
                    sec.classList.add('block');
                } else {
                    sec.classList.add('hidden');
                    sec.classList.remove('block');
                }
            });
        });
    });

    // Helper: update avatar UI across Settings, Navbar and Sidebar
    function updateAvatarDisplay(photoUrl, name) {
        const initial = (name || 'U').charAt(0).toUpperCase();

        // 1. Settings avatar
        if (settingsAvatar) {
            if (photoUrl) {
                settingsAvatar.innerHTML = `<img src="${photoUrl}" alt="${name || 'User'}" class="w-full h-full object-cover rounded-full" id="settings-avatar-img" style="width: 100%; height: 100%; object-fit: cover;">`;
            } else {
                settingsAvatar.innerHTML = `<span id="settings-avatar-initial">${initial}</span>`;
            }
        }

        // 2. Navbar avatar
        const navbarAvatar = document.getElementById('navbar-user-avatar');
        if (navbarAvatar) {
            if (photoUrl) {
                navbarAvatar.innerHTML = `<img src="${photoUrl}" alt="${name || 'User'}" class="w-full h-full object-cover rounded-full" style="width: 100%; height: 100%; object-fit: cover;">`;
            } else {
                navbarAvatar.innerHTML = `<span>${initial}</span>`;
            }
        }

        // 3. Sidebar avatar
        const sidebarAvatar = document.getElementById('sidebar-user-avatar');
        if (sidebarAvatar) {
            if (photoUrl) {
                sidebarAvatar.innerHTML = `<img src="${photoUrl}" alt="${name || 'User'}" class="w-full h-full object-cover rounded-full" style="width: 100%; height: 100%; object-fit: cover;">`;
            } else {
                sidebarAvatar.innerHTML = `<span>${initial}</span>`;
            }
        }

        // 4. Toggle remove button
        if (btnRemoveAvatar) {
            if (photoUrl) btnRemoveAvatar.classList.remove('hidden');
            else btnRemoveAvatar.classList.add('hidden');
        }
    }

    // Load profile
    async function loadProfile() {
        try {
            const res = await API.auth.me();
            const user = res.data || res;
            if (user && profileForm) {
                if (document.getElementById('profile_name')) document.getElementById('profile_name').value = user.name || '';
                if (document.getElementById('profile_email')) document.getElementById('profile_email').value = user.email || '';
                if (document.getElementById('profile_phone')) document.getElementById('profile_phone').value = user.phone || '';
                
                // Set currency from user profile or localStorage
                const userCurr = user.currency || App.currency.get();
                if (currencySelect) currencySelect.value = userCurr;
                App.currency.set(userCurr);

                // Set avatar
                updateAvatarDisplay(user.profile_photo, user.name);
            }
        } catch (err) {
            console.error('Failed to load profile:', err);
        }
    }

    // Avatar upload triggers
    const triggerUpload = () => avatarFileInput?.click();
    btnChangeAvatar?.addEventListener('click', triggerUpload);
    btnUploadAvatarText?.addEventListener('click', triggerUpload);
    settingsAvatar?.addEventListener('click', triggerUpload);

    avatarFileInput?.addEventListener('change', async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;

        if (file.size > 2 * 1024 * 1024) {
            App.toast.show('File size must be under 2MB', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('photo', file);

        try {
            App.toast.show('Uploading profile photo...', 'info');
            const res = await API.users.uploadPhoto(formData);
            const photoUrl = res.photo_url || res.data?.photo_url;
            const currentName = document.getElementById('profile_name')?.value || 'User';

            updateAvatarDisplay(photoUrl, currentName);
            App.toast.show('Profile photo updated successfully', 'success');
        } catch (err) {
            console.error('Photo upload error:', err);
            App.toast.show(err.message || 'Failed to upload photo', 'error');
        } finally {
            avatarFileInput.value = '';
        }
    });

    // Remove avatar
    btnRemoveAvatar?.addEventListener('click', async () => {
        if (await App.confirm('Remove profile photo and restore default initial?')) {
            try {
                await API.users.deletePhoto();
                const currentName = document.getElementById('profile_name')?.value || 'User';
                updateAvatarDisplay(null, currentName);
                App.toast.show('Profile photo removed', 'success');
            } catch (err) {
                console.error('Remove photo error:', err);
                App.toast.show('Failed to remove photo', 'error');
            }
        }
    });

    // Save profile
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('profile_name').value.trim();
            const phone = document.getElementById('profile_phone')?.value?.trim() || '';
            const currency = currencySelect?.value || App.currency.get();

            const payload = { name, phone, currency };

            try {
                await API.auth.updateProfile(payload);
                App.currency.set(currency);

                // Update names in UI
                document.querySelectorAll('.user-name').forEach(el => el.textContent = name);
                
                App.toast.show('Profile & preferences updated successfully', 'success');
            } catch (err) {
                console.error('Update profile error:', err);
                App.toast.show(err.message || 'Failed to update profile', 'error');
            }
        });
    }

    // Change password
    if (passwordForm) {
        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const currentPassword = document.getElementById('current_password').value;
            const newPassword = document.getElementById('new_password').value;
            const confirmPassword = document.getElementById('confirm_password').value;

            if (newPassword !== confirmPassword) {
                App.toast.show('New passwords do not match', 'warning');
                return;
            }

            try {
                await API.auth.changePassword({
                    old_password: currentPassword,
                    new_password: newPassword
                });
                App.toast.show('Password changed successfully', 'success');
                passwordForm.reset();
            } catch (err) {
                console.error('Password change error:', err);
                App.toast.show(err.message || 'Failed to change password', 'error');
            }
        });
    }

    // Export buttons
    btnExportCsv?.addEventListener('click', async () => {
        try {
            App.toast.show('Preparing CSV export...', 'info');
            await API.export.csv('medical_records');
            App.toast.show('CSV export downloaded', 'success');
        } catch (err) {
            console.error('Export CSV error:', err);
            App.toast.show('Failed to export CSV', 'error');
        }
    });

    btnExportJson?.addEventListener('click', async () => {
        try {
            App.toast.show('Preparing backup JSON...', 'info');
            await API.export.backup();
            App.toast.show('Backup downloaded', 'success');
        } catch (err) {
            console.error('Export JSON error:', err);
            App.toast.show('Failed to download backup', 'error');
        }
    });

    // Delete account
    btnDeleteAccount?.addEventListener('click', async () => {
        if (await App.confirm('ARE YOU ABSOLUTELY SURE? This will permanently delete your account and all associated health records.')) {
            try {
                await API.users.deleteAccount({ confirm: 'yes' });
                window.location.href = '/login';
            } catch (err) {
                console.error('Delete account error:', err);
                App.toast.show('Could not delete account at this time', 'error');
            }
        }
    });

    await loadProfile();
});
