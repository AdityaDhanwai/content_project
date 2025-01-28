# from flask import Flask, render_template, request, redirect, url_for, flash
# import boto3
# import os
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
# from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_S3_BUCKET, AWS_S3_REGION, UPLOAD_FOLDER

# app = Flask(__name__)
# app.secret_key = "supersecretkey"  # Replace with a strong key
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///content_metadata.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# # S3 client
# s3_client = boto3.client(
#     's3',
#     aws_access_key_id=AWS_ACCESS_KEY,
#     aws_secret_access_key=AWS_SECRET_KEY,
#     region_name=AWS_S3_REGION
# )

# # Database model
# class ContentMetadata(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     file_type = db.Column(db.String(50), nullable=False)  # "image" or "video"
#     file_name = db.Column(db.String(200), nullable=False)
#     caption = db.Column(db.Text, nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return f"Content(id={self.id}, file_name={self.file_name}, file_type={self.file_type})"

# # Routes
# @app.route("/", methods=["GET", "POST"])
# def choose_upload_type():
#     if request.method == "POST":
#         file_type = request.form.get("file_type")
#         if file_type in ["image", "video"]:
#             return redirect(url_for("upload_file", file_type=file_type))
#         else:
#             flash("Invalid choice. Please select either Image or Video.", "danger")
#     return render_template("upload_choice.html")

# @app.route("/upload/<file_type>", methods=["GET", "POST"])
# def upload_file(file_type):
#     if request.method == "POST":
#         uploaded_file = request.files.get("file")
#         caption = request.form.get("caption")

#         if uploaded_file and caption:
#             # Save file temporarily
#             local_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
#             uploaded_file.save(local_path)

#             # Upload to S3 with public read access
#             s3_key = f"{file_type}s/{uploaded_file.filename}"
#             import mimetypes

#             # Detect the correct content type based on the file extension
#             content_type = mimetypes.guess_type(local_path)[0] or "application/octet-stream"

#             s3_client.upload_file(
#                 local_path,
#                 AWS_S3_BUCKET,
#                 s3_key,
#                 ExtraArgs={"ContentType": content_type}  # 👈 Set correct MIME type
#             )



#             # Save metadata in the database
#             metadata = ContentMetadata(file_type=file_type, file_name=s3_key, caption=caption)
#             db.session.add(metadata)
#             db.session.commit()

#             # Cleanup
#             os.remove(local_path)

#             flash(f"{file_type.capitalize()} and caption uploaded successfully!", "success")
#             return redirect(url_for("view_content"))
#         else:
#             flash("Please upload a file and provide a caption.", "danger")

#     return render_template("upload_form.html", file_type=file_type)


# @app.route("/content", methods=["GET"])
# def view_content():
#     contents = ContentMetadata.query.all()
#     return render_template("view_content.html", contents=contents, bucket_name=AWS_S3_BUCKET)

# if __name__ == "__main__":
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
#     # ✅ Ensure database tables are created inside app context
#     with app.app_context():
#         db.create_all()
    
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash
import boto3
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_S3_BUCKET, AWS_S3_REGION, UPLOAD_FOLDER

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Replace with a strong key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///content_metadata.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# S3 Client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_S3_REGION
)

# Database Model
class ContentMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_type = db.Column(db.String(50), nullable=False)  # "image" or "video"
    file_name = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Content(id={self.id}, file_name={self.file_name}, file_type={self.file_type})"

# Route to Choose File Type
@app.route("/", methods=["GET", "POST"])
def choose_upload_type():
    if request.method == "POST":
        file_type = request.form.get("file_type")
        if file_type in ["image", "video"]:
            return redirect(url_for("upload_file", file_type=file_type))
        else:
            flash("Invalid choice. Please select either Image or Video.", "danger")
    return render_template("upload_choice.html")

# Route to Upload File
@app.route("/upload/<file_type>", methods=["GET", "POST"])
def upload_file(file_type):
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        caption = request.form.get("caption")

        if uploaded_file and caption:
            # Save file temporarily
            local_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(local_path)

            # Upload to S3 with correct MIME type
            s3_key = f"{file_type}s/{uploaded_file.filename}"
            import mimetypes
            content_type = mimetypes.guess_type(local_path)[0] or "application/octet-stream"

            s3_client.upload_file(
                local_path,
                AWS_S3_BUCKET,
                s3_key,
                ExtraArgs={"ContentType": content_type}  # 👈 Set correct MIME type
            )

            # Save metadata in database
            metadata = ContentMetadata(file_type=file_type, file_name=s3_key, caption=caption)
            db.session.add(metadata)
            db.session.commit()

            # Cleanup local file
            os.remove(local_path)

            flash(f"{file_type.capitalize()} and caption uploaded successfully!", "success")
            return redirect(url_for("view_content"))
        else:
            flash("Please upload a file and provide a caption.", "danger")

    return render_template("upload_form.html", file_type=file_type)

# Route to View Content
@app.route("/content", methods=["GET"])
def view_content():
    contents = ContentMetadata.query.all()
    return render_template("view_content.html", contents=contents, bucket_name=AWS_S3_BUCKET, region=AWS_S3_REGION)

# Route to Delete Content (File from S3 + Entry from DB)
@app.route("/delete/<int:content_id>", methods=["POST"])
def delete_content(content_id):
    content = ContentMetadata.query.get(content_id)
    if content:
        try:
            # Delete file from S3
            s3_client.delete_object(Bucket=AWS_S3_BUCKET, Key=content.file_name)
            print(f"Deleted {content.file_name} from S3")
        except Exception as e:
            print(f"Error deleting from S3: {e}")

        # Delete entry from database
        db.session.delete(content)
        db.session.commit()

        flash("Content deleted successfully!", "success")
    else:
        flash("Content not found!", "danger")

    return redirect(url_for("view_content"))

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Ensure database tables are created inside app context
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
