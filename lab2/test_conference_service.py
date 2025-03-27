import requests
import json

url = "http://localhost:8002/conferences/"
headers = {
    "Authorization": "Bearer ",  # Укажите действительный токен после Bearer
    "Content-Type": "application/json"
}
data = {
    "title": "Title",
    "description": "Description",
    "start_date": "2025-01-01",
    "end_date": "2025-01-02"
}

response = requests.post(
    url,
    data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
    headers=headers
)

if response.status_code == 200:
    print("Успешный запрос:", response.json())
elif response.status_code == 401:
    print("Ошибка аутентификации: Проверьте токен")
else:
    print(f"Ошибка {response.status_code}: {response.text}")