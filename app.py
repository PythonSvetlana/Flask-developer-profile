import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Конфигурация путей
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__, 
    template_folder=os.path.join(current_dir, 'templates'),
    static_folder=os.path.join(current_dir, 'static')
)

# Настройка подключения к базе данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(current_dir, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений для работы с БД и миграциями
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Пункт 01 и 05: Описание модели Notes с учетом колонки subtitle
class Notes(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)     # Заголовок (title)
    subtitle = db.Column(db.String(150), nullable=True)    # Подзаголовок (subtitle)
    text = db.Column(db.Text, nullable=False)             # Текст (text)

    def __repr__(self):
        return f"<Note {self.title}>"



# Главная страница: Таблица успеваемости и Профиль
@app.route('/')
def index():
    topics_data = [
        {"name": "Тема 1.<br>Flask", "progress": "100%", "hw": "100%", "comment": "Полный объем", "status": True},
        {"name": "Тема 2.<br>HTML/CSS", "progress": "100%", "hw": "100%", "comment": "Стилизован", "status": True},
        {"name": "Тема 3.<br>Шаблоны", "progress": "100%", "hw": "100%", "comment": "Jinja2 и наследование", "status": True},
        {"name": "Тема 4.<br>SQLAlchemy", "progress": "100%", "hw": "100%", "comment": "Интеграция СУБД и миграции", "status": True}, # Обновлен статус 4-й темы
        {"name": "Тема 5.<br>Auth", "progress": "", "hw": "", "comment": "", "status": False},
        {"name": "Тема 6.<br>REST API", "progress": "", "hw": "", "comment": "", "status": False},
        {"name": "Тема 7.<br>Проект", "progress": "", "hw": "", "comment": "", "status": False}
    ]
    return render_template('index.html', topics=topics_data)

# Пункт 03 и 04: Страница "Дневник программиста" с обработкой данных БД
@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if request.method == 'POST':
        # Сбор данных из полей формы
        input_title = request.form.get('title')
        input_subtitle = request.form.get('subtitle') # Получение подзаголовка
        input_text = request.form.get('content')
        
        if input_title and input_text:
            # Создание экземпляра модели и фиксация в БД
            new_note = Notes(title=input_title, subtitle=input_subtitle, text=input_text)
            db.session.add(new_note)
            db.session.commit()
            return redirect(url_for('notes'))
            
    # Пункт 04: Выгрузка всех существующих записей из БД для отображения на странице
    all_notes = Notes.query.order_by(Notes.id.desc()).all()
    return render_template('notes.html', notes=all_notes)

if __name__ == '__main__':
    app.run(debug=True)