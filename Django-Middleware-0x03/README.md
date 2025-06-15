# Django Middleware Project

This project is a Django-based messaging application that demonstrates the implementation of middleware in Django.

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- On Windows:
```bash
.\venv\Scripts\activate
```
- On Unix or MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Project Structure

- `messaging_app/`: Main Django project directory
- `chats/`: Django app containing the messaging functionality
- `requirements.txt`: Project dependencies
- `manage.py`: Django's command-line utility for administrative tasks

## API Documentation

The API documentation and Postman collection are available in the `postman_collection.json` file. 