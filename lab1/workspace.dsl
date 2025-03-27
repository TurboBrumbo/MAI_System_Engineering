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
            }

            review_service = container "Сервис докладов" {
                description "Управляет докладами"
                technology "Python, FastAPI"
            }

            conference_service = container "Сервис конференций" {
                description "Управляет конференциями"
                technology "Python, FastAPI"
            }

            API -> user_service "Передача данных о пользователе"
            API -> review_service "Передача данных о докладах"
            user_service -> data_base "Сохранение данных о пользователях"
            review_service -> conference_service "Добавление докладов в конференцию"
            review_service -> data_base "Сохранение доклада напрямую без привязки к конференции"
            conference_service -> data_base "Сохранение данных о конференции"
        }

        user -> API "Запрос на доступ пользователя к конференции" 
        API -> conference_site "Обработка запросов"
        admin -> API "Запрос на добавление доклада или пользователя" 

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
            admin -> API "Запрос на добавление нового пользователя"
            API -> conference_site.user_service "Передача данных о новом пользователе"
            conference_site.user_service -> data_base "Сохранение данных о новом пользователе в базе данных"
        }

        dynamic conference_site "Find_user_login" "Поиск пользователя по логину" {
            autolayout lr
            description "Сценарий поиска пользователя по логину"
            admin -> API "Запрос на поиск пользователя по логину"
            API -> conference_site.user_service "Передача логина пользователя"
            conference_site.user_service -> data_base "Поиск пользователя с заданным логином в базе данных"
        }

        dynamic conference_site "Find_user_mask" "Поиск пользователя по маске имени и фамилии" {
            autolayout lr
            description "Сценарий поиска пользователя по маске имени и фамилии"
            admin -> API "Запрос на поиск пользователя по маске имени и фамилии"
            API -> conference_site.user_service "Передача имени и фамилии пользователя"
            conference_site.user_service -> data_base "Поиск пользователя с заданными именем и фамилией в базе данных"
        }

        dynamic conference_site "Add_review" "Добавление доклада" {
            autoLayout lr
            description "Сценарий добавления доклада в конференцию"
            admin -> API "Запрос на добавление доклада"
            API -> conference_site.review_service "Передача данных о докладе"
            conference_site.review_service -> conference_site.conference_service "Добавление доклада в конференцию"
            conference_site.conference_service -> data_base "Сохранение данных в базу данных"
        }

        dynamic conference_site "Create_review" "Создание доклада" {
            autoLayout lr
            description "Сценарий создания доклада"
            admin -> API "Запрос на создание доклада"
            API -> conference_site.review_service "Передача данных о докладе"
            conference_site.review_service -> data_base "Добавление доклада в базу данных"
        }

        dynamic conference_site "extract_list_of_reviews" "Получение списка всех докладов" {
            autolayout lr
            description "Сценарий получения списка всех докладов"
            user -> API "Запрос на получение списка докладов"
            API -> conference_site.review_service "Передача запроса на получение списка докладов"
            conference_site.review_service -> data_base "Поиск всех докладов в базе данных"
        }

        dynamic conference_site "extract_list_of_conference_reviews" "Получение списка докладов с конференции" {
            autolayout lr
            description "Сценарий получения списка докладов с конференции"
            user -> API "Запрос на получение списка докладов с конференции"
            API -> conference_site.review_service "Передача запроса на получение списка докладов с конференции"
            conference_site.review_service -> conference_site.conference_service "Поиск докладов в сервисе конференции"
            conference_site.conference_service -> data_base "Поиск в базе данных и получение списка докладов"
        }
    }
}
