import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Инициализация и конфигурация путей окружения
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__, 
    template_folder=os.path.join(current_dir, 'templates'),
    static_folder=os.path.join(current_dir, 'static')
)

# Системная конфигурация безопасности сессий и СУБД SQLite
app.config['SECRET_KEY'] = 'academic-super-secret-key-1205'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(current_dir, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация подсистемы базы данных и миграций
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Настройка подсистемы авторизации Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Перенаправление неавторизованных пользователей


# Классы моделей СУБД (Объявление структуры таблиц)


class Users(UserMixin, db.Model):
    """Модель авторизованных пользователей с поддержкой UUID-токенов"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)            # Криптографический хеш пароля
    token = db.Column(db.String(100), unique=True, nullable=True)   # Системный токен доступа

class Notes(db.Model):
    """Модель записей для раздела хроники «Дневник программиста»"""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(150), nullable=True)
    text = db.Column(db.Text, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    """Обязательный метод Flask-Login для извлечения объекта пользователя по ID"""
    return Users.query.get(int(user_id))


# Маршрутизация и бизнес-логика (Контроллеры)

@app.route('/home')
def home():
    """Начальная приветственная страница (экран-заглушка)"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/')
@login_required 
def index():
    """Главная страница — Личный кабинет со стеком и таблицей успеваемости"""
    topics_data = [
        {"name": "Тема 1.<br>Flask", "progress": "100%", "hw": "100%", "comment": "Полный объем", "status": True},
        {"name": "Теma 2.<br>HTML/CSS", "progress": "100%", "hw": "100%", "comment": "Блог стилизован", "status": True},
        {"name": "Тема 3.<br>Шаблоны", "progress": "100%", "hw": "100%", "comment": "Jinja2 и наследование", "status": True},
        {"name": "Тема 4.<br>SQLAlchemy", "progress": "100%", "hw": "100%", "comment": "Интеграция СУБД и миграции", "status": True},
        {"name": "Тема 5.<br>Auth", "progress": "100%", "hw": "100%", "comment": "Система авторизации и токены", "status": True},
        {"name": "Тема 6.<br>REST API", "progress": "", "hw": "", "comment": "", "status": False},
        {"name": "Тема 7.<br>Проект", "progress": "", "hw": "", "comment": "", "status": False}
    ]
    return render_template('index.html', topics=topics_data, user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового аккаунта с генерацией соли и уникального UUID токена"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Проверка дублирования логина или email в БД
        if Users.query.filter((Users.username == username) | (Users.email == email)).first():
            flash('Пользователь с таким логином или email уже существует.', 'danger')
            return redirect(url_for('register'))
        
        # Хеширование пароля методом pbkdf2
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Создание записи пользователя со стартовым UUID-токеном
        new_user = Users(username=username, email=email, password=hashed_password, token=str(uuid.uuid4()))
        db.session.add(new_user)
        db.session.commit()
        
        flash('Регистрация успешно завершена! Войдите в профиль.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Авторизация пользователя, верификация хеша и динамическое обновление токена"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Users.query.filter_by(username=username).first()
        
        # Проверка существования записи и сверка хеш-кода пароля
        if user and check_password_hash(user.password, password):
            # При каждом новом входе генерируем и обновляем сессионный токен доступа
            user.token = str(uuid.uuid4())
            db.session.commit()
            
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Безопасный выход пользователя с уничтожением токена сессии куки"""
    logout_user()
    return redirect(url_for('home'))

@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    """Управление разделом хроники «Дневник программиста»"""
    if request.method == 'POST':
        input_title = request.form.get('title')
        input_subtitle = request.form.get('subtitle')
        input_text = request.form.get('content')
        
        # Запись новой хроники в SQLite при условии заполнения обязательных полей
        if input_title and input_text:
            new_note = Notes(title=input_title, subtitle=input_subtitle, text=input_text)
            db.session.add(new_note)
            db.session.commit()
            return redirect(url_for('notes'))
            
    # Извлечение архива записей с обратной сортировкой (от новых к старым)
    all_notes = Notes.query.order_by(Notes.id.desc()).all()
    return render_template('notes.html', notes=all_notes)

if __name__ == '__main__':
    app.run(debug=True)