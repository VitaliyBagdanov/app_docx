import os
import time
import subprocess
import requests
import tempfile
import pytest
import sys
import psycopg2
from dotenv import load_dotenv
from docx import Document

API_URL = "http://localhost:8000/v2/generate-docx"
TEMP_DIR = tempfile.gettempdir()
TEST_ID = 1  # валидный id для успешного теста

def wait_for_server(url, timeout=15):
    """
    Ждёт, пока сервер не начнёт отвечать на HTTP-запросы.
    Теперь дополнительно логирует ошибки соединения.
    """
    start = time.time()
    last_exception = None
    while time.time() - start < timeout:
        try:
            r = requests.post(url, json={"id": TEST_ID}, timeout=1)
            if r.status_code in {200,400,404,422}:
                return True
        except Exception as e:
            last_exception = e
        time.sleep(0.5)
    print("Последняя ошибка подключения:", last_exception)
    raise RuntimeError("Uvicorn не стартовал за отведенное время.")

@pytest.fixture(scope="module")
def run_uvicorn():
    """
    Запускает uvicorn сервер для тестов на время модуля.
    Теперь порт выбирается динамически, чтобы исключить конфликт.
    """
    import socket
    s = socket.socket()
    s.bind(('', 0))
    free_port = s.getsockname()[1]
    s.close()
    api_url = f"http://localhost:{free_port}/v2/generate-docx"
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", f"{free_port}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        wait_for_server(api_url)
        yield api_url
    finally:
        proc.terminate()
        proc.wait(timeout=10)
        out, err = proc.communicate(timeout=5)

def cleanup_generated_file(filename_or_path):
    file_path = filename_or_path if os.path.isabs(filename_or_path) else os.path.join(TEMP_DIR, filename_or_path)
    if os.path.exists(file_path):
        os.remove(file_path)

@pytest.mark.parametrize(
    "test_id,expected_values,expect_success",
    [
        (1, ["Юлия, Тилл, Патрик, Саня", "Раз, два, три, четыре, пять"], True),         # успешный кейс
        (99999, [], False),  # несуществующий id, должен быть 404/400
    ]
)
def test_generate_docx_various(run_uvicorn, test_id, expected_values, expect_success):
    """
    Универсальный тест для успешного и неуспешного генерации docx.
    Теперь покрывает: кейсы 200, 404, 400; парсит docx и проверяет конкретные значения;
    логирует проблему при невалидном ответе.
    """
    api_url = run_uvicorn
    data = {"id": test_id}
    r = requests.post(api_url, json=data)
    if expect_success:
        assert r.status_code == 200, f"Ответ не 200 OK: {r.status_code}, тело: {r.content[:300]}"
        ct = r.headers.get("content-type", "")
        assert (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in ct
            or "application/octet-stream" in ct
        ), f"Неверный Content-Type: {ct}"
        # Сохраняем файл
        out_path = os.path.join(TEMP_DIR, f"test_result_{test_id}.docx")
        with open(out_path, 'wb') as f:
            f.write(r.content)
        # анализируем содержимое docx
        doc = Document(out_path)
        text = "\n".join([p.text for p in doc.paragraphs])
        for val in expected_values:
            assert val in text, f"'{val}' не найден(а) в сгенерированном docx!"
        cleanup_generated_file(out_path)
    else:
        assert r.status_code in {400, 404}, f"Ожидался 400 или 404, получено: {r.status_code}"

def test_invalid_json(run_uvicorn):
    """
    Проверяем обработку некорректного тела запроса (например, невалидный JSON).
    """
    api_url = run_uvicorn
    r = requests.post(api_url, data="not-a-json")
    assert r.status_code in (400, 422), f"Сервер не отдал ошибку на невалидный JSON! ({r.status_code})"

def test_missing_id_key(run_uvicorn):
    """
    Проверка реакции на отсутсвие ключа 'id' в запросе.
    """
    api_url = run_uvicorn
    r = requests.post(api_url, json={})
    assert r.status_code in (400, 422), f"Сервер должен вернуть ошибку при отсутствии id! ({r.status_code})"


def test_db_connects():
    conn = None
    try:
        # Ensure all environment variables are loaded
        load_dotenv()

        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT", 5432), # Default to 5432 if not set
        )
        # Execute a simple query to confirm connection
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            assert cur.fetchone()[0] == 1
    finally:
        if conn:
            conn.close()