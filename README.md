# EquipTrack

EquipTrack is a web-based Equipment Inventory and Tracking System developed using Django and Supabase PostgreSQL. The system is designed to help organizations efficiently manage equipment records, monitor inventory status, and track borrowing and returning transactions through a secure and user-friendly interface.

## Features

### Current Features
- User Registration
- User Login and Logout
- Custom Admin Dashboard
- Secure Authentication
- PostgreSQL Database Integration (Supabase)
- Responsive User Interface

### Planned Features
- Equipment Management (CRUD)
- Category Management
- Borrow Equipment
- Return Equipment
- Equipment Availability Tracking
- Dashboard Analytics
- Search and Filter Equipment
- User Profile Management
- Activity Logs
- Reports Generation

---

## Technology Stack

### Backend
- Python 3.12
- Django 5.x

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Database
- Supabase PostgreSQL

### Version Control
- Git
- GitHub

---

## Project Structure

```text
equiptrack/
│
├── accounts/
├── dashboard/
├── equiptrack/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── registration/
│   └── dashboard/
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/elyszely21/EquipTrack.git
```

Navigate to the project folder:

```bash
cd EquipTrack
```

---

## Create a Virtual Environment

Windows

```bash
python -m venv .venv
```

Activate the virtual environment:

PowerShell

```bash
.venv\Scripts\Activate.ps1
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=your_supabase_session_pooler_connection_string
```

> **Note:** Never commit your `.env` file to GitHub.

---

## Apply Database Migrations

```bash
python manage.py migrate
```

---

## Create a Superuser

```bash
python manage.py createsuperuser
```

---

## Run the Development Server

```bash
python manage.py runserver
```

Open your browser:

```
http://127.0.0.1:8000/
```

---

## GitHub Repository

Repository:

https://github.com/elyszely21/EquipTrack

---

## Project Status

🚧 This project is currently under active development as part of the Systems Integration and Architecture course. Additional features and improvements will be implemented throughout the development lifecycle.

---

## Developer

**Eleazar Labitad Mabini Jr.**

Bachelor of Science in Information Technology

Cebu Institute of Technology – University

---

## License

This project is developed for educational purposes only.
