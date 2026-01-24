FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# 修改這裡：gunicorn 尋找的是 main.py 檔案裡的 app 物件
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]