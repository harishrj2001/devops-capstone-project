"""
Account Service

This microservice handles the lifecycle of Accounts
"""
from flask import Flask, jsonify, request, make_response, abort, url_for
from service.models import Account
from service.common import status  # HTTP Status Codes

app = Flask(__name__)

HEADER_CONTENT_TYPE = "application/json"

############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return jsonify(
        name="Account REST API Service",
        version="1.0",
        # paths=url_for("list_all_accounts", _external=True)
    ), status.HTTP_200_OK

######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """Creates an Account"""
    check_content_type(HEADER_CONTENT_TYPE)
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    location_url = url_for("read_account", account_id=account.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED, {"Location": location_url})

######################################################################
# LIST ALL ACCOUNTS
######################################################################
@app.route("/accounts", methods=["GET"])
def list_all_accounts():
    """List all accounts"""
    account_list = Account.all()
    if len(account_list) == 0:
        return jsonify([]), status.HTTP_200_OK
    else:
        return jsonify([account.serialize() for account in account_list]), status.HTTP_200_OK

######################################################################
# READ AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def read_account(account_id: int):
    """Read an account depending on supplied ID"""
    account = Account.find(account_id)
    if account is None:
        return jsonify({"error": f"Account {account_id} not found"}), status.HTTP_404_NOT_FOUND
    return jsonify(account.serialize()), status.HTTP_200_OK

######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id: int):
    """Update an account depending on supplied ID"""
    check_content_type(HEADER_CONTENT_TYPE)
    account = Account.find(account_id)
    if account is None:
        return jsonify({"error": f"Account {account_id} not found"}), status.HTTP_404_NOT_FOUND
    account.deserialize(request.get_json())
    account.id = account_id
    account.update()
    return jsonify(account.serialize()), status.HTTP_200_OK

######################################################################
# DELETE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id: int):
    """Delete an account depending on supplied ID"""
    account = Account.find(account_id)
    if account is None:
        return jsonify({"error": f"Account {account_id} not found"}), status.HTTP_404_NOT_FOUND
    account.delete()
    return "", status.HTTP_204_NO_CONTENT

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type != media_type:
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {media_type}")
