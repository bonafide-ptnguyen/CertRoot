# 1. Use an official lightweight Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy dependencies first (caching optimization)
COPY requirements.txt .

# 4. Install dependencies
# --no-cache-dir keeps the image small
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Expose the port the app runs on (Default FastAPI port is 8000)
EXPOSE 8000

# 7. Command to run the application
# Adjust 'app:app' if your main file is named differently (e.g., main.py)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]