# 🚀 Snippet Vault: iOS26 Edition

A high-end, developer-centric code snippet manager featuring a native-OS aesthetic.

## 🎨 Design System (iOS26 Aesthetic)
- **Visual Style:** Ultra-minimalist "Glassmorphism."
- **3D Engine (Three.js):** - A background `canvas` renders a slow-moving, interactive **3D Mesh Gradient**.
  - **Interaction:** The gradient colors shift slightly based on mouse position (parallax).
  - **System Aware:** The Three.js scene swaps material colors (Light Frost vs. Deep Midnight) based on the user's system dark/light mode.
- **Surface:** `.glass-container` cards with `backdrop-filter: blur(25px);`.

## 🛠 Tech Stack
- **Backend:** Python / Flask
- **Auth:** Flask-Login + Werkzeug Hashing.
- **Database:** SQLite (Dev) / Neon PostgreSQL (Prod).
- **Frontend:** Jinja2, **Three.js** (Background Engine), Prism.js (Syntax).

## 🏗 Data Models & Privacy Logic
- **User:**
  - `username`: Unique identifier for profile URLs (`/user/<username>`).
  - `snippets`: Relationship to Snippet model.
- **Snippet:**
  - `is_public`: Boolean (Default: `False`).
  - `user_id`: Foreign Key linking to owner.

## 🔐 Privacy & Visibility Rules
1. **Private Snippets:** Visible only to the owner.
2. **Public Snippets:** Visible to anyone at `/user/<username>`.
3. **Owner View:** The owner sees all snippets on their own profile, with "Private" or "Public" status badges.

## 🤖 AI Programming Guidelines
1. **Three.js Integration:** Initialize the Three.js scene in `static/js/background.js`. Ensure it is responsive and uses `requestAnimationFrame` for smooth 60fps movement.
2. **Dynamic Routing:** Use `@app.route('/user/<username>')` to fetch profiles.
3. **Filtering:** Use `.filter_by(is_public=True)` for non-owner visitors.
4. **Performance:** Ensure the Three.js canvas has a `z-index: -1` so it doesn't interfere with clicks on snippets.
