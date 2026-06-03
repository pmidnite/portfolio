# Developer Guide & Setup Instructions

Welcome to the **Developer Guide** for the Portfolio Flask Application. This document provides step-by-step instructions on setting up the website from scratch, configuring the environment, performing migrations, and seeding content via the Admin Control Panel.

- **Live URL:** [https://sarfarazn.pythonanywhere.com](https://sarfarazn.pythonanywhere.com)
- **LinkedIn:** [https://in.linkedin.com/in/snawaz11](https://in.linkedin.com/in/snawaz11)

---

## 🛠️ Tech Stack & Requirements

- **Backend:** Flask (Python 3.10+)
- **Database:** MySQL / MariaDB (SQLAlchemy ORM with Flask-Migrate)
- **Authentication:** Flask-JWT-Extended
- **Email Service:** Flask-Mail (TLS configured)
- **Frontend:** HTML5, Vanilla CSS, Bootstrap 5 (Icons included)
- **Security:** Rate limiting with Flask-Limiter, HTML escaping/sanitization to prevent XSS.

---

## 🚀 Step-by-Step Local Setup

Follow these commands to get the application running locally on your machine.

### 1. Set Up Environment Variables
Copy the template configuration file to create your local `.env`:
```bash
cp portfolio/.env.example portfolio/.env
```
Open `portfolio/.env` and update the parameters (see the Configuration section below for details).

### 2. Configure a Virtual Environment
Create and activate a Python virtual environment:
```bash
# Navigate to the portfolio folder
cd portfolio/

# Create a virtual environment
python3 -m venv .venvsql

# Activate the virtual environment
source .venvsql/bin/activate
```

### 3. Install Dependencies
Install all required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Database Setup & Migrations
1. Create a MySQL database (e.g., named `portfolio`).
2. Run the database migration commands to generate the database schema automatically:

```bash
# Generate the migration script based on models
flask --app wsgi:app db migrate -m "Initial schema setup"

# Apply migrations to your database
flask --app wsgi:app db upgrade
```

### 5. Launch the Development Server
Run the Flask application:
```bash
FLASK_DEBUG=true flask --app wsgi:app run --port 5001
```
Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

---

## ⚙️ Configuration (.env)

Ensure your `.env` contains the correct variables:
- **`SECRET_KEY` & `JWT_SECRET_KEY`**: Used to sign cookies/sessions and JWT admin authorization tokens.
- **`API_USERNAME` & `API_PASSWORD`**: Credentials used to log in to `/admin` dashboard.
- **`DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME`**: MySQL connection credentials.
  *Note: If your database name has a `$` symbol (like on PythonAnywhere), wrap it in single quotes in `.env`:*
  `DB_NAME='sarfarazn$portfolio'`
- **`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_RECIPIENT`**: Used by the contact form to dispatch email notifications.

---

## 🔑 Admin Panel & Data Guide

The administration interface is located at `/admin`. Log in using the `API_USERNAME` and `API_PASSWORD` defined in your `.env`.

To populate the portfolio with content, insert/configure data under these sections:

### 1. About / Profile Settings
This section contains your primary bio, tags, CV download link, and social profiles.
- **Required Data:**
  - **Email:** Must match the owner/developer email (e.g., used to link experience/education).
  - **Title / Role:** E.g., *"Full Stack Developer"*.
  - **Description:** A short biography detailing your expertise.
  - **Resume / CV Link:** A URL to your uploaded resume (can be stored under `/static/uploads/resume.pdf` or a Google Drive link).
  - **Social Links:** LinkedIn, GitHub, and Twitter profile URLs.
  - **Profile Picture URL:** Image showing your avatar on the main page.

### 2. Experiences
Lists your professional work history.
- **Required Data:**
  - **Company:** Name of the employer.
  - **Designation:** Your job title.
  - **Description:** Bullet points or text detailing your accomplishments.
  - **Start & End Years:** Format as YYYY (e.g., `2024` or `Present`).
  - **Email:** The profile owner's email.

### 3. Education
Lists your academic background.
- **Required Data:**
  - **Institution:** School, College, or University name.
  - **Degree:** Degree/Certificate title.
  - **Description:** Optional course details or honors.
  - **Start & End Years:** Format as YYYY.
  - **Email:** The profile owner's email.

### 4. Skills
Displays your technical skillset.
- **Required Data:**
  - **Skill Name:** E.g., *"Python"*, *"Flask"*, *"MySQL"*.
  - **Proficiency:** Level or percentage score (e.g., `90` for 90%).
  - **Icon Class:** Bootstrap Icon classes (e.g., `bi-code-slash`, `bi-database`, `bi-cpu`).

### 5. Certifications
- **Required Data:**
  - **Cert Name:** Title of the certification.
  - **Issuer:** E.g., *"Google"*, *"AWS"*, *"Cisco"*.
  - **Date:** Date of issuance.
  - **Credential Link:** URL to verify the certificate online.

### 6. Testimonials
Reviews or recommendations from clients or colleagues.
- **Required Data:**
  - **Name:** Reviewer's name.
  - **Designation:** E.g., *"Project Manager at Acme Corp"*.
  - **Message:** The text of their recommendation.
  - **Avatar URL:** Headshot picture of the client.

---

## 🖼️ Media & Asset Guidelines

To keep the UI looking modern and polished:

| Asset Type | Recommended Resolution | Storage Location | Example Format |
| :--- | :--- | :--- | :--- |
| **Profile Pic** | `400 x 400 px` (Square/Ratio 1:1) | `/app/static/images/profile.jpg` | `.jpg`, `.png`, `.webp` |
| **Testimonial Avatars** | `150 x 150 px` (Square/Ratio 1:1) | `/app/static/images/testimonials/` | `.jpg`, `.png` |
| **Resume / CV** | N/A | `/app/static/uploads/resume.pdf` | `.pdf` |
| **Icons** | SVG / Font Icons | Bootstrap Icons Library | `bi-code-slash`, `bi-heart` |

> [!TIP]
> You can place custom static assets inside the `portfolio/app/static/` directory (e.g., under `images/` or `uploads/`) and reference them in the admin dashboard as `/static/images/filename.ext`.
