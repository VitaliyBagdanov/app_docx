# 📄 FastAPI Docx Template Service

**Микросервис для автоматической генерации docx-файлов по шаблону и данным из PostgreSQL.  
Работает в Docker, собирается через CI/CD, масштабируем для расширения.**

---

## 🚀 Возможности

- Генерирует docx-документы на основе шаблона (`template.docx`) из volume.
- Получает данные (`secretary`, `body`) из PostgreSQL по ID.
- Сохраняет сгенерированные файлы в volume (`shared_data`).
- REST API с валидируемым POST-эндпоинтом.
- Полная интеграция в docker-compose стек (Postgres, n8n, nginx и т.д.).

---

## 📦 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/XXXX
cd fastapi-docx-service
```

### 2. Подготовка `.env`

Создайте `.env` в корне:


### 3. Файл шаблона

Положите ваш `template.docx` в папку `shared_data/` (или убедитесь, что она смонтирована).

### 4. Запуск через Docker Compose

```bash
docker-compose up --build -d
```

### 5. Проверка работы

#### Быстрый тест

```bash
curl -X POST http://localhost:8000/generate-docx \
  -H "Content-Type: application/json" \
  -d '{"id": "math-001"}'
```

Ответ:

```json
{
  "status": "success",
  "filename": "math-001_output.docx",
  "detail": "File generated and saved in shared_data."
}
```

---

## 🔗 Эндпоинты

### POST `/generate-docx`

**Запрос:**
```json
{
  "id": "math-001"
}
```
**Ответ при успехе:**
```json
{
  "status": "success",
  "filename": "math-001_output.docx",
  "detail": "File generated and saved in shared_data."
}
```
**Возможные ошибки:**

- `404`: Документ с таким id не найден
- `500`: Нет шаблона или ошибка генерации файла

---

## 🗃️ Структура БД

```sql
CREATE TABLE documents (
    id VARCHAR PRIMARY KEY,
    secretary VARCHAR,
    body TEXT
);
-- Пример:
INSERT INTO documents (id, secretary, body) VALUES
('math-001', 'Иванов И.И.', 'Уважаемые коллеги! ...');
```

---

## 🎛️ Архитектура Docker Compose

- **fastapi-docx-service:** FastAPI сервис (current repo)
- **db:** PostgreSQL сервис
- **shared_data:** смонтирован между сервисами volume для docx файлов/шаблонов
- **n8n, nginx:** могут быть добавлены по необходимости (см. docker-compose.yml)

---

## ⚙️ Как добавить новый шаблон/метку?

1. Добавьте новый плейсхолдер (`{field}`) в шаблон.
2. Создайте столбец в базе данных, передавайте его в эндпоинт и обрабатывайте в коде.
3. Обновите docx_handler.py — обеспечить замену новых полей.

---

## 📝 Расширение и масштабирование

- Можно добавить другие шаблоны и несколько эндпоинтов.
- Проект легко переносится под k8s или clustered-решения.
- Структура модулярна (легко расширять API, добавлять бизнес-логику).

---

## 📚 Для разработчиков

- Все ключевые параметры хранятся в `.env`
- Используйте `docker-compose logs fastapi-app` для диагностики
- Для локальной работы рекомендуем `python3 -m venv venv; source venv/bin/activate; pip install -r requirements.txt`
- Для деплоя обновляйте контейнер так:
    ```bash
    git pull
    docker-compose build fastapi-app
    docker-compose up -d
    ```

---

## 🗂️ Cтруктура проекта

```
app/
  ├── main.py
  ├── db.py
  ├── schemas.py
  ├── docx_handler.py
  ├── config.py
shared_data/
  ├── template.docx
requirements.txt
docker-compose.yml
README.md
```

---

## ❓ FAQ / troubleshoot

- **Нет файла:** Проверьте, что `template.docx` лежит в `shared_data/`
- **Ошибка подключения к БД:** Убедитесь, что POSTGRES_HOST совпадает с именем службы в docker-compose
- **Недостаточно данных:** Проверьте таблицу и сам запрос

---

## 🏗️ Контакты и поддержка

Для фич-реквестов/багов оставляйте issues на [GitHub](https://github.com/yourorg/fastapi-docx-service/issues).

