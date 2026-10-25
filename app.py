import os
import sqlite3
from flask import Flask, render_template
from flask.json.provider import DefaultJSONProvider
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, sqlite3.Row):
            return dict(obj)
        return super().default(obj)

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    app.json_provider_class = CustomJSONProvider
    app.json = CustomJSONProvider(app)
    app.url_map.strict_slashes = False
    
    # Load config
    app.config.from_object('config.Config')
    
    # Ensure directories exist
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    os.makedirs('database', exist_ok=True)
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'pages.login_page'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        user_data = User.get_by_id(int(user_id))
        if user_data:
            from models.user import UserLogin
            return UserLogin(user_data)
        return None

    @app.context_processor
    def inject_user():
        from flask_login import current_user
        return dict(user=current_user)
    
    # Initialize database
    from models.db import init_app, init_db
    init_app(app)
    
    with app.app_context():
        init_db()
        # Create admin if not exists
        try:
            from services.auth_service import create_admin_if_not_exists
            create_admin_if_not_exists()
        except ImportError:
            pass
    
    # Register blueprints
    from routes.pages import pages_bp
    from routes.auth import auth_bp
    from routes.family_members import family_bp
    from routes.medical_records import records_bp
    from routes.documents import documents_bp
    from routes.prescriptions import prescriptions_bp
    from routes.medicines import medicines_bp
    from routes.reminders import reminders_bp
    from routes.appointments import appointments_bp
    from routes.tests import tests_bp
    from routes.vaccinations import vaccinations_bp
    from routes.health_parameters import health_params_bp
    from routes.expenses import expenses_bp
    from routes.insurance import insurance_bp
    from routes.notifications import notifications_bp
    from routes.export import export_bp
    from routes.search import search_bp
    from routes.admin import admin_bp
    from routes.users import users_bp
    from routes.dashboard import dashboard_bp
    from routes.emergency import emergency_bp
    from routes.timeline import timeline_bp
    
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(family_bp, url_prefix='/api/family-members')
    app.register_blueprint(records_bp, url_prefix='/api/records')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(prescriptions_bp, url_prefix='/api/prescriptions')
    app.register_blueprint(medicines_bp, url_prefix='/api/medicines')
    app.register_blueprint(reminders_bp, url_prefix='/api/reminders')
    app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
    app.register_blueprint(tests_bp, url_prefix='/api/tests')
    app.register_blueprint(vaccinations_bp, url_prefix='/api/vaccinations')
    app.register_blueprint(health_params_bp, url_prefix='/api/health-parameters')
    app.register_blueprint(expenses_bp, url_prefix='/api/expenses')
    app.register_blueprint(insurance_bp, url_prefix='/api/insurance')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(export_bp, url_prefix='/api/export')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(emergency_bp, url_prefix='/api/emergency')
    app.register_blueprint(timeline_bp, url_prefix='/api/timeline')
    
    # Exempt API blueprints from CSRF if using token header
    csrf.exempt(auth_bp)
    csrf.exempt(family_bp)
    csrf.exempt(records_bp)
    csrf.exempt(documents_bp)
    csrf.exempt(prescriptions_bp)
    csrf.exempt(medicines_bp)
    csrf.exempt(reminders_bp)
    csrf.exempt(appointments_bp)
    csrf.exempt(tests_bp)
    csrf.exempt(vaccinations_bp)
    csrf.exempt(health_params_bp)
    csrf.exempt(expenses_bp)
    csrf.exempt(insurance_bp)
    csrf.exempt(notifications_bp)
    csrf.exempt(export_bp)
    csrf.exempt(search_bp)
    csrf.exempt(admin_bp)
    csrf.exempt(users_bp)
    csrf.exempt(dashboard_bp)
    csrf.exempt(emergency_bp)
    csrf.exempt(timeline_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    import os
    import socket
    import werkzeug.serving as ws

    # Enable dual-stack IPv4/IPv6 socket binding on Windows so localhost (::1 and 127.0.0.1) both work
    orig_bind = ws.BaseWSGIServer.server_bind
    def dual_stack_bind(self):
        if hasattr(socket, 'IPV6_V6ONLY') and self.address_family == socket.AF_INET6:
            try:
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except Exception:
                pass
        orig_bind(self)
    ws.BaseWSGIServer.server_bind = dual_stack_bind

    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '::')
    try:
        app.run(host=host, port=port, debug=True)
    except Exception:
        app.run(host='0.0.0.0', port=port, debug=True)

