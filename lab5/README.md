# Дисциплина Программная инженерия
Задания выполнял студент группы М8О-114СВ-24 Красавин М.А.
# ДЗ №5 (Вариант 3)
## Цели и задачи
1. Для данных, хранящихся в реляционной базе PotgreSQL реализуйте шаблон сквозное чтение и сквозная запись (Пользователь/Клиент …)
2. В качестве кеша – используйте Redis
3. Замерьте производительность запросов на чтение данных с и без кеша с использованием утилиты wrk https://github.com/wg/wrk изменяя количество потоков из которых производятся запросы (1, 5, 10)
4. Актуализируйте модель архитектуры в Structurizr DSL
5. Ваши сервисы должны запускаться через docker-compose командой dockercompose up (создайте Docker файлы для каждого сервиса)

## Результаты работы
Три сервиса:
* [Сервис авторизации пользователей](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab5/user_service) (FastAPI + PostgreSQL + Redis): http://localhost:8000/docs - веб-интерфейс для сервиса авторизации через Swagger UI FastAPI
* [Сервис докладов](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab5/review_service) (FastAPI + MongoDB): http://localhost:8001/
* [Сервис конференций](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab5/conference_service) (FastAPI + MongoDB): http://localhost:8002/

Мастер-пользователь:
* Логин: `admin`
* Пароль: `secret`

Базы данных:
| СУБД | Данные | Инициализация |
|------|--------|---------------|
| PostgreSQL | Таблица `users` | [init_db.py](user_service/init_db.py) |
| MongoDB | Коллекции `reviews`, `conferences` | [mongodb.py](review_service/mongodb.py) |
| Redis | Кеш пользователей | Автоматическая инициализация |

Прочее:

* [updated_workspace.dsl](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab5/updated_workspace.dsl) - обновленная архитектура из первого задания
* [docker-compose.yml](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab5/docker-compose.yml) - YAML-файл для управления мультиконтейнерными Docker-приложениями
* [openapi.yaml](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab5/openapi.yaml) - спецификация в формате YAML, описывающая API сервиса согласно стандарту OpenAPI

## Тестирование производительности

1. Эндпоинты для теста:
   - Без кеша: `/users/nocache/{id}`
   - С кешем: `/users/withcache/{id}`

2. Команды для теста:
Тест с 1 потоком:

`wrk -t1 -c100 -d10s http://localhost:8000/users/withcache/1`

Тест с 5 потоками:

`wrk -t5 -c500 -d30s http://localhost:8000/users/withcache/1`

3. Результаты:
| Потоки | RPS (без кеша) | RPS (с кешем) |
|--------|----------------|---------------|
| 1 | 509 | 774 |
| 2 | 535 | 766 |
| 3 | 528 | 784 |