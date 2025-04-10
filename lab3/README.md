# Дисциплина Программная инженерия
Задания выполнял студент группы М8О-114СВ-24 Красавин М.А.
# ДЗ №3 (Вариант 3)
## Цели и задачи
1. Для сервиса управления данными (созданного в предыдущей лабораторной работе) о клиентах создайте долговременное хранилище данных в реляционной СУБД PostgreSQL 14
2. Должен быть создан скрипт по созданию базы данных и таблиц, а также наполнению СУБД тестовыми значениями. Он должен запускаться при первом запуске вашего сервиса
3. Для сущности, должны быть созданы запросы к БД (CRUD) согласно ранее разработанной архитектуре
4. Данные о пользователе должны включать логин и пароль. Пароль должен храниться в закрытом виде (хэширован) – в этом задании опционально
5. Должно применяться индексирования по полям, по которым будет производиться поиск
6. При необходимости актуализируйте модель архитектуры в Structurizr DSL
7. Ваши сервисы должны запускаться через docker-compose командой dockercompose up (создайте Docker файлы для каждого сервиса)
## Результаты работы
Три сервиса:
* [Сервис авторизации пользователей](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab3/user_service): http://localhost:8000/docs - веб-интерфейс для сервиса авторизации через Swagger UI FastAPI
* [Сервис докладов](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab3/review_service): http://localhost:8001/
* [Сервис конференций](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab3/conference_service): http://localhost:8002/

Мастер-пользователь:
* Логин: `admin`
* Пароль: `secret`

СУБД PostgreSQL 15.12 в Docker-контейнере, в которой были созданы таблицы:
* `users`
* `reviews`
* `conferences`

Для инициализации БД создан скрипт [init_db.py](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab3/user_service/init_db.py), который создает таблицы с индексами и наполняет их тестовыми данными

Прочее:

* [updated_workspace.dsl](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab3/updated_workspace.dsl) - обновленная архитектура из первого задания
* [docker-compose.yml](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab3/docker-compose.yml) - YAML-файл для управления мультиконтейнерными Docker-приложениями
* [openapi.yaml](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab3/openapi.yaml) - спецификация в формате YAML, описывающая API сервиса согласно стандарту OpenAPI

## Тестирование
1. Выполнить команду в cmd: `docker-compose up --build`
2. По ссылке http://localhost:8000/docs авторизоваться под мастер-пользователем (`admin`, `secret`)
3. Получить токен: `curl -X POST http://localhost:8000/token -d "username=admin&password=secret"`
4. В отличие от прошлого задания, теперь мы можем наполнять сервисы данными, и они будут сохраняться в базе данных: `curl -X POST "http://localhost:8002/conferences/" -H "Authorization: Bearer ВСТАВИТЬ_АКТУАЛЬНЫЙ_ТОКЕН" -H "Content-Type: application/json" -d "{\"title\": \"МФТИ IT Purple Conf\", \"description\": \"Для ботанов\", \"start_date\": \"2023-03-15T09:00:00\", \"end_date\": \"2023-03-15T18:00:00\"}"` - эта команда добавляет в таблицу `conferences` данные о конференции
5. Выполнить команду `docker-compose exec postgres psql -U postgres -d conference_db`, чтобы взаимодействовать с базой данных PostgreSQL через терминал
6. В качестве простых тестовых запросов можно выполнить: `SELECT * FROM users; SELECT * FROM conferences; SELECT * FROM reviews;`