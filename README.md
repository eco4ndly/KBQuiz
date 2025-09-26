# KBC Quiz Master

A colourful, animated web application for hosting KBC-style quiz competitions. Administrators can create multiple quiz competitions, add topics, feed them with four-option questions, and wipe the slate clean when needed. Players can browse competitions, pick a topic, and answer questions one by one with immediate feedback.

## Features

- 💼 **Admin dashboard** with password protection for creating competitions, topics, and questions.
- 🧠 **Multiple competitions and topics** stored in a persistent SQLite database via SQLAlchemy.
- 🗑️ **One-click reset** button to discard all saved competitions, topics, and questions.
- 🎨 **Vibrant animated UI** with glowing cards, smooth hover effects, and responsive design.
- ✅ **Interactive quiz flow** showing one question at a time with selectable options, blue selection state, and green/red feedback after checking the answer.
- 🔁 **Navigation controls** for next/previous questions and an exit button that returns to the topic list.

## Getting Started

1. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```
2. **Configure admin password (optional)**
   ```bash
   export APP_ADMIN_PASSWORD="your-secure-password"
   export APP_SECRET_KEY="random-secret"
   ```
   On Windows PowerShell:
   ```powershell
   setx APP_ADMIN_PASSWORD "your-secure-password"
   setx APP_SECRET_KEY "random-secret"
   ```
3. **Run the application**
   ```bash
   flask --app app run
   ```
   The site will be available at <http://localhost:5000>.

## Usage Tips

- Visit `/admin` to log in and access the dashboard.
- Create a competition, then add topics inside the competition, and finally add questions to each topic.
- Use the **Clear All Data** button on the dashboard to remove every stored competition, topic, and question.
- Players can visit the homepage to choose a competition, pick a topic, and enjoy the quiz experience.

## Project Structure

```
.
├── app.py
├── requirements.txt
├── README.md
├── static/
│   ├── styles.css
│   └── quiz.js
└── templates/
    ├── 404.html
    ├── admin_competition.html
    ├── admin_dashboard.html
    ├── admin_login.html
    ├── admin_topic.html
    ├── base.html
    ├── competitions.html
    ├── quiz.html
    └── topics.html
```

## License

This project is provided as-is for demonstration purposes.
