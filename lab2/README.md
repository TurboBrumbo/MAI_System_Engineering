# Дисциплина Программная инженерия
Задания выполнял студент группы М8О-114СВ-24 Красавин М.А.
# ДЗ №2 (Вариант 3)
## Цели и задачи
1. Создайте HTTP REST API для сервисов, спроектированных в первом задании (по
проектированию). Должно быть реализовано как минимум два сервиса
(управления пользователем, и хотя бы один «бизнес» сервис)
2. Сервис должен поддерживать аутентификацию с использованием JWT-token
(Bearer)
3. Должен быть отдельный endpoint для получения токена по логину/паролю
4. Сервис должен реализовывать как минимум GET/POST методы
5. Данные сервиса должны храниться в памяти (базу данных добавим потом)
6. В целях проверки должен быть заведён мастер-пользователь (имя admin,
пароль secret)
7. Сделайте OpenAPI спецификацию и сохраните ее в корне проекта
8. Актуализируйте модель архитектуры в Structurizr DSL
9. Ваши сервисы должны запускаться через docker-compose коммандой dockercompose up (создайте Docker файлы для каждого сервиса)
## Результаты работы
Три сервиса:
* [Сервис авторизации пользователей](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab2/user_service): http://localhost:8000/docs - веб-интерфейс для сервиса авторизации через Swagger UI FastAPI
* [Сервис докладов](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab2/review_service): http://localhost:8001/
* [Сервис конференций](https://github.com/TurboBrumbo/MAI_System_Engineering/tree/main/lab2/conference_service): http://localhost:8002/

Мастер-пользователь:
* Логин: `admin`
* Пароль: `secret`

Прочее:

* [updated_workspace.dsl](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab2/updated_workspace.dsl) - обновленная архитектура из первого задания
* [docker-compose.yml](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab2/docker-compose.yml) - YAML-файл для управления мультиконтейнерными Docker-приложениями
* [openapi.yaml](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab2/openapi.yaml) - спецификация в формате YAML, описывающая API сервиса согласно стандарту OpenAPI

## Тестирование
1. Выполнить команду в cmd: `docker-compose up --build`
2. По ссылке http://localhost:8000/docs авторизовать под мастер-пользователем (`admin`, `secret`)
3. Получить токен: `curl -X POST http://localhost:8000/token -d "username=admin&password=secret"`
4. Ввести полученный токен в [test_review_service.py](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab2/test_review_service.py) и [test_conference_service.py](https://github.com/TurboBrumbo/MAI_System_Engineering/blob/main/lab2/test_conference_service.py) и посмотреть результат
5. В случае, если был использован актуальный токен авторизованного пользователя, в сервисах будут сохраняться данные о конференциях и докладах, в противном случае - ошибка
