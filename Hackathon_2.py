# hackathon_2.py

from flask import Flask, request, jsonify, render_template_string
import bleach
import json
from markupsafe import escape

app = Flask(__name__)

DB = {}

# --- Sanitization (looks strong) ---
def sanitize_input(data):
    return bleach.clean(data, tags=["b", "i"], strip=True)

# --- Non-linear transformation ---
def transform(data):
    # confusing transformation
    return data.replace("{{user}}", data)

# --- Save endpoint ---
@app.route("/save", methods=["POST"])
def save():
    raw = request.form.get("nickname", "")

    # Step 1: sanitize
    clean = sanitize_input(raw)

    # Step 2: misleading "extra safety"
    safe = escape(clean)

    # Step 3: transformation
    final = transform(safe)

    # Step 4: overwrite (subtle bug)
    if request.args.get("debug") == "1":
        final = raw  # bypass everything

    DB["user"] = {"nickname": final}
    return "saved"


# --- API endpoint ---
@app.route("/profile")
def profile():
    user = DB.get("user", {"nickname": ""})
    return jsonify(user)


# --- Frontend A (Jinja, misleading safe usage) ---
@app.route("/ui")
def ui():
    user = DB.get("user", {"nickname": ""})

    template = """
    <html>
      <body>
        <h3>UI View</h3>
        <!-- looks intentional -->
        <div id="name">{{ nickname|safe }}</div>
      </body>
    </html>
    """
    return render_template_string(template, nickname=user["nickname"])


# --- Frontend B (indirect DOM sink) ---
@app.route("/admin")
def admin():
    return """
    <html>
      <body>
        <h3>Admin Panel</h3>
        <div id="root"></div>

        <script>
          fetch('/profile')
            .then(res => res.json())
            .then(data => {
              const container = document.getElementById("root");

              // indirect sink (not obvious innerHTML)
              const tpl = "<section>" + data.nickname + "</section>";
              container.outerHTML = tpl;
            });
        </script>
      </body>
    </html>
    """


# --- Frontend C (JS context confusion) ---
@app.route("/widget")
def widget():
    user = DB.get("user", {"nickname": ""})

    return f"""
    <html>
      <body>
        <h3>Widget</h3>
        <div id="w"></div>

        <script>
          // inserted into JS string context
          var nickname = "{user['nickname']}";

          // later used in HTML context
          document.getElementById("w")
            .insertAdjacentHTML("beforeend", "<p>" + nickname + "</p>");
        </script>
      </body>
    </html>
    """


# --- Hidden alternate flow ---
@app.route("/alt")
def alt():
    user = DB.get("user", {"nickname": ""})

    # double parsing scenario
    return f"""
    <html>
      <body>
        <script>
          let data = JSON.parse('{json.dumps(user)}');
          document.write(data.nickname);
        </script>
      </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)