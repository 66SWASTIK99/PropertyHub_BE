pip install -r requirements.txt || exit /b
python manage.py collectstatic --no-input || exit /b
python manage.py migrate || exit /b