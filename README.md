# Установка
python3 -m venv venv

source venv/bin/activate

pip install django

python manage.py migrate

# Запуск сервера
python3 manage.py runserver

# Админ
login - test
pass - test