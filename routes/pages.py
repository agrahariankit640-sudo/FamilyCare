from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def landing_page():
    if current_user.is_authenticated:
        return redirect(url_for('pages.dashboard_page'))
    return render_template('index.html')

@pages_bp.route('/login')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('pages.dashboard_page'))
    return render_template('login.html')

@pages_bp.route('/register')
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('pages.dashboard_page'))
    return render_template('register.html')

@pages_bp.route('/dashboard')
@login_required
def dashboard_page():
    return render_template('dashboard.html')

@pages_bp.route('/family')
@login_required
def family_page():
    return render_template('family.html')

@pages_bp.route('/member')
@pages_bp.route('/member/<int:id>')
@login_required
def member_page(id=None):
    if not id:
        id = request.args.get('id')
    return render_template('member.html', member_id=id)

@pages_bp.route('/records')
@login_required
def records_page():
    return render_template('records.html')

@pages_bp.route('/medicines')
@login_required
def medicines_page():
    return render_template('medicines.html')

@pages_bp.route('/reminders')
@login_required
def reminders_page():
    return render_template('reminders.html')

@pages_bp.route('/appointments')
@login_required
def appointments_page():
    return render_template('appointments.html')

@pages_bp.route('/tests')
@login_required
def tests_page():
    return render_template('tests.html')

@pages_bp.route('/vaccinations')
@login_required
def vaccinations_page():
    return render_template('vaccinations.html')

@pages_bp.route('/health-tracker')
@login_required
def health_tracker_page():
    return render_template('health-tracker.html')

@pages_bp.route('/timeline')
@login_required
def timeline_page():
    return render_template('timeline.html')

@pages_bp.route('/expenses')
@login_required
def expenses_page():
    return render_template('expenses.html')

@pages_bp.route('/insurance')
@login_required
def insurance_page():
    return render_template('insurance.html')

@pages_bp.route('/emergency')
@login_required
def emergency_page():
    return render_template('emergency.html')

@pages_bp.route('/search')
@login_required
def search_page():
    return render_template('search.html')

@pages_bp.route('/notifications')
@login_required
def notifications_page():
    return render_template('notifications.html')

@pages_bp.route('/settings')
@login_required
def settings_page():
    return render_template('settings.html')

@pages_bp.route('/export')
@login_required
def export_page():
    return redirect('/settings#data')

@pages_bp.route('/admin')
@login_required
def admin_page():
    if current_user.role != 'admin':
        return redirect(url_for('pages.dashboard_page'))
    return render_template('admin.html')

@pages_bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('pages.login_page'))
