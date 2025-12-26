FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Run Streamlit
CMD ["streamlit", "run", "family_expense_tracker.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.headless=true"]
