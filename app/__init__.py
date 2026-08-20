import json
import os
from flask import Flask, session, g
from .config import Config
from .models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Load translations
    def load_translations():
        translations = {}
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        translations_dir = os.path.join(base_dir, 'translations')
        
        for lang in ['en', 'fr']:
            file_path = os.path.join(translations_dir, f'strings_{lang}.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    translations[lang] = json.load(f)
            except FileNotFoundError:
                translations[lang] = {}
        return translations

    app.translations = load_translations()

    @app.before_request
    def before_request():
        # Set language
        lang = session.get('lang', 'en')
        g.lang = lang
        g.strings = app.translations.get(lang, {})
        
        # Set theme
        g.theme = session.get('theme', 'light')

    @app.context_processor
    def inject_globals():
        return {
            't': lambda key: g.strings.get(key, key),
            'lang': g.lang,
            'theme': g.theme
        }

    # Register blueprints
    from .auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .stock.routes import bp as stock_bp
    app.register_blueprint(stock_bp, url_prefix='/stock')

    from .sales.routes import bp as sales_bp
    app.register_blueprint(sales_bp, url_prefix='/sales')
    
    from .reports.routes import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')

    from .staff.routes import bp as staff_bp
    app.register_blueprint(staff_bp, url_prefix='/staff')

    from .main.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
