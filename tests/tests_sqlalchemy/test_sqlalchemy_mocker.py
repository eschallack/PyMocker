import pytest
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    DateTime,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from pymocker.mocker import Mocker
import datetime
import docker
import time
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
# Load environment variables from .env file
load_dotenv()

# 1. Define SQLAlchemy models
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

@pytest.mark.usefixtures("db_session")
class TestSQLAlchemyMocker:

    @pytest.fixture(scope="class")
    def postgres_db(self):
        """
        A class-scoped fixture to provide a running PostgreSQL container.
        """
        client = docker.from_env()
        container = None
        
        try:
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
                ports={"5432/tcp": 9898}
            )

            container.reload()
            retries = 10
            delay = 5
            for i in range(retries):
                try:
                    host_ports = container.ports["5432/tcp"]
                    if not isinstance(host_ports,list) or len(host_ports) == 0:
                        raise TypeError
                    
                    host_port=host_ports[0]["HostPort"]
                    db_url = f"postgresql://postgres:{os.environ.get('POSTGRES_PASSWORD','testpassword')}@localhost:{host_port}/postgres"
                    break
                except TypeError:
                    time.sleep(delay)
            for i in range(retries):
                try:
                    engine = create_engine(db_url)
                    engine.connect()
                    print("Database connection successful!")
                    break
                except Exception:
                    print(f"Database not ready yet. Retrying in {delay}s... ({i+1}/{retries})")
                    time.sleep(delay)
            else:
                pytest.fail("Could not connect to the database container.")
            yield db_url

        finally:
            if container:
                print("\nStopping and removing PostgreSQL container...")
                container.stop()
                container.remove()

    @pytest.fixture(scope="class")
    def db_session(self, postgres_db:str):
        """
        A class-scoped fixture to provide a database session for tests.
        """
        engine = create_engine(postgres_db)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
        Base.metadata.drop_all(engine)

    def test_sqlalchemy_factory_creation(self):
        """
        Tests that Mocker can create a factory for a SQLAlchemy model.
        """
        class UserFactory(Mocker):
            __model__ = User
        assert UserFactory.__model__ == User
        assert hasattr(UserFactory, "build")

    def test_sqlalchemy_build_instance(self, db_session: Session):
        """
        Tests that the factory can build an instance without persisting it.
        """
        class UserFactory(Mocker):
            __model__ = User
        user_instance = UserFactory.build()
        assert isinstance(user_instance, User)
        assert user_instance.id is None 
        assert isinstance(user_instance.name, str)
        assert isinstance(user_instance.age, int)

    def test_sqlalchemy_create_instance(self, db_session: Session):
        """
        Tests that the factory can create and persist an instance.
        """
        class UserFactory(Mocker):
            __model__ = User
        UserFactory.__session__ = db_session
        user_instance = UserFactory.create_sync()

        assert isinstance(user_instance, User)
        assert user_instance.id is not None 
        
        retrieved_user = db_session.query(User).filter_by(id=user_instance.id).one()
        assert retrieved_user is not None
        assert retrieved_user.name == user_instance.name
        assert retrieved_user.age == user_instance.age

    def test_sqlalchemy_pk_fk_relationship(self, db_session: Session):
        """
        Tests that PK/FK relationships are handled correctly.
        """
        class UserFactory(Mocker):
            __model__ = User
        class PostFactory(Mocker):
            __model__ = Post
        UserFactory.__session__ = db_session
        PostFactory.__session__ = db_session
        UserFactory.__set_relationships__ = True
        PostFactory.__set_relationships__ = True
        
        user = UserFactory.create_sync()
        post = PostFactory.create_sync(user_id=user.id)

        assert post.user_id == user.id
        assert post.user is not None
        assert post.user.id == user.id

        post_with_new_user = PostFactory.create_sync()
        assert post_with_new_user.user_id is not None
        assert post_with_new_user.user is not None
        
        retrieved_user = db_session.query(User).filter_by(id=post_with_new_user.user.id).one()
        assert retrieved_user is not None

    def test_generated_data_types(self, db_session: Session):
        """
        Tests that the generated data types match the model's column types.
        """
        class PostFactory(Mocker):
            __model__ = Post
        PostFactory.__session__ = db_session
        
        post_instance = PostFactory.create_sync()

        assert isinstance(post_instance.id, int)
        assert isinstance(post_instance.title, str)
        assert isinstance(post_instance.content, str)
        assert isinstance(post_instance.user_id, int)
        assert isinstance(post_instance.created_at, datetime.datetime)
        assert isinstance(post_instance.rating, float)

    def test_batch_creation(self, db_session: Session):
        """
        Tests creating a batch of instances.
        """
        class UserFactory(Mocker):
            __model__ = User
        UserFactory.__session__ = db_session
        
        num_users = 5
        users = UserFactory.create_batch_sync(num_users)

        assert len(users) == num_users
        for user in users:
            assert isinstance(user, User)
            assert user.id is not None
        
        assert db_session.query(User).count() >= num_users

    def test_table_creation(self, db_session: Session, postgres_db: str):
        """
        Tests that tables are created properly.
        """
        engine = create_engine(postgres_db)
        assert "users" in Base.metadata.tables
        assert "posts" in Base.metadata.tables
        
        from sqlalchemy import inspect
        inspector = inspect(engine)
        assert inspector.has_table("users")
        assert inspector.has_table("posts")