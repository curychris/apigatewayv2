from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Mode mock (untuk development lokal tanpa AWS/API)
IS_MOCK = os.getenv("MOCK_AWS", "true").lower() == "true"

# Dummy config buat tampilan
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "dummy-bucket")
API_URL = os.getenv("API_GATEWAY_URL", "http://localhost:5000/mock-api")

# === MOCK SECTION ===
if IS_MOCK:
    print("🧪 Running in MOCK mode...")

    class MockS3Client:
        def upload_fileobj(self, file, bucket, key):
            print(f"📦 [MOCK] Pretending to upload {key} to bucket {bucket}")

    s3_client = MockS3Client()

    dummy_users = [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "institution": "Example University",
            "position": "Researcher",
            "phone": "1234567890",
            "image_url": "",
        }
    ]

else:
    import boto3
    import requests

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        region_name=AWS_REGION,
    )

@app.route("/")
def index():
    if IS_MOCK:
        users = dummy_users
    else:
        response = requests.get(API_URL)
        users = response.json()
    return render_template("index.html", users=users, s3_bucket=f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/")

@app.route("/users", methods=["POST"])
def add_user():
    name = request.form["name"]
    email = request.form["email"]
    institution = request.form["institution"]
    position = request.form["position"]
    phone = request.form["phone"]
    image = request.files["image"]

    # Check existing user
    if IS_MOCK:
        if any(u["email"] == email for u in dummy_users):
            return jsonify({"error": "Email already exists"}), 409
    else:
        check_response = requests.get(f"{API_URL}?email={email}")
        if check_response.status_code == 409:
            return jsonify({"error": "Email already exists"}), 409

    # Upload image
    image_url = ""
    if image:
        image_filename = f"users/{image.filename}"
        try:
            s3_client.upload_fileobj(image, S3_BUCKET, image_filename)
            image_url = f"https://{S3_BUCKET}.s3-{AWS_REGION}.amazonaws.com/{image_filename}"
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Save user
    user_data = {
        "name": name,
        "email": email,
        "institution": institution,
        "position": position,
        "phone": phone,
        "image_url": image_url,
    }

    if IS_MOCK:
        new_id = max(u["id"] for u in dummy_users) + 1
        user_data["id"] = new_id
        dummy_users.append(user_data)
    else:
        response = requests.post(API_URL, json=user_data)
        if response.status_code == 409:
            return jsonify({"error": "Email already exists"}), 409

    return redirect(url_for("index"))

@app.route("/users/<int:user_id>/delete", methods=["DELETE"])
def delete_user(user_id):
    if IS_MOCK:
        global dummy_users
        dummy_users = [u for u in dummy_users if u["id"] != user_id]
        return jsonify({"message": "User deleted successfully"}), 200
    else:
        response = requests.delete(f"{API_URL}/{user_id}")
        return jsonify(response.json()), response.status_code

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    if IS_MOCK:
        user = next((u for u in dummy_users if u["id"] == user_id), None)
        return jsonify(user), 200 if user else 404
    else:
        response = requests.get(f"{API_URL}/{user_id}")
        return jsonify(response.json()), response.status_code

@app.route("/users/<int:user_id>", methods=["PUT", "PATCH"])
def update_user(user_id):
    data = request.json
    if IS_MOCK:
        for u in dummy_users:
            if u["id"] == user_id:
                u.update(data)
                return jsonify({"message": "User updated", "data": u})
        return jsonify({"error": "User not found"}), 404
    else:
        response = requests.put(f"{API_URL}/{user_id}", json=data)
        return jsonify(response.json()), response.status_code

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
