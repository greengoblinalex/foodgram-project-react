# praktikum_new_diplom

## Развертывание проекта локально через Docker
1. Запускаем Docker Compose в режиме демона `docker compose -f docker-compose.yml up -d`
2. Выполняем миграции с помощью команды `docker compose exec backend python manage.py migrate`
3. Подключаем статику для админки `docker compose exec backend python manage.py collectstatic`
4. Перекидываем статику в нужное место `docker compose exec backend sh -c "cp -r /app/collected_static/. /backend_static/static/"`
5. Импортируем ингредиенты `docker compose exec backend python manage.py import_json data/ingredients.json`

