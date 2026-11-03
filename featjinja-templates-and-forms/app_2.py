import os
from flask import Flask, render_template, request, redirect, url_for

# Конфигурация абсолютных путей для директории Project_3
current_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__, 
    template_folder=os.path.join(current_dir, 'templates'),
    static_folder=os.path.join(current_dir, 'static')
)

# Хранилище записей дневника программиста (оперативная память)
notes_storage = {
    "Инициализация архитектуры": "Успешно развернуто базовое Flask-приложение, настроена маршрутизация и подключены статические файлы.",
    "Проектирование интерфейса": "Интерфейс личного кабинета полностью переведен на двухколоночный макет с использованием CSS Flexbox."
}

# Главная страница: Мониторинг успеваемости и Профиль
@app.route('/')
def index():
    # Матрица данных академического прогресса с флагами заполнения (status=True/False)
    topics_data = [
        {"name": "Тема 1.<br>Flask", "progress": "100%", "hw": "100%", "comment": "Полный объем", "status": True},
        {"name": "Тема 2.<br>HTML/CSS", "progress": "100%", "hw": "100%", "comment": "Стилизован", "status": True},
        {"name": "Тема 3.<br>Шаблоны", "progress": "100%", "hw": "100%", "comment": "Jinja2 и наследование", "status": True},
        {"name": "Тема 4.<br>SQLAlchemy", "progress": "", "hw": "", "comment": "", "status": False},
        {"name": "Тема 5.<br>Auth", "progress": "", "hw": "", "comment": "", "status": False},
        {"name": "Тема 6.<br>REST API", "progress": "", "hw": "", "comment": "", "status": False},
        {"name": "Тема 7.<br>Проект", "progress": "", "hw": "", "comment": "", "status": False}
    ]
    return render_template('index.html', topics=topics_data)

# Страница "Дневник программиста"
@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if title and content:
            notes_storage[title] = content
            return redirect(url_for('notes'))
            
    return render_template('notes.html', notes=notes_storage)

if __name__ == '__main__':
    app.run(debug=True)