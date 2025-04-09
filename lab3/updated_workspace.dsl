workspace {
    !identifiers hierarchical
    model {
        admin = Person "Администратор" "Управляет сервисами и БД"
        user = Person "Участник" "Принимает участие в конференции"

        postgres_db = softwareSystem "База данных/ PostgreSQL" {
            description "Хранит данные о пользователях (users), докладах (reviews) и конференциях (conferences)"
        }

        API = softwareSystem "API Getaway" {
            description "Общий вход для всех сервисов"
        }

        conference_site = softwareSystem "Сайт конференции" {
            description "Служит для управления пользователями, докладами и конференциями"

            user_service = container "Пользовательский сервис авторизации" {
                description "Обрабатывает /token и аутентификацию"
                technology "Python, FastAPI"
                tags "rest-api"
            }

            review_service = container "Сервис докладов" {
                description "Управляет докладами"
                technology "Python, FastAPI"
                tags "rest-api"
            }

            conference_service = container "Сервис конференций" {
                description "Управляет конференциями"
                technology "Python, FastAPI"
                tags "rest-api"
            }

            API -> user_service "HTTP Запросы"
            API -> review_service "HTTP Запросы"
            API -> conference_service "HTTP Запросы"
            user_service -> postgres_db "SQL - таблица users"
            review_service -> conference_service "REST: Добавление докладов в конференцию по conference_id"
            review_service -> postgres_db "SQL - таблица reviews"
            conference_service -> postgres_db "SQL - таблица conferences"
            user_service -> review_service

        }

        user -> API "HTTP Запросы"
        admin -> API "HTTP Запросы"
        API -> conference_site "Запросы на сайте"

    }

    views {
        systemContext conference_site "c1" {
            include *
            autoLayout
        }

        container conference_site "c2" {
            include *
            autoLayout
        }

        dynamic conference_site "User_Registration" "Регистрация пользователя" {
            autolayout lr
            description "Сценарий регистрации нового пользователя"

            user -> API "HTTP POST /users/"
            API -> conference_site.user_service "REST API"
            conference_site.user_service -> postgres_db "Сохранить данные пользователя"
        }

        dynamic conference_site "User_Login" "Аутентификация пользователя" {
            autolayout lr
            description "Сценарий входа пользователя и получения JWT токена"

            user -> API "HTTP POST /token"
            API -> conference_site.user_service "REST API"
            conference_site.user_service -> postgres_db "Проверить учетные данные"
        }

        dynamic conference_site "Add_Participant" "Добавление пользователя" {
            autolayout lr
            description "Сценарий добавления нового пользователя (требуется JWT токен)"

            admin -> API "HTTP POST /users/ (с JWT)"
            API -> conference_site.user_service "REST API (JWT)"
            conference_site.user_service -> postgres_db "Сохранить данные участника"
        }

        dynamic conference_site "Get_User_Profile" "Получение профиля" {
            autolayout lr
            description "Сценарий получения профиля пользователя (требуется JWT)"

            user -> API "HTTP GET /users/me (с JWT)"
            API -> conference_site.user_service "REST API (JWT)"
            conference_site.user_service -> postgres_db "Получить данные пользователя"
        }

        dynamic conference_site "Add_Review" "Добавление доклада" {
            autoLayout lr
            description "Сценарий добавления доклада в конференцию (требуется JWT)"

            admin -> API "HTTP POST /reviews/ (с JWT)"
            API -> conference_site.review_service "REST API (JWT)"
            conference_site.review_service -> conference_site.conference_service "REST API (JWT)"
            conference_site.conference_service -> postgres_db "Сохранить данные выступления"
        }

        dynamic conference_site "Docker_Deployment" "Развертывание в Docker" {
            autolayout lr
            description "Архитектура развертывания сервисов в Docker"
            
            conference_site.user_service -> conference_site.review_service "Docker cеть"
            conference_site.review_service -> conference_site.conference_service "Docker cеть"
            conference_site.conference_service -> postgres_db "Docker volume (postgres_data)"
            
            API -> conference_site.user_service "Docker порт : 8000"
            API -> conference_site.review_service "Docker порт : 8001"
            API -> conference_site.conference_service "Docker порт : 8002"
            postgres_db -> conference_site.user_service "Docker PostgreSQL контейнер"
        }
    }
}