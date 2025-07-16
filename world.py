from flask import Flask, request

import sqlite3
 
app = Flask(__name__)
 
def get_db_connection():

    conn = sqlite3.connect('sql_inject.db')  # SQLite database

    conn.row_factory = sqlite3.Row

    return conn
 
@app.route('/userCheck', methods=['GET', 'POST'])

def user_check():

    user = request.args.get('user', '')  # Get 'user' parameter from request
 
    conn = get_db_connection()

    cursor = conn.cursor()
 
    query = f"SELECT * FROM User WHERE userid='{user}'"

    print(f"Executing query: {query}")  # Debug output
 
    try:

        cursor.execute(query)

        results = cursor.fetchall()
 
        response = "<h1>SQL Injection Example</h1><br/><br/>"

        response += f"Query: {query}<br/><br/>Results:<br/>"

        for row in results:

            response += f"{row['userid']}<br/>"
 
    except Exception as e:

        response = f"Error: {str(e)}"
 
    finally:

        conn.close()
 
    return response
 
if __name__ == '__main__':

    app.run(debug=True)  # Run Flask server
 
