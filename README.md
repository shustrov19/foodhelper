# Foodgram
## Описание 
Проект Foodgram c backend на Django, c контейниразацией Docker и CI/CD. Благодаря этому проекту, можно на сайт [Foodgram](https://food-helper.ddns.net/) создавать разные рецепты, подписываться на авторов, добавлять рецепты в избранное и корзину, скачивать список ингредиентов необходимых для приготовления блюд.

**Проект Foodgram [https://food-helper.ddns.net/](https://food-helper.ddns.net/)**

**API-документация [https://food-helper.ddns.net/api/docs/](https://food-helper.ddns.net/api/docs/)**

**Админка [https://food-helper.ddns.net/admin/](https://food-helper.ddns.net/admin/)** 
* username: admin 
* пароль: admin

## Технологии 
- Python 3.10
- Django 4.1
- Nginx 1.19
- Gunicorn 20.1
- React
- Django Rest Framework 3.14
- Certbot
- Docker
- PosgreSQL 13.10
- GitHub Actions

## Инструкция по запуску на локальном сервере

1. Клонирование проекта с GitHub на локальный компьютер
```
git clone git@github.com:shustrov19/foodgram-project-react.git
```
2. В директории проекта перейдите в директорию infra/.
3. Создайте файл .env в директории infra/ и заполните его. Переменные для работы проекта перечислены в файле .env.example, находящемся в директории infra/.
3. Запустите в терминале контейнеры Docker внутри папки infra:
```
docker compose up --build
``` 
4. Выполните миграции в другом терминале:
```
docker compose exec backend python manage.py migrate
```
5. Создайте администратора:
```
docker compose exec backend python manage.py createsuperuser
```
6. Соберите статику backend:
```
docker compose exec backend python manage.py collectstatic
```
7. Загрузите в базу данных ингредиенты и теги :
```
docker compose exec backend python manage.py load_ingredients
docker compose exec backend python manage.py load_tags
```
8. Перейдите на сайт:
```
https://localhost:8080
```
## Инструкция по запуску на удалённом сервере
### Создание Docker-образов и загрузка на Docker Hub
1. В терминале в корне проекта foodgram-project-react последовательно выполните следующие команды; замените username на ваш логин на Docker Hub.
```
cd frontend
docker build -t username/foodgram_frontend .
cd ../backend  
docker build -t username/foodgram_backend .
```
2. Загрузите образы на Docker Hub
```
docker push username/foodgram_frontend
docker push username/foodgram_backend
```
### Деплой на сервер
1. В терминале Git Bash введите:
```
ssh -i путь_до_SSH_ключа/название_файла_с_SSH_ключом_без_расширения login@ip
```
2. Создайте директорию foodgram
```
mkdir foodgram
```
3. Установите Docker Compose на сервер:
```
cd
sudo apt update
sudo apt install curl
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose
```
4. Замените в файле docker-compose.production.yml в пункте backend:
```
image: <username>/foodgram_backend
```
где username - ваш логин на Docker Hub 

5. Замените в файле docker-compose.production.yml в пункте frontend:
```
image: <username>/foodgram_frontend
```
где username - ваш логин на Docker Hub

6. Скопируйте файлы docker-compose.production.yml, nginx.conf и .env в директорию foodgram на сервер. Для этого зайдите на своём компьютере в директорию foodgram-project-react/infra и выполните в Git Bash команду копирования:
```
scp -i <path_to_SSH>/<SSH_name> docker-compose.production.yml \
    <username>@<server_ip>:/home/<username>/foodgram/docker-compose.production.yml 
```
```
scp -i <path_to_SSH>/<SSH_name> nginx.conf \
    <username>@<server_ip>:/home/<username>/foodgram/nginx.conf 
```
```
scp -i <path_to_SSH>/<SSH_name> .env \
    <username>@<server_ip>:/home/<username>/foodgram/.env 
```
где:
* path_to_SSH — путь к файлу с SSH-ключом;
* SSH_name — имя файла с SSH-ключом (без расширения);
* username — ваше имя пользователя на сервере;
* server_ip — IP вашего сервера.
7. Для запуска Docker Compose в режиме демона выполните команду:
```
sudo docker compose -f docker-compose.production.yml up -d
```
8. Выполните миграции из директории foodgram
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
9. Соберите статику backend
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```
10. На сервере в редакторе nano откройте конфиг Nginx
```
nano /etc/nginx/sites-enabled/default
```
11. Измените настройки 
```
server_name <ваш_домен>
location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:8080;
}
```
11. Выполните команду проверки конфигурации:
```
sudo nginx -t 
```
12. Перезапустите Nginx:
```
sudo service nginx reload 
```
### Автоматизация деплоя CI/CD
В папке проекта на локальном компьютере есть файл workflow main.yml
```
foodgram-project-react/.github/workflows/main.yml
```
При каждом изменении проекта и его загрузке на GitHub, на сервере будет автоматически обноваляться код, перед этим проходя проверку тестами. При положительном результате вам придёт сообщение в телеграм о том, что деплой прошел успешно.
Для использования данного файла необходимо на сайте [GitHub](https://github.com/) перейти в **Settings** проекта -> **Secrets and variables** -> **Actions** и поменять следующие значения на свои
```
DOCKER_USERNAME - имя пользователя в DockerHub
DOCKER_PASSWORD - пароль пользователя в DockerHub
HOST            - IP-адрес сервера
USER            - имя пользователя на сервере
SSH_KEY         - содержимое приватного SSH-ключа
SSH_PASSPHRASE  - PASSPHRASE для SSH-ключа
TELEGRAM_TO     - ID вашего телеграм-аккаунта
TELEGRAM_TOKEN  - токен вашего бота 
```

### Автор 
[Виктор Шустров](https://github.com/shustrov19)

### Контакты
email: shustrov19@gmail.com
Telegram: [@Shustrov19](https://t.me/Shustrov19)

