workspace {
    !identifiers hierarchical
    model {
        admin = Person "Администратор" "Управляет данными с сервисов и пользователями"
        user = Person "Участник" "Принимает участие в конференции"

        data_base = softwareSystem "База данных" {
            description "Хранит данные о пользователях, докладах и конференциях"
        }

        API = softwareSystem "API Getaway" {
            description "Обрабатывает запросы от пользователей"
        }

        conference_site = softwareSystem "Сайт конференции" {
            description "Служит для управления пользователями, докладами и конференциями"

            user_service = container "Пользовательский сервис" {
                description "Управляет пользователями"
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

            API -> user_service "REST API"
            API -> review_service "REST API"
            user_service -> data_base "Сохранение данных о пользователях"
            review_service -> conference_service "REST API: Добавление докладов в конференцию"
            review_service -> data_base "Сохранение доклада"
            conference_service -> data_base "Сохранение данных о конференции"
        }

        user -> API "HTTP: Запрос на доступ пользователя к конференции"
        API -> conference_site "HTTP: Обработка запросов"
        admin -> API "HTTP: Запрос на добавление доклада или пользователя"

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

        dynamic conference_site "Add_participant" "Добавление пользователя" {
            autolayout lr
            description "Сценарий добавления нового пользователя"
            admin -> API "HTTP POST /users/"
            API -> conference_site.user_service "REST API"
            conference_site.user_service -> data_base "Сохранить данные"
        }

        dynamic conference_site "Find_user_login" "Поиск пользователя по логину" {
            autolayout lr
            description "Сценарий поиска пользователя по логину"
            admin -> API "HTTP GET /users/search/username/{username}"
            API -> conference_site.user_service "REST API"
            conference_site.user_service -> data_base "Поиск пользователя"
        }

        dynamic conference_site "Find_user_mask" "Поиск пользователя по маске имени и фамилии" {
            autolayout lr
            description "Сценарий поиска пользователя по маске имени и фамилии"
            admin -> API "HTTP GET /users/search/name/{name_part}"
            API -> conference_site.user_service "REST API"
            conference_site.user_service -> data_base "Поиск пользователей"
        }

        dynamic conference_site "Add_review" "Добавление доклада" {
            autoLayout lr
            description "Сценарий добавления доклада в конференцию"
            admin -> API "HTTP POST /reviews/"
            API -> conference_site.review_service "REST API"
            conference_site.review_service -> conference_site.conference_service "REST API"
            conference_site.conference_service -> data_base "Сохранить данные"
        }

        dynamic conference_site "Create_review" "Создание доклада" {
            autoLayout lr
            description "Сценарий создания доклада"
            admin -> API "HTTP POST /reviews/"
            API -> conference_site.review_service "REST API"
            conference_site.review_service -> data_base "Сохранить данные"
        }

        dynamic conference_site "extract_list_of_reviews" "Получение списка всех докладов" {
            autolayout lr
            description "Сценарий получения списка всех докладов"
            user -> API "HTTP GET /reviews/"
            API -> conference_site.review_service "REST API"
            conference_site.review_service -> data_base "Получить доклады"
        }

        dynamic conference_site "extract_list_of_conference_reviews" "Получение списка докладов с конференции" {
            autolayout lr
            description "Сценарий получения списка докладов с конференции"
            user -> API "HTTP GET /reviews/?conference_id={id}"
            API -> conference_site.review_service "REST API"
            conference_site.review_service -> data_base "Получить доклады"
        }
    }
}