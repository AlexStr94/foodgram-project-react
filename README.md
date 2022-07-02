# Дипломный проект по специальности Python-разработчик

**Описание сервиса**

Cайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов в формате PDF, необходимых для приготовления одного или нескольких выбранных блюд.

**Описание дипломного проекта**

В рамках дипломного проекта был создан бекенд для сайта, написанный на фреймворке Django. Было реализовано API с использованием Django REST Framework.

**Запуск проекта на локальном компьютере**

Необходимо скопировать проект:

```
git clone https://github.com/AlexStr94/foodgram-project-react.git
```

Перейти в папку 'infra'

```
cd infra
```

Запустить Docker Compose

```
docker-compose up
```

Следует учитывать, что согласно инструкции, размещенной в файле docker-compose.yml, Docker не собирает бекенд, а скачивает его из образа. Поэтому в случае редактирования проекта, необходимо изменить инструкцию в файле docker-compose.yml .

После запуска Docker Compose, необходимо выполнить миграции, создать суперпользователя и собрать статистические файлы:

```
docker-compose exec <id контейнера с Django> python manage.py migrate
docker-compose exec <id контейнера с Django> python manage.py createsuperuser
docker-compose exec <id контейнера с Django> python manage.py collectstatic --no-input
```

**Запуск проекта на сервере**

На сервер необходимо скопировать следующие папки и файлы (все должны размещаться в одной директории):
- docker-compose.yml
- nginx.conf
- frontend/
- docs/ (Redoc, опционально)

В файле docker-compose.yml необходимо заменить строчку:

```
context: ../frontend
```

на:

```
context: ./frontend
```

Далее необходимо запустить Docker Compose:

```
docker-compose up
```

После запуска Docker Compose, необходимо выполнить миграции, создать суперпользователя и собрать статистические файлы:

```
docker-compose exec <id контейнера с Django> python manage.py migrate
docker-compose exec <id контейнера с Django> python manage.py createsuperuser
docker-compose exec <id контейнера с Django> python manage.py collectstatic --no-input
```

После установки документация API доступна по адресу: /api/docs/

HOST: 130.193.55.238
Admin: 
-Username: admin
-Password: admin