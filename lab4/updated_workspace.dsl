workspace {
    !identifiers hierarchical
    model {
        admin = Person "Администратор" "Управляет сервисами и БД"
        user = Person "Участник" "Принимает участие в конференции"

        postgres_db = softwareSystem "PostgreSQL" {
            description "Хранит только данные пользователей (users)"
            tags "database"
        }

        mongodb = softwareSystem "MongoDB" {
            description "Хранит данные о конференциях (conferences) и докладах (reviews)"
            tags "database"
        }

        API = softwareSystem "API Gateway" {
            description "Общий вход для всех сервисов"
            tags "api-gateway"
        }

        conference_site = softwareSystem "Сайт конференции" {
            description "Служит для управления пользователями, докладами и конференциями"
            tags "main-system"

            user_service = container "User Service" {
                description "Обрабатывает аутентификацию и управление пользователями"
                technology "Python, FastAPI"
                tags "rest-api auth-service"
            }

            review_service = container "Review Service" {
                description "Управляет докладами (MongoDB)"
                technology "Python, FastAPI"
                tags "rest-api"
            }

            conference_service = container "Conference Service" {
                description "Управляет конференциями (MongoDB)"
                technology "Python, FastAPI"
                tags "rest-api"
            }

            API -> user_service "HTTP Запросы"
            API -> review_service "HTTP Запросы"
            API -> conference_service "HTTP Запросы"
            
            user_service -> postgres_db "SQL - таблица users"
            review_service -> mongodb "MongoDB - коллекция reviews"
            conference_service -> mongodb "MongoDB - коллекция conferences"
            
            review_service -> conference_service "REST: Добавление докладов в конференцию"
            user_service -> review_service "JWT валидация"
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

        dynamic conference_site "User_Registration" "Регистрация" {
            autolayout lr
            description "Регистрация нового пользователя (PostgreSQL)"

            user -> API "HTTP POST /users/"
            API -> conference_site.user_service "REST API"
            conference_site.user_service -> postgres_db "INSERT INTO users"
        }

        dynamic conference_site "Conference_Creation" "Создание конференции" {
            autolayout lr
            description "Создание новой конференции (MongoDB)"

            admin -> API "HTTP POST /conferences/ (с JWT)"
            API -> conference_site.conference_service "REST API (JWT)"
            conference_site.conference_service -> mongodb "db.conferences.insert()"
        }

        dynamic conference_site "Add_Review" "Добавление доклада" {
            autoLayout lr
            description "Добавление доклада в конференцию (MongoDB)"

            admin -> API "HTTP POST /reviews/ (с JWT)"
            API -> conference_site.review_service "REST API (JWT)"
            conference_site.review_service -> conference_site.conference_service "Проверка conference_id"
            conference_site.review_service -> mongodb "db.reviews.insert()"
        }

        dynamic conference_site "Docker_Deployment" "Развертывание сервиса" {
            autolayout lr
            description "Архитектура развертывания в Docker"
            
            conference_site.user_service -> conference_site.review_service "Docker сеть"
            conference_site.review_service -> conference_site.conference_service "Docker сеть"
            
            conference_site.user_service -> postgres_db "Docker volume (postgres_data)"
            conference_site.conference_service -> mongodb "Docker volume (mongo_data)"
            conference_site.review_service -> mongodb "Docker volume (mongo_data)"
            
            API -> conference_site.user_service "Порт :8000"
            API -> conference_site.review_service "Порт :8001"
            API -> conference_site.conference_service "Порт :8002"
        }
    }
}