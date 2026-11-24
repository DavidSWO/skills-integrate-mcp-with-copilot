# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- View current participants without signing in
- Let authenticated teachers sign up or unregister students

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/auth/login`                                                     | Sign in as a teacher; sets an HTTP-only session cookie               |
| GET    | `/auth/me`                                                        | Return the current teacher sign-in status                            |
| POST   | `/auth/logout`                                                    | Clear the teacher session cookie                                     |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Teacher-only student signup                                          |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Teacher-only unregister                                         |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Activity registrations are stored in memory and reset when the server restarts. Teacher credentials are stored separately in the JSON file described below.

## Teacher access

Create or update a teacher account with:

```sh
python src/create_teacher.py teacher@mergington.edu
```

The command prompts for a password and stores a salted PBKDF2 hash in
`~/.config/mergington/teachers.json` with owner-only file permissions. Set
`TEACHER_CREDENTIALS_FILE` to use another path. Passwords are never stored in
plain text. The application reads this JSON file to authenticate teachers;
there is no public account-management page.

Set `SESSION_SECRET` to a long random value in deployments. Without it, a
temporary random key is generated at startup and existing sessions will expire
when the server restarts. Set `COOKIE_SECURE=true` when serving over HTTPS; it
is disabled by default for local HTTP development. Teacher sessions expire
after eight hours. Activity listings remain public, but signup and unregister
requests require a valid teacher session.
