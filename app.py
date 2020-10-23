"""
Zak Yeomanson
Applications of Programming Principles
Full Stack App: Python

Date Issued: 6th February 2020
Submission Due Date: 29th May 2020
"""

# Import flask, the main module for our app. This allows us to actually have a backend.
# https://flask.palletsprojects.com/en/1.1.x/
from flask import Flask, jsonify, request, make_response, send_from_directory

# Since we are working with json, the json module comes in handy
# https://docs.python.org/3/library/json.html
from json import dump, load

# This is useful to check if the FILEPATH constant is correct
# https://docs.python.org/3/library/os.html
from os import path

# This module is quite neat, in that it includes all HTTP status responses as named variables. It is an enumerated type
# e.g, HTTPStatus.OK.value is 200.
# https://docs.python.org/3/library/http.html
from http import HTTPStatus

# Using this just for pagination in my app
# https://docs.python.org/3/library/math.html
from math import ceil


# Create the app
app = Flask(__name__)

# This is the FILEPATH constant. This should be the location of where the JSON data is kept
dirname = path.dirname(__file__)
FILEPATH = path.join(dirname, r"static\json\data.json")


@app.route('/')
def main_page():
    """When the root is loaded, returns the users.html file"""

    return app.send_static_file("users.html")


@app.route("/css/<file>")
def send_css(file):
    """Adds our CSS to the page"""

    return app.send_static_file("css/" + file)


@app.route("/js/<file>")
def send_js(file):
    """Adds our JS to the page"""
    return app.send_static_file("js/" + file)


@app.route('/favicon-16x16.png')
def favicon():
    """Adds a favicon to our web app
    https://flask.palletsprojects.com/en/1.1.x/patterns/favicon/
    """
    return send_from_directory(path.join(app.root_path, 'static'),
                               'favicon-16x16.png', mimetype='image/vnd.microsoft.icon')


@app.route("/api/users/all", methods=["GET"])
def api_get_all_users():
    """When the url receives a GET request, return the json data

    :return
        jsonData: The json data being used in our app, gotten from the FILEPATH
    """
    json_data = get_json_data(FILEPATH)
    return jsonify(json_data)


@app.route("/api/users/<user_id>", methods=["GET", "PUT"])
def api_single_user(user_id):
    """Calculates what function to call, based on the request method (GET or PUT)

    :return
        response: A response consisting of json data (optional) and the HTTP response, e.g 200 OK
    """
    if request.method == "GET":
        return get_single_user(user_id)
    elif request.method == "PUT":
        return post_single_user(request.json)


def get_single_user(user_id):
    """Attempts to find a user based on the userID given, and returns it in a response format for our app

    :param
        user_id: The ID of the user being found (integer)
    :return
        response: The response of the outcome.
    """

    # First, see if the userID is an integer, or can be cast into one. If not, this cannot work.
    try:
        user_id = int(user_id)
    except ValueError:
        return make_response(jsonify({"ValueError": "{} is not a valid literal.".format(user_id)}),
                             HTTPStatus.BAD_REQUEST)  # 400

    # Then, if it's okay, grab all JSON data
    json_data = get_json_data(FILEPATH)

    # Here we cycle through all users, and see if we can match the ID with any of our data's ID
    for user in json_data:
        if user["id"] == user_id:  # Match found!
            return make_response(jsonify(user), HTTPStatus.OK)  # 200

    # No match found!
    return make_response(jsonify({"IndexError": "User {} not found.".format(user_id)}),
                         HTTPStatus.NOT_FOUND)  # 404


def post_single_user(json_request):
    """Updates a user by modifying the JSON based on the JSON data given

        :param
            json_request: The request data we are given from the PUT request
        :return
            response: The response of the outcome
        """
    response = ""

    # Grab the JSON data
    json_data = get_json_data(FILEPATH)

    # Loop through our json data, and see if we can match our ID given to an ID in our data
    for i in range(0, len(json_data)):
        if str(json_data[i]["id"]) == str(json_request["id"]):  # Found a match!
            # Now we can edit this part of the data and update it
            json_data[i]["email"] = json_request["email"]
            json_data[i]["first_name"] = json_request["first_name"]
            json_data[i]["last_name"] = json_request["last_name"]

            response = make_response(jsonify(), HTTPStatus.CREATED)  # 201

            # Now we write back to the file to save our changes.
            # https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file
            with open(FILEPATH, "w", encoding="utf-8") as f:
                dump(sorted(json_data, key=lambda user: user["id"]), f, ensure_ascii=False, indent=4)

            break  # Break for efficiency purposes; no point in continuing the loop now

    if not response:
        response = make_response(jsonify({"IndexError": "User {} not found.".format(json_request["id"])}),
                                 HTTPStatus.NOT_FOUND)  # 404

    return response


