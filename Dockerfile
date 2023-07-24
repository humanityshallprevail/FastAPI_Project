FROM python:3.11.4


WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Add this line to print out the list of installed packages
RUN pip list

COPY . .

CMD ["uvicorn", "menu:app", "--host", "0.0.0.0", "--port", "8000"]
