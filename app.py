import os
from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
from utils.aws_utils import upload_to_s3, send_to_sqs
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables
load_dotenv()
app = Flask(__name__)

# DB setup
engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    about = Column(Text)
    photo_path = Column(Text)

Base.metadata.create_all(engine)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        about = request.form["about"]
        photo = request.files["photo"]

        s3_key = upload_to_s3(photo, os.getenv("S3_BUCKET"))
        send_to_sqs(os.getenv("SQS_QUEUE_URL"), s3_key)

        session = SessionLocal()
        new_user = User(
            name=name,
            email=email,
            about=about,
            photo_path=s3_key
        )
        session.add(new_user)
        session.commit()
        session.close()

        return redirect(url_for("show_users"))
    return render_template("index.html")

@app.route("/users")
def show_users():
    session = SessionLocal()
    users = session.query(User).all()
    session.close()
    return render_template("users.html", users=users, bucket=os.getenv("S3_BUCKET"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