@app.route("/api/users/page/<int:page>", methods=["GET"])
def api_get_page(page):
    """Returns specific JSON data, based on the page, and user's perpage

    :param
        page: The page to load (int)
    :return
        response: The response of the outcome.
    """

    json_data = get_json_data(FILEPATH)

    # Check if the user has supplied the ?perpage= query
    if 'perpage' in request.args:
        per_page = int(request.args['perpage'])  # If they have, change our per_page variable
    else:
        per_page = 6  # default value; arbitrary

    # Calculating some pagination variables
    begin = (page - 1) * per_page
    end = begin + per_page

    if begin >= len(json_data) or page <= 0:  # Invalid page
        return make_response(jsonify({"IndexError": "Page {} not found.".format(page)}),
                             HTTPStatus.NOT_FOUND)  # 404

    page_data = json_data[begin:end]

    return make_response(jsonify({"total_pages": ceil(len(json_data) / per_page), "data": page_data}),
                         HTTPStatus.OK)  # 200


@app.route("/api/users/create", methods=["POST"])
def api_create_user():
    """Creates a user based on the json POSTed and adds it to the JSON file

    :return
        response: The response of the outcome.
    """
    data = request.get_json()
    # Grab the JSON data
    json_data = get_json_data(FILEPATH)
    new_user_id = 1
    while user_id_taken(new_user_id):  # Find the next lowest userID available
        new_user_id += 1

    # Create our new user in JSON format, adding an ID also
    data_to_append = {"id": new_user_id,
                      "email": data["email"],
                      "first_name": data["first_name"],
                      "last_name": data["last_name"],
                      "avatar": data["avatar"]}

    # Append our new user, and save the changes by writing to our JSON file, then make a response
    json_data.append(data_to_append)

    with open(FILEPATH, "w", encoding="utf-8") as f:
        dump(sorted(json_data, key=lambda user: user["id"]), f, ensure_ascii=False, indent=4)

    return make_response(data_to_append, HTTPStatus.CREATED)  # 201


@app.route("/api/users/delete/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    """Deletes a specific user from the JSON file

    :param
        user_id: The userID of the user to be deleted
    :return
        response: The response of the outcome.
    """
    response = ""

    json_data = get_json_data(FILEPATH)

    for index in range(0, len(json_data)):
        if json_data[index]["id"] == user_id:  # User found!

            # Delete and save the changes
            del json_data[index]

            response = make_response(jsonify(), HTTPStatus.NO_CONTENT)  # 204

            with open(FILEPATH, "w", encoding="utf-8") as f:
                dump(sorted(json_data, key=lambda user: user["id"]), f, ensure_ascii=False, indent=4)

            break  # Break for efficiency purposes; no point in continuing the loop now

    if not response:
        response = make_response(jsonify({"IndexError": "User {} not found.".format(user_id)}),
                                 HTTPStatus.NOT_FOUND)  # 404
    return response


def get_json_data(json_path):
    """Simple function to return our data in a json form"""
    with open(json_path) as json_string:
        return load(json_string)


def user_id_taken(user_id):
    """Simple function to check if the userID exists within my data"""
    json_data = get_json_data(FILEPATH)

    for user in json_data:
        if user["id"] == user_id:
            return True

    return False


if __name__ == '__main__':

    # First, check if the FILEPATH exists. This is necessary for my app to work, as it saves all JSON data in this file.
    if not path.exists(FILEPATH):
        raise IOError("No such file or directory {}. Please make one, or set the correct FILEPATH".format(FILEPATH))

    # If it exists, we can run the app
    app.run()
