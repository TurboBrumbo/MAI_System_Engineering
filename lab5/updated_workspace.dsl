workspace {
    !identifiers hierarchical
    model {
        admin = person "Администратор" "Управляет сервисами и БД"
        user = person "Участник" "Принимает участие в конференции"
        tester = person "Тестировщик" "Проводит нагрузочное тестирование"

        postgres_db = softwareSystem "PostgreSQL" {
            description "Хранит только данные пользователей (users)"
            tags "database sql"
        }

        mongodb = softwareSystem "MongoDB" {
            description "Хранит данные о конференциях (conferences) и докладах (reviews)"
            tags "database nosql"
        }

         redis = softwareSystem "Redis" {
            description "Кеширующий сервер для User Service"
            tags "cache"
        }

        API = softwareSystem "API Gateway" {
            description "Общий вход для всех сервисов"
            tags "api-gateway"
        }

        wrk = softwareSystem "wrk" {
            description "Инструмент нагрузочного тестирования"
            tags "testing"
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
            user_service -> redis "GET/SET (Cache-Aside)"
            review_service -> mongodb "MongoDB - коллекция reviews"
            conference_service -> mongodb "MongoDB - коллекция conferences"
            
            review_service -> conference_service "REST: Добавление докладов в конференцию"
            user_service -> review_service "JWT валидация"
        }

        user -> API "HTTP Запросы"
        admin -> API "HTTP Запросы"
        API -> conference_site "Запросы на сайте"

        tester -> wrk "Запуск тестов"
        wrk -> conference_site.user_service "HTTP Запросы /users/withcache/"
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

        dynamic conference_site "User_Registration_With_Cache" "Регистрация с кешированием" {
            autolayout lr
            description "Регистрация нового пользователя с кешированием (PostgreSQL + Redis)"

            user -> API "HTTP POST /users/"
            API -> conference_site.user_service "REST API"
            conference_site.user_service -> postgres_db "INSERT INTO users"
            conference_site.user_service -> redis "SET user:{id}"
        }

        dynamic conference_site "Performance_Testing" "Тестирование производительности" {
            autolayout lr
            description "Нагрузочное тестирование с wrk"

            tester -> wrk "Запуск wrk"
            wrk -> conference_site.user_service "HTTP GET /users/withcache/{id}"
            conference_site.user_service -> redis "GET user:{id} [Cache Hit]"
            conference_site.user_service -> postgres_db "SELECT [Cache Miss]"
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
            
            conference_site.user_service -> postgres_db "Docker volume (postgres_data) 5432/tcp"
            conference_site.user_service -> redis "6379/tcp"
            conference_site.conference_service -> mongodb "Docker volume (mongo_data)"
            conference_site.review_service -> mongodb "Docker volume (mongo_data)"
            wrk -> conference_site.user_service "8000/tcp"
            
            API -> conference_site.user_service "Порт :8000"
            API -> conference_site.review_service "Порт :8001"
            API -> conference_site.conference_service "Порт :8002"
        }
    }
}