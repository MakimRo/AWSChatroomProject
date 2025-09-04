from flask import Flask, jsonify, request
import pymysql
import bcrypt

RDS_DB_HOSTNAME= 'mysql'
RDS_DB_USERNAME='username'
RDS_DB_PASSWORD='password'
RDS_DB_NAME='db'
# TODO add any necessary imports here

app = Flask(__name__)   

# TODO add an appropriate Dockerfile and requirements.txt (separate files)

# TODO add any necessary helper functions here
def get_database_connection():
    conn = pymysql.connect(host=RDS_DB_HOSTNAME,
                             user=RDS_DB_USERNAME,
                             password=RDS_DB_PASSWORD,
                             db=RDS_DB_NAME,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    return conn
# TODO add any other necessary API endpoint handlers here

@app.route("/new_profile", methods=["POST"])
def new_profile():
    # Create a new profile based on the parameters passed
    # in the POST body as JSON. There will be three parameters:
    # user_name, password, bio. Each is a string.
    # On error, respond with JSON as follows:
    # {"error": "<Your error message here>"}
    # On success, respond with JSON as follows:
    # {"profile_id": <unique profile identifier here>}
    # where the profile identifier is an integer.
    # You must store the profile info the MySQL database.
    try:
        pagedata = request.get_json()
        username = pagedata.get("user_name")
        password = pagedata.get("password")
        bio = pagedata.get("bio")

        if not username or not password or not bio:
            return jsonify({"error": "All fields required!"}), 400

        hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO profiles (username,password,bio) VALUES (%s, %s, %s)", (username, hashpass, bio))
        conn.commit()
        profile_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({"profile_id": profile_id})

    except pymysql.MySQLError as err:
        return jsonify({"error": f"Database Error: {str(err)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/validate_user", methods = ["POST"])
def validate_user():
    # Determine if the given login credentials are valid.
    # There will be two parameters passed in the POST
    # body as JSON: user_name and password. Each is a string.
    # On failure, respond with JSON as follows:
    # {"profile_id": None}
    # On success, respond with JSON as follows:
    # {"profile_id": <unique profile identifier here>}
    # where the profile identifier is an integer.
    try:
        pagedata = request.get_json()
        username = pagedata.get("user_name")
        password = pagedata.get("password")

        if not username or not password:
            return jsonify({"profile_id": None})
        
        
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM profiles WHERE username = %s", username)
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({"profile_id": user["id"]})
        else:
            return jsonify({"profile_id": None})
        

    except pymysql.MySQLError as err:
        return jsonify({"error": f"Database Error: {str(err)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/get_username/<int:profile_id>', methods=['GET'])
def get_username(profile_id):
    # Respond with the user name of the given profile, 
    # expresesd as an integer identifier, passed
    # as a URI parameter.
    # On failure, respond with JSON as follows:
    # {"message": "<Your error message here>"}
    # On success, respond with JSON as follows:
    # {"username": <the user's username>}
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM profiles where id = %s", profile_id)
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return jsonify({"username": user["username"]})
    else:
        return jsonify({"message": "Error finding user for profile ID"})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
