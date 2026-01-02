# 📸 codeSnap: The iOS26 Snippet Vault

**codeSnap** is a high-fidelity, developer-centric code snippet manager designed with a futuristic "iOS26" aesthetic. It merges ultra-minimalist glassmorphism with an interactive 3D environment to create a workspace that feels native, fluid, and alive.

---

## 🎨 Design System: "iOS26"
codeSnap isn't just a tool; it's a visual experience.
- **Glassmorphism**: The UI is built on `backdrop-filter: blur(25px)`, creating deep, semi-transparent layers that mimic frosted glass.
- **Alive Background**: A custom **Three.js** engine renders a slow-moving, interactive 3D Mesh Gradient that responds to your mouse movement (parallax effect).
- **Adaptive Theming**: The application respects your system's `prefers-color-scheme`.
  - **Dark Mode**: Deep Midnight background with frosted white glass.
  - **Light Mode**: Light Frost background with high-contrast, dark glass elements.
- **Micro-Interactions**: iOS-style toggle switches, hover states, and smooth transitions.

---

## ✨ Key Features

### 🔐 Core Functionality
- **User Authentication**: Secure account creation and login (powered by `Flask-Login` & `Werkzeug`).
- **Snippet Management**: Create, Read, Update, and Delete (CRUD) your code snippets.
- **Syntax Highlighting**: Automatic language detection and highlighting for JavaScript, Python, CSS, HTML, and Markdown (via `Prism.js`).

### 🛡️ Privacy & Sharing
- **Privacy Toggles**: Mark snippets as **Public** (visible to everyone) or **Private** (encrypted for your eyes only).
- **Shareable Links**: Generate direct links to specific snippets with a single click.
- **User Profiles**: Every user gets a dedicated profile (`/user/<username>`) showcasing their public portfolio.

### 🤝 Social & Discovery
- **Voting System**: Upvote or downvote snippets to surface the best code.
- **User Search**: Instantly find other developers via the global search bar.
- **Community Feed**: The "Public Vault" serves as a homepage feed of the latest community contributions.

---

## 🛠 Tech Stack

### Backend
- **Python 3.8+**
- **Flask**: Micro-framework for routing and app logic.
- **Flask-SQLAlchemy**: ORM for database management.
- **Flask-Login**: Session management and authentication.
- **SQLite**: Lightweight, serverless database (Development).

### Frontend
- **Jinja2**: Templating engine.
- **Bootstrap 5**: Responsive layout and component primitives.
- **Three.js**: WebGL engine for the background visualization.
- **Prism.js**: Lightweight, robust syntax highlighter.
- **CSS3 Variables**: For dynamic theming and glassmorphism effects.

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python Package Installer)

### Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/codesnap.git
   cd codesnap
   ```

2. **Create a Virtual Environment (Recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**
   The application will automatically create the `snippets.db` file on the first run, but you can manually initialize it:
   ```bash
   python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. **Run the Application**
   ```bash
   flask run
   ```
   *Alternatively:* `python app.py` (Runs on port 5001)

6. **Access the App**
   Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 📂 Project Structure

```
codesnap/
├── app.py                 # Main application entry point & routes
├── models.py              # Database models (User, Snippet, Vote)
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Global styles, Glassmorphism, Theming
│   └── js/
│       └── background.js  # Three.js 3D Background Engine
└── templates/
    ├── base.html          # Base template with Nav & Scripts
    ├── index.html         # Public Feed
    ├── login.html         # Auth Forms
    ├── profile.html       # User Portfolio
    ├── register.html      # Auth Forms
    ├── snippet_edit.html  # Create/Edit Form
    └── snippet_view.html  # Single Snippet Detail View
```

---

## 🤝 Contributing
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

**codeSnap** — *Snap it. Store it. Share it.*
