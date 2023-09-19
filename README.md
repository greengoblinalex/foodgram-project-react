<h1 align="center">Всем привет! Меня зовут <a href="https://github.com/greengoblinalex" target="_blank">Алексей</a> и я автор данного проекта
<img src="https://github.com/blackcater/blackcater/raw/main/images/Hi.gif" height="32"/></h1>

# Foodgram
![Deploy badge](github.com/greengoblinalex/foodgram-project-react/actions/workflows/main.yaml/badge.svg)

## Описание

Проект Foogram - это сервис, который позволяет создавать свои рецепты, смотреть рецепты других пользователей,
подписываться на понравившихся пользователей, добавлять рецепты в избранное и список покупок. После добавления
рецептов в список покупок, мы можем скачать список всех ингредиентов, которые необходимы нам для данных рецептов.

## Использованные технологии
- Django
- React
- Docker
- DockerHub
- Git
- GitHub
- Nginx
- Gunicorn

## Отличия версий docker-compose.yml
docker-compose.yml используется в локальной версии, когда
вам нужно протестировать проект. В нем используются build для докер из проекта.

docker-compose.production.yml используется в продакшен версии, когда
мы выкладываем проект в открытый доступ. В нем используются image для докера из Docker Hub.

## Развертывание проекта локально через Docker
1. Запускаем Docker Compose в режиме демона `docker compose -f docker-compose.yml up -d`
2. Выполняем миграции с помощью команды `docker compose exec backend python manage.py migrate`
3. Подключаем статику для админки `docker compose exec backend python manage.py collectstatic`
4. Перекидываем статику в нужное место `docker compose exec backend sh -c "cp -r /app/collected_static/. /backend_static/static/"`
5. Импортируем ингредиенты `docker compose exec backend python manage.py import_json data/ingredients.json`
6. Создаем админа `docker compose exec backend python manage.py createsuperuser`
7. Заходим в панель админа и добавляем нужные тэги(завтрак, обед, ужин)

## Развертывание проекта на сервере
1. Устанавливаем Docker Compose на сервер
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin 
```
2. Устанавливаем и запускаем nginx
```
sudo apt install nginx
sudo systemctl start nginx
```
3. Через редактор Nano откройте файл конфигурации веб-сервера
```
sudo nano /etc/nginx/sites-enabled/default
```
4. Удалите все настройки из файла, запишите и сохраните новые
```
server {
    listen 80;
    server_name публичный_ip_вашего_удалённого_сервера;
    
    location / {
        proxy_set_header HOST $host;
        proxy_pass http://127.0.0.1:9000;
    }

} 
```
3. Создаём деррикторию проекта на сервере
4. Копируем в данную деррикторию docker-compose.production.yml и создаём .env, после чего прописываем в нем нужные данные, как в .env.example
5. Запускаем Docker Compose в режиме демона 
```
sudo docker compose -f docker-compose.production.yml up -d
```
6. Выполняем миграции с помощью команды 
```
docker compose exec backend python manage.py migrate
```
7. Подключаем статику для админки 
```
docker compose exec backend python manage.py collectstatic
```
8. Перекидываем статику в нужное место 
```
docker compose exec backend sh -c "cp -r /app/collected_static/. /backend_static/static/"
```
9. Импортируем ингредиенты 
```
docker compose exec backend python manage.py import_json data/ingredients.json
```
10. Создаем админа 
```
docker compose exec backend python manage.py createsuperuser
```
11. Заходим в панель админа и добавляем нужные тэги(завтрак, обед, ужин)


## Развертывание проекта с использованием CI/CD
1. Делаем Fork репозитория
2. Заходим в settings сфоркнутого репозитория и прописываем все Secrets:
DOCKER_PASSWORD - Пароль от dockerhub
DOCKER_USERNAME - Username от dockerhub
USER - username хоста
HOST - ip хоста
SSH_KEY - ssh-ключ хоста
SSH_PASSPHRASE - пароль хоста
TELEGRAM_TO - id вашего телеграма
TELEGRAM_TOKEN - токен вашего телеграм-бота
3. Устанавливаем Docker Compose на сервер
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin 
```
4. Устанавливаем и запускаем nginx
```
sudo apt install nginx
sudo systemctl start nginx
```
5. Через редактор Nano откройте файл конфигурации веб-сервера
```
sudo nano /etc/nginx/sites-enabled/default
```
6. Удалите все настройки из файла, запишите и сохраните новые
```
server {
    listen 80;
    server_name публичный_ip_вашего_удалённого_сервера;
    
    location / {
        proxy_set_header HOST $host;
        proxy_pass http://127.0.0.1:9000;
    }

} 
```
7. Создаём деррикторию проекта на сервере
8. Копируем в данную деррикторию docker-compose.production.yml и создаём .env, после чего прописываем в нем нужные данные, как в .env.example
9. Запускаем Docker Compose в режиме демона 
```
sudo docker compose -f docker-compose.production.yml up -d
```
10. Выполняем миграции с помощью команды 
```
docker compose exec backend python manage.py migrate
```
11. Подключаем статику для админки 
```
docker compose exec backend python manage.py collectstatic
```
12. Перекидываем статику в нужное место 
```
docker compose exec backend sh -c "cp -r /app/collected_static/. /backend_static/static/"
```
13. Импортируем ингредиенты 
```
docker compose exec backend python manage.py import_json data/ingredients.json
```
14. Создаем админа 
```
docker compose exec backend python manage.py createsuperuser
```
15. Заходим в панель админа и добавляем нужные тэги(завтрак, обед, ужин)
16. Теперь при пуше коммитов в ветку main будет происходить автоматическое тестирование, обновление image на dockerhub и деплой проекта на сервер

## <a href="https://simonov-tech.online" target="_blank">Развернутый проект</a>
