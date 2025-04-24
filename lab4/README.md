# Дисциплина Программная инженерия
Задания выполнял студент группы М8О-114СВ-24 Красавин М.А.
# ДЗ №4 (Вариант 3)
## Цели и задачи
1. Для одного сервиса управления данными (созданного в предыдущих лабораторных работах) создайте долговременное хранилище данных в noSQL базе данных MongoDB (4.0 или 5.0)
2. Выберете любой сервис, не связанный с клиентскими данными (клиентский сервис остается в PostgreSQL). Например, данные о поездках, данные о планах, данные о сообщениях …
3. Должен быть создан скрипт по наполнению СУБД тестовыми значениями. Он должен запускаться при первом запуске вашего сервиса
4. Для сущности, должны быть созданы запросы к БД (CRUD) согласно ранее разработанной архитектуре
5. Должны быть созданы индексы, ускоряющие запросы
6. Должно применяться индексирования по полям, по которым будет производиться поиск
7. При необходимости актуализируйте модель архитектуры в Structurizr DSL
8. Ваши сервисы должны запускаться через docker-compose командой dockercompose up (создайте Docker файлы для каждого сервиса)

## Результаты работы
Три сервиса:
* [Сервис авторизации пользователей](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab4/user_service): http://localhost:8000/docs - веб-интерфейс для сервиса авторизации через Swagger UI FastAPI
* [Сервис докладов](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab4/review_service): http://localhost:8001/
* [Сервис конференций](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab4/conference_service): http://localhost:8002/

Мастер-пользователь:
* Логин: `admin`
* Пароль: `secret`

СУБД PostgreSQL 15.12 в Docker-контейнере, в которой была созданы таблицы:
* `users`

СУБД MongoDB 5.0 в Docker-контейнере, в которой были созданы коллекции:
* `reviews`
* `conferences`

Для инициализации БД PostgreSQL создан скрипт [init_db.py](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab3/user_service/init_db.py), который создает таблицы с индексами и наполняет их тестовыми данными

Для инициализации БД MongoDB создано два скрипта `mongodb.py` соответственно находящиеся в [сервисе докладов](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab4/review_service) и [сервисе конференций](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab4/conference_service), создающие две коллекции в одной базе данных, наполняет их тестовыми данными, также создаются индексы для ускорения поиска

Прочее:

* [updated_workspace.dsl](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab4/updated_workspace.dsl) - обновленная архитектура из первого задания
* [docker-compose.yml](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab4/docker-compose.yml) - YAML-файл для управления мультиконтейнерными Docker-приложениями
* [openapi.yaml](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab4/openapi.yaml) - спецификация в формате YAML, описывающая API сервиса согласно стандарту OpenAPI

## Тестирование
1. Выполнить команду в cmd: `docker-compose up --build`

Примечание: шаги для тестирования веб-сервиса и БД PostgreSQL приведены в [ДЗ №3](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab3)

2. Подключиться к контейнеру с MongoDB: `docker-compose exec mongodb bash`
3. Запустить оболочку MongoDB Shell: `mongosh -u mongo -p 1`
4. В качестве простых тестовых запросов можно выполнить: `show dbs` -> `use conference_db` -> `show collections` -> `db.conferences.find().pretty()` | `db.reviews.find().pretty()`