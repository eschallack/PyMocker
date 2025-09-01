from pymocker.mocker import Mocker
import docker
import docker.errors
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    DateTime,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import datetime
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="posts")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    rating = Column(Float)

def run_example():
    """
    Starts a postgres container, creates a user, prints it, and cleans up.
    """
    client = docker.from_env()
    container = None
    db_url = None

    try:
        # Start postgres container
        db_name = "postgres:latest"
        try:
            client.images.get(db_name)
        except docker.errors.ImageNotFound:
            print(f"Pulling {db_name} image...")
            client.images.pull(db_name)

        print("Starting PostgreSQL container...")
        container = client.containers.run(
            db_name,
            environment={"POSTGRES_PASSWORD": os.environ.get('POSTGRES_PASSWORD','testpassword')},
            detach=True,
            ports={"5432/tcp": None} # Use a random available port
        )

        # Get connection URL
        for i in range(10):
            try:
                container.reload()
                host_port = container.ports["5432/tcp"][0]["HostPort"]
                db_url = f"postgresql://postgres:{os.environ.get('POSTGRES_PASSWORD','testpassword')}@localhost:{host_port}/postgres"
                break
            except (IndexError, TypeError):
                time.sleep(1)
        
        if not db_url:
            raise Exception("Could not determine database URL.")

        # Connect to DB
        engine = create_engine(db_url)
        for i in range(10):
            try:
                engine.connect()
                print("Database connection successful!")
                break
            except Exception:
                time.sleep(1)
        else:
            raise Exception("Could not connect to the database container.")

        # Create table and session
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Create and save a user
        UserFactory = Mocker(User)
        user_instance = UserFactory.build()
        
        print("Generated User (in memory):", user_instance.name, user_instance.age)

        session.add(user_instance)
        session.commit()

        print("User saved to database with ID:", user_instance.id)

        # Query and print the user
        retrieved_user = session.query(User).filter_by(id=user_instance.id).one()
        print("Retrieved User from DB:", retrieved_user.name, retrieved_user.age)

        # Clean up tables
        Base.metadata.drop_all(engine)
        session.close()

    finally:
        if container:
            print("\nStopping and removing PostgreSQL container...")
            container.stop()
            container.remove()

if __name__ == '__main__':
    run_example()
