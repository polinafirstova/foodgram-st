# Foodgram — Социальная сеть рецептов

Foodgram — это веб-приложение, позволяющее пользователям делиться своими любимыми рецептами, добавлять чужие рецепты в избранное, подписываться на публикации других авторов и создавать списки покупок.

## Особенности

*   **Регистрация и аутентификация:** пользователи могут создавать аккаунты с указанием имени, фамилии, никнейма, email и пароля, а также безопасно входить в систему. Аутентификация реализована с использованием токенов.
*   **Просмотр рецептов:** доступен просмотр рецептов на главной странице (с пагинацией), на странице пользователя и на странице подписок. Рецепты отсортированы по дате публикации (от новых к старым).
*   **Подписки:** зарегистрированные пользователи могут подписываться на других авторов и видеть их рецепты на странице «Мои подписки».
*   **Избранное:** зарегистрированные пользователи могут добавлять рецепты в избранное и просматривать свой список избранных рецептов.
*   **Список покупок:** зарегистрированные пользователи могут добавлять ингредиенты из рецептов в свой список покупок и скачивать его в формате .txt. Ингредиенты в списке суммируются.
*   **Создание и редактирование рецептов:** зарегистрированные пользователи могут создавать, редактировать и удалять свои рецепты.
*   **Страница пользователя:** отображает имя пользователя, список его рецептов и кнопку для подписки/отписки.
*   **API:** REST API, реализованный в соответствии со спецификацией.
*   **Админ-панель:** админ-панель Django для управления пользователями, рецептами, ингредиентами и другими моделями.
*   **Статические страницы:** «О проекте» и «Технологии».
*   **Изменение пароля и аватара:** зарегистрированные пользователи могут изменять свой пароль и аватар.

## Технологии

*   Python 3.12
*   Django 4.2
*   Django REST Framework
*   Gunicorn
*   PostgreSQL
*   Nginx
*   React
*   Docker
*   Docker Compose
*   GitHub Actions

## Архитектура проекта

Проект состоит из следующих контейнеров:

