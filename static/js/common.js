const App = {
    theme: {
        init() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            App.theme.updateIcons(savedTheme);

            const toggleBtn = document.getElementById('theme-toggle');
            if (toggleBtn && !toggleBtn.dataset.themeBound) {
                toggleBtn.dataset.themeBound = 'true';
                toggleBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    App.theme.toggle();
                });
            }
        },
        updateIcons(theme) {
            const sunIcon = document.querySelector('.theme-toggle .sun-icon');
            const moonIcon = document.querySelector('.theme-toggle .moon-icon');
            if (sunIcon && moonIcon) {
                if (theme === 'dark') {
                    sunIcon.classList.add('hidden');
                    moonIcon.classList.remove('hidden');
                } else {
                    sunIcon.classList.remove('hidden');
                    moonIcon.classList.add('hidden');
                }
            }
        },
        toggle() {
            const current = document.documentElement.getAttribute('data-theme') || 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            App.theme.updateIcons(next);
        }
    },
    currency: {
        RATES: {
            'USD': 1.0,
            'INR': 83.5,
            'EUR': 0.92,
            'GBP': 0.79,
            'AED': 3.67,
            'CAD': 1.36,
            'AUD': 1.52
        },
        SYMBOLS: {
            'INR': '₹',
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'AED': 'AED ',
            'CAD': 'CA$',
            'AUD': 'AU$'
        },
        get() {
            return localStorage.getItem('familycare_currency') || 'USD';
        },
        getSymbol(curr) {
            const c = curr || App.currency.get();
            return App.currency.SYMBOLS[c] || '$';
        },
        set(curr) {
            localStorage.setItem('familycare_currency', curr);
            if (typeof API !== 'undefined' && API.users && API.users.updateSettings) {
                API.users.updateSettings({ currency: curr }).catch(() => {});
            }
            window.dispatchEvent(new CustomEvent('currencyChanged', { detail: curr }));
        },
        convert(amount, fromCurr = 'USD', toCurr = null) {
            const val = parseFloat(amount || 0);
            if (isNaN(val) || val === 0) return 0;
            const from = (fromCurr || 'USD').toUpperCase();
            const target = (toCurr || App.currency.get()).toUpperCase();
            const fromRate = App.currency.RATES[from] || 1.0;
            const toRate = App.currency.RATES[target] || 1.0;
            const inUsd = val / fromRate;
            return inUsd * toRate;
        },
        format(amount, fromCurr = null, targetCurr = null) {
            const val = parseFloat(amount || 0);
            const target = targetCurr || App.currency.get();
            if (isNaN(val)) return `${App.currency.getSymbol(target)}0.00`;
            const converted = fromCurr ? App.currency.convert(val, fromCurr, target) : val;
            const symbol = App.currency.getSymbol(target);
            return `${symbol}${converted.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        },
        init() {
            const userCurrencyMeta = document.querySelector('meta[name="user-currency"]');
            if (userCurrencyMeta && userCurrencyMeta.content && !localStorage.getItem('familycare_currency')) {
                localStorage.setItem('familycare_currency', userCurrencyMeta.content);
            }
            document.querySelectorAll('.currency-selector, #currency-selector, #setting-currency').forEach(select => {
                select.value = App.currency.get();
                if (!select.dataset.currencyBound) {
                    select.dataset.currencyBound = 'true';
                    select.addEventListener('change', (e) => {
                        App.currency.set(e.target.value);
                    });
                }
            });
            window.addEventListener('currencyChanged', (e) => {
                document.querySelectorAll('.currency-selector, #currency-selector, #setting-currency').forEach(select => {
                    select.value = e.detail;
                });
            });
        }
    },
    passwordToggle: {
        init() {
            document.querySelectorAll('.password-toggle, .toggle-password').forEach(btn => {
                if (btn.dataset.toggleBound || btn.dataset.authToggleBound) return;
                btn.dataset.toggleBound = 'true';
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const group = this.closest('.password-input-group') || this.parentElement;
                    const input = group ? group.querySelector('input') : null;
                    if (input) {
                        const isPassword = input.getAttribute('type') === 'password';
                        input.setAttribute('type', isPassword ? 'text' : 'password');
                        this.innerHTML = `<i data-lucide="${isPassword ? 'eye-off' : 'eye'}"></i>`;
                        if (typeof lucide !== 'undefined' && lucide.createIcons) {
                            lucide.createIcons();
                        }
                    }
                });
            });
        }
    },
    sidebar: {
        init() {
            // Hamburger open button in the top navbar
            const toggleBtn = document.getElementById('mobile-menu-toggle');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', App.sidebar.toggle);
            }
            // X close button inside the sidebar header
            const closeBtn = document.querySelector('.sidebar .mobile-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', App.sidebar.close);
            }
            // Close when clicking the overlay behind the sidebar
            const overlay = document.querySelector('.sidebar-overlay');
            if (overlay) {
                overlay.addEventListener('click', App.sidebar.close);
            }
            // Close when pressing Escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    App.sidebar.close();
                }
            });
            // Mark active nav link
            const path = window.location.pathname;
            document.querySelectorAll('.sidebar-nav a').forEach(link => {
                if (link.getAttribute('href') === path) {
                    link.classList.add('active');
                }
                link.addEventListener('click', () => {
                    if (window.innerWidth <= 768) App.sidebar.close();
                });
            });
        },
        toggle() {
            document.querySelector('.sidebar')?.classList.toggle('open');
        },
        close() {
            document.querySelector('.sidebar')?.classList.remove('open');
        }
    },
    modal: {
        open(modalId) {
            let modal = document.getElementById(modalId);
            if (!modal) {
                document.querySelectorAll('template').forEach(tpl => {
                    const el = tpl.content.querySelector('#' + modalId);
                    if (el) {
                        const clone = document.importNode(tpl.content, true);
                        document.body.appendChild(clone);
                        modal = document.getElementById(modalId);
                        tpl.remove();
                    }
                });
            }
            if (modal) {
                modal.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
                    if (!btn.dataset.closeBound) {
                        btn.dataset.closeBound = 'true';
                        btn.addEventListener('click', (e) => {
                            e.preventDefault();
                            App.modal.close(modalId);
                        });
                    }
                });
                modal.classList.add('active');
                document.addEventListener('keydown', App.modal._handleEsc);
                if (typeof lucide !== 'undefined' && lucide.createIcons) {
                    lucide.createIcons();
                }
            }
        },
        close(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove('active');
                document.removeEventListener('keydown', App.modal._handleEsc);
            }
        },
        _handleEsc(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal.active').forEach(m => App.modal.close(m.id));
            }
        },
        create(id, title, content, footerButtons) {
            const existing = document.getElementById(id);
            if (existing) existing.remove();
            
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.id = id;
            modal.innerHTML = `
                <div class="modal-overlay" onclick="App.modal.close('${id}')"></div>
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>${title}</h2>
                        <button class="modal-close" onclick="App.modal.close('${id}')">&times;</button>
                    </div>
                    <div class="modal-body">${content}</div>
                    <div class="modal-footer">${footerButtons}</div>
                </div>
            `;
            document.body.appendChild(modal);
            return modal;
        }
    },
    toast: {
        show(message, type = 'info', duration = 4000) {
            let container = document.getElementById('toast-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'toast-container';
                container.className = 'toast-container';
                document.body.appendChild(container);
            }
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.innerHTML = `
                <span>${message}</span>
                <button onclick="this.parentElement.remove()">&times;</button>
            `;
            container.appendChild(toast);
            setTimeout(() => {
                if (toast.parentElement) toast.remove();
            }, duration);
        }
    },
    confirm(title, message, onConfirm, type = 'danger') {
        return new Promise((resolve) => {
            const id = 'confirm-modal-' + Date.now();
            const footer = `
                <button class="btn btn-secondary" onclick="App.modal.close('${id}');">Cancel</button>
                <button class="btn btn-${type}" id="${id}-confirm">Confirm</button>
            `;
            App.modal.create(id, title, `<p>${message}</p>`, footer);
            App.modal.open(id);
            document.getElementById(`${id}-confirm`).addEventListener('click', async () => {
                App.modal.close(id);
                if (onConfirm) await onConfirm();
                resolve(true);
            });
        });
    },
    loading: {
        show(container) {
            if (typeof container === 'string') container = document.querySelector(container);
            if (!container) return;
            const spinner = document.createElement('div');
            spinner.className = 'loading-overlay';
            spinner.innerHTML = '<div class="spinner"></div>';
            container.style.position = 'relative';
            container.appendChild(spinner);
        },
        hide(container) {
            if (typeof container === 'string') container = document.querySelector(container);
            if (!container) return;
            const overlay = container.querySelector('.loading-overlay');
            if (overlay) overlay.remove();
        },
        showBtn(button) {
            if (typeof button === 'string') button = document.querySelector(button);
            if (!button) return;
            button.dataset.originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<span class="spinner-small"></span> Loading...';
        },
        hideBtn(button, originalText) {
            if (typeof button === 'string') button = document.querySelector(button);
            if (!button) return;
            button.disabled = false;
            button.innerHTML = originalText || button.dataset.originalText;
        }
    },
    form: {
        getData(formElement) {
            const formData = new FormData(formElement);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            return data;
        },
        setData(formElement, data) {
            for (let key in data) {
                const input = formElement.elements[key];
                if (input) {
                    if (input.type === 'checkbox') input.checked = !!data[key];
                    else input.value = data[key];
                }
            }
        },
        clear(formElement) {
            formElement.reset();
            App.form.clearFieldErrors(formElement);
        },
        validate(formElement) {
            let isValid = true;
            const errors = {};
            App.form.clearFieldErrors(formElement);
            
            Array.from(formElement.elements).forEach(input => {
                if (input.required && !input.value.trim()) {
                    isValid = false;
                    errors[input.name] = 'This field is required';
                    App.form.showFieldError(input, 'This field is required');
                } else if (input.type === 'email' && input.value) {
                    if (!App.form.validateEmail(input.value)) {
                        isValid = false;
                        errors[input.name] = 'Invalid email address';
                        App.form.showFieldError(input, 'Invalid email address');
                    }
                }
            });
            return { isValid, errors };
        },
        showFieldError(input, message) {
            input.classList.add('error');
            let errorEl = input.parentElement.querySelector('.error-message');
            if (!errorEl) {
                errorEl = document.createElement('div');
                errorEl.className = 'error-message';
                input.parentElement.appendChild(errorEl);
            }
            errorEl.textContent = message;
        },
        clearFieldErrors(formElement) {
            formElement.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
            formElement.querySelectorAll('.error-message').forEach(el => el.remove());
        },
        validateEmail(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        },
        validatePassword(password) {
            if (password.length < 8) return { valid: false, message: 'Password must be at least 8 characters' };
            if (!/[A-Z]/.test(password)) return { valid: false, message: 'Password must contain an uppercase letter' };
            if (!/[a-z]/.test(password)) return { valid: false, message: 'Password must contain a lowercase letter' };
            if (!/[0-9]/.test(password)) return { valid: false, message: 'Password must contain a number' };
            return { valid: true, message: 'Strong password' };
        }
    },
    date: {
        format(dateStr) {
            if (!dateStr) return '';
            const d = new Date(dateStr);
            const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            return `${d.getDate().toString().padStart(2, '0')} ${months[d.getMonth()]} ${d.getFullYear()}`;
        },
        formatDateTime(dateStr) {
            if (!dateStr) return '';
            const d = new Date(dateStr);
            const time = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            return `${App.date.format(dateStr)}, ${time}`;
        },
        formatRelativeTime(dateStr) {
            if (!dateStr) return '';
            const diff = (new Date() - new Date(dateStr)) / 1000;
            if (diff < 60) return 'Just now';
            if (diff < 3600) return Math.floor(diff/60) + ' mins ago';
            if (diff < 86400) {
                const hrs = Math.floor(diff/3600);
                return hrs + (hrs === 1 ? ' hour ago' : ' hours ago');
            }
            if (diff < 172800) return 'Yesterday';
            return Math.floor(diff/86400) + ' days ago';
        },
        getAge(dateOfBirth) {
            if (!dateOfBirth) return '';
            const today = new Date();
            const birthDate = new Date(dateOfBirth);
            let age = today.getFullYear() - birthDate.getFullYear();
            const m = today.getMonth() - birthDate.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
            return age;
        },
        isToday(dateStr) {
            const d = new Date(dateStr);
            const today = new Date();
            return d.getDate() === today.getDate() &&
                   d.getMonth() === today.getMonth() &&
                   d.getFullYear() === today.getFullYear();
        },
        isFuture(dateStr) {
            return new Date(dateStr) > new Date();
        },
        isPast(dateStr) {
            return new Date(dateStr) < new Date();
        }
    },
    table: {
        create(headers, rows, options = {}) {
            let html = '<table class="table">';
            html += '<thead><tr>' + headers.map(h => `<th>${h}</th>`).join('') + '</tr></thead>';
            html += '<tbody>';
            if (rows.length === 0) {
                html += `<tr><td colspan="${headers.length}" class="text-center">No records found</td></tr>`;
            } else {
                html += rows.map(r => '<tr>' + r.map(c => `<td>${c}</td>`).join('') + '</tr>').join('');
            }
            html += '</tbody></table>';
            return html;
        },
        paginate(currentPage, totalPages, onPageChange) {
            if (totalPages <= 1) return '';
            let html = '<div class="pagination">';
            html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="${onPageChange}(${currentPage - 1})">Prev</button>`;
            html += `<span>Page ${currentPage} of ${totalPages}</span>`;
            html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="${onPageChange}(${currentPage + 1})">Next</button>`;
            html += '</div>';
            return html;
        }
    },
    emptyState: {
        create(icon, message, actionText, onActionStr) {
            return `
                <div class="empty-state">
                    <div class="icon">${icon}</div>
                    <p>${message}</p>
                    ${actionText ? `<button class="btn btn-primary" onclick="${onActionStr}">${actionText}</button>` : ''}
                </div>
            `;
        }
    },
    search: {
        debounce(func, wait = 300) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        },
        buildQuery(params) {
            return Object.keys(params)
                .map(k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k]))
                .join('&');
        },
        parseQuery(str) {
            if (str.startsWith('?')) str = str.substring(1);
            if (!str) return {};
            return str.split('&').reduce((acc, pair) => {
                const [key, value] = pair.split('=');
                acc[decodeURIComponent(key)] = decodeURIComponent(value);
                return acc;
            }, {});
        }
    },
    notifications: {
        init() {
            App.notifications.poll();
            setInterval(App.notifications.poll, 60000);

            const notifBtn = document.querySelector('.notification-btn');
            if (notifBtn && !notifBtn.dataset.notifBound) {
                notifBtn.dataset.notifBound = 'true';
                notifBtn.addEventListener('click', () => {
                    App.notifications.loadDropdown();
                });
            }
        },
        updateCount(count) {
            document.querySelectorAll('.notification-badge, #notification-badge').forEach(badge => {
                badge.textContent = count;
                if (count > 0) {
                    badge.classList.remove('hidden');
                    badge.style.display = 'inline-block';
                } else {
                    badge.classList.add('hidden');
                    badge.style.display = 'none';
                }
            });
        },
        async poll() {
            if (typeof API !== 'undefined' && API.notifications && API.notifications.unreadCount) {
                try {
                    const data = await API.notifications.unreadCount();
                    if (data && data.count !== undefined) {
                        App.notifications.updateCount(data.count);
                    }
                } catch (e) {
                    // Ignore background polling error
                }
            }
        },
        async loadDropdown() {
            const listEl = document.getElementById('notification-dropdown-list');
            if (!listEl) return;
            
            listEl.innerHTML = '<div class="p-4 text-center text-xs text-secondary"><i data-lucide="loader" class="spin mb-1"></i> Loading...</div>';
            if (typeof lucide !== 'undefined' && lucide.createIcons) lucide.createIcons();
            
            try {
                const res = await API.notifications.list();
                const items = Array.isArray(res) ? res : (res?.data || []);
                
                if (items.length === 0) {
                    listEl.innerHTML = '<div class="p-4 text-center text-xs text-secondary">No notifications right now</div>';
                    return;
                }
                
                const preview = items.slice(0, 5);
                listEl.innerHTML = preview.map(n => {
                    const timeAgo = App.date.formatRelativeTime ? App.date.formatRelativeTime(n.created_at) : (n.created_at || '');
                    const isUnread = !n.is_read;
                    return `
                        <div class="notification-dropdown-item p-3 border-b border-border-color hover:bg-background cursor-pointer flex items-start gap-2 ${isUnread ? 'bg-primary-bg' : ''}" onclick="App.notifications.handleItemClick(${n.id})">
                            <div class="notif-dot mt-1 ${isUnread ? 'bg-primary' : 'bg-transparent'}" style="width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; background: ${isUnread ? 'var(--color-primary)' : 'transparent'};"></div>
                            <div class="flex-1 text-xs">
                                <div class="font-semibold text-main mb-0.5">${App.utils.escapeHtml(n.title || 'Notification')}</div>
                                <div class="text-secondary line-clamp-2">${App.utils.escapeHtml(n.message || '')}</div>
                                <div class="text-secondary text-[10px] mt-1 font-mono">${timeAgo}</div>
                            </div>
                        </div>
                    `;
                }).join('');
                
                if (typeof lucide !== 'undefined' && lucide.createIcons) lucide.createIcons();
            } catch (err) {
                listEl.innerHTML = '<div class="p-3 text-center text-xs text-danger">Failed to load notifications</div>';
            }
        },
        async handleItemClick(id) {
            try {
                if (typeof API !== 'undefined' && API.notifications) {
                    await API.notifications.markRead(id);
                    App.notifications.poll();
                    App.notifications.loadDropdown();
                }
            } catch (e) {
                console.error(e);
            }
        }
    },
    fileUpload: {
        create(container, options = {}) {
            if (typeof container === 'string') container = document.querySelector(container);
            if (!container) return;
            
            container.className = 'file-upload-container';
            container.innerHTML = `
                <div class="file-upload-dropzone">
                    <span>Drag & drop file here or click to browse</span>
                    <input type="file" style="display:none" ${options.accept ? `accept="${options.accept}"` : ''}>
                </div>
                <div class="file-upload-preview"></div>
            `;
            
            const dropzone = container.querySelector('.file-upload-dropzone');
            const input = container.querySelector('input[type="file"]');
            
            dropzone.addEventListener('click', () => input.click());
            
            dropzone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropzone.classList.add('dragover');
            });
            
            dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
            
            dropzone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropzone.classList.remove('dragover');
                if (e.dataTransfer.files.length) {
                    input.files = e.dataTransfer.files;
                    input.dispatchEvent(new Event('change'));
                }
            });
            
            input.addEventListener('change', (e) => {
                if (options.onChange && e.target.files.length > 0) {
                    options.onChange(e.target.files[0]);
                }
            });
        },
        validate(file, maxSizeMb = 5, allowedTypes = []) {
            if (file.size > maxSizeMb * 1024 * 1024) {
                return { valid: false, error: `File must be less than ${maxSizeMb}MB` };
            }
            if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
                return { valid: false, error: 'Invalid file type' };
            }
            return { valid: true };
        },
        formatSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
    },
    familyMembers: {
        _cache: null,
        async load() {
            if (App.familyMembers._cache) return App.familyMembers._cache;
            try {
                if (typeof API !== 'undefined' && API.familyMembers) {
                    const members = await API.familyMembers.list();
                    App.familyMembers._cache = members;
                    return members;
                }
            } catch (e) {
                console.error("Failed to load family members", e);
                return [];
            }
        },
        async createSelect(selectElement) {
            if (typeof selectElement === 'string') selectElement = document.querySelector(selectElement);
            if (!selectElement) return;
            const members = await App.familyMembers.load();
            
            let html = '<option value="">Select Family Member</option>';
            if (members.length) {
                members.forEach(m => {
                    html += `<option value="${m.id}">${m.name}</option>`;
                });
            }
            selectElement.innerHTML = html;
        },
        getCurrent() {
            const params = new URLSearchParams(window.location.search);
            return params.get('member_id');
        }
    },
    dropdown: {
        init() {
            document.querySelectorAll('.dropdown-toggle').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const wrapper = btn.closest('.dropdown-wrapper');
                    if (wrapper) {
                        const wasActive = wrapper.classList.contains('active');
                        document.querySelectorAll('.dropdown-wrapper.active').forEach(w => w.classList.remove('active'));
                        if (!wasActive) wrapper.classList.add('active');
                    }
                });
            });

            document.addEventListener('click', (e) => {
                if (!e.target.closest('.dropdown-menu')) {
                    document.querySelectorAll('.dropdown-wrapper.active').forEach(w => w.classList.remove('active'));
                }
            });
        }
    },
    init() {
        App.theme.init();
        App.sidebar.init();
        App.dropdown.init();
        App.notifications.init();
        App.currency.init();
        App.passwordToggle.init();
    }
};

document.addEventListener('DOMContentLoaded', App.init);
