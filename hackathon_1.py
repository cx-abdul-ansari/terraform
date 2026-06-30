# hackathon_1.py
# Intent: Looks sanitized, but vulnerable via multi-consumer reuse

from flask import Flask, request, jsonify, render_template_string
import bleach
import json

app = Flask(__name__)

# in-memory "database"
DB = {}

# --- Sanitization (appears secure) ---
def sanitize_input(user_input):
    # Allow basic formatting tags only
    return bleach.clean(user_input, tags=["b", "i", "u"], strip=True)

# --- Store user input ---
@app.route("/save", methods=["POST"])
def save():
    nickname = request.form.get("nickname", "")

    # sanitize before storage
    clean = sanitize_input(nickname)

    DB["user"] = {"nickname": clean}
    return "saved"

# --- API endpoint (shared data model) ---
@app.route("/profile")
def profile():
    user = DB.get("user", {"nickname": ""})

    # returned as JSON
    return jsonify(user)

# --- Frontend A (Jinja template) ---
@app.route("/ui")
def ui():
    user = DB.get("user", {"nickname": ""})

    # looks safe because Jinja auto-escapes,
    # but developer disables it
    template = """
    <html>
      <body>
        <h3>User Profile</h3>
        <div id="name">{{ nickname|safe }}</div>
      </body>
    </html>
    """
    return render_template_string(template, nickname=user["nickname"])

# --- Frontend B (JS consumer) ---
@app.route("/admin")
def admin():
    # Legacy dashboard consuming API
    return """
    <html>
      <body>
        <h3>Admin Panel</h3>
        <div id="name"></div>

        <script>
          fetch('/profile')
            .then(res => res.json())
            .then(data => {
              // direct DOM injection
              document.getElementById("name").innerHTML = data.nickname;
            });
        </script>
      </body>
    </html>
    """

# --- Frontend C (JSON inside script context) ---
@app.route("/widget")
def widget():
    user = DB.get("user", {"nickname": ""})

    # embedded in JS context (different interpretation)
    return f"""
    <html>
      <body>
        <script>
          var user = {json.dumps(user)};
          document.write(user.nickname);
        </script>
      </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)