*   **db:** контейнер с СУБД PostgreSQL. Используется официальный образ `postgres:14`.
*   **backend:** контейнер с бэкендом (Django + Gunicorn). Образ `polinafirstova/foodgram-backend:latest` опубликован на [Docker Hub](https://hub.docker.com/).
*   **frontend:** контейнер с фронтендом (React). Образ `polinafirstova/foodgram-frontend:latest` опубликован на [Docker Hub](https://hub.docker.com/).
*   **nginx:** контейнер с веб-сервером Nginx. Используется официальный образ `nginx:1.25.4-alpine`.


## Запуск проекта

**С использованием Docker Compose:**

1.  **Склонируйте репозиторий:**

    ```bash
    git clone https://github.com/polinafirstova/foodgram-st.git
    ```

2. **Перейдите в директорию `backend`:**

    ```bash
    cd backend
    ```

3.  **Скопируйте файл `.env.example` и переименуйте его в `.env`:**

    ```bash
    cp .env.example .env
    ```
4.  **Заполните файл `.env` своими данными:**

    ```bash
    POSTGRES_DB=your_database_name
    POSTGRES_USER=your_database_user
    POSTGRES_PASSWORD=your_database_password
    SECRET_KEY=your_secret_key
    ```
    
    *   `SECRET_KEY` — cекретный ключ Django. Сгенерируйте случайную строку (например, с помощью `python -c "import secrets; print(secrets.token_hex())"`).
    *   `DATABASE_NAME` — имя базы данных PostgreSQL.
    *   `DATABASE_USER` — имя пользователя PostgreSQL.
    *   `DATABASE_PASSWORD` — пароль пользователя PostgreSQL.

5.  **Перейдите в директорию `infra`:**

    ```bash
    cd ../infra
    ```

6.  **Запустите проект с помощью Docker Compose:**

    ```bash
    docker-compose up -d
    ```

    Эта команда скачает образы `polinafirstova/foodgram-backend:latest` и `polinafirstova/foodgram-frontend:latest` с Docker Hub, а также образы `postgres:14` и `nginx:1.25.4-alpine`, и запустит все контейнеры. Убедитесь, что Docker Desktop запущен.

7.  **Дождитесь запуска всех контейнеров:**

    Это может занять несколько минут.

8.  **Откройте проект в браузере:**

    Перейдите по [ссылке](http://localhost/) в своем браузере.

**Развертывание без Docker (Альтернативный способ):**

Эти инструкции предполагают, что у вас установлены Python 3.12 и PostgreSQL.

1.  **Клонируйте репозиторий:**

    ```bash
    git clone https://github.com/polinafirstova/foodgram-st.git
    ```

2.  **Создайте и активируйте виртуальное окружение:**

    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate  # Для Linux/macOS
    venv\Scripts\activate  # Для Windows
    ```

3.  **Установите зависимости:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Настройте PostgreSQL:**

    *   Убедитесь, что PostgreSQL установлен и запущен.
    *   Создайте базу данных, пользователя и предоставьте пользователю права на эту базу данных.

5.  **Настройте Django:**

    1.    **Скопируйте файл `.env.example` и переименуйте его в `.env`:**

            ```bash
            cp .env.example .env
            ```
    2.  **Заполните файл `.env` своими данными:**

        ```bash
        POSTGRES_DB=your_database_name
        POSTGRES_USER=your_database_user
        POSTGRES_PASSWORD=your_database_password
        SECRET_KEY=your_secret_key
        ```
        
        *   `SECRET_KEY` — cекретный ключ Django. Сгенерируйте случайную строку (например, с помощью `python -c "import secrets; print(secrets.token_hex())"`).
        *   `DATABASE_NAME` — имя базы данных PostgreSQL.
        *   `DATABASE_USER` — имя пользователя PostgreSQL.
        *   `DATABASE_PASSWORD` — пароль пользователя PostgreSQL.

    3.    **Измените настройки базы данных в `backend/settings.py` на свои:**

            Укажите параметры подключения к вашей базе данных PostgreSQL. Убедитесь, что значения `HOST` и `PORT` соответствуют настройкам вашей базы данных. Для локального запуска PostgreSQL `HOST` может быть `localhost` или `127.0.0.1.`. `PORT` обычно равен `5432` для PostgreSQL.

            ```python
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'NAME': os.environ['POSTGRES_DB'],
                    'USER': os.environ['POSTGRES_USER'],
                    'PASSWORD': os.environ['POSTGRES_PASSWORD'],
                    'HOST': 'db',
                    'PORT': 5432,
                }
            }
            ```
    4.    Выполните миграции:

            ```bash
            python manage.py migrate
            ```

    5.    Создайте суперпользователя:

            ```bash
            python manage.py createsuperuser
            ```

6.  **Загрузите фикстуры (необязательно):**

    Если вы хотите загрузить стартовые данные:

    ```bash
    python manage.py load_data --type ingredients
    python manage.py load_data --type users
    python manage.py load_data --type recipes
    ```

7.  **Запустите сервер Django:**

    ```bash
    python manage.py runserver
    ```
    
8.  **Откройте проект в браузере:**

    Перейдите по [ссылке](http://localhost:8000/) в своем браузере.

## Дополнительные инструкции

*   **API:**
    *   Документация API доступна по адресу `http://localhost/api/docs/` (если запущено с Docker) или `http://localhost:8000/api/docs/` (если запущено без Docker).
*   **Админ-панель:**
    *   Админ-панель доступна по адресу `http://localhost/admin/` (если запущено с Docker) или `http://localhost:8000/admin/` (если запущено без Docker).

## CI/CD

Автоматическая сборка и публикация образов на Docker Hub настроены с помощью GitHub Actions. При каждом push в ветку `main` backend автоматически проверяется, собирается и публикуется на Docker Hub.
