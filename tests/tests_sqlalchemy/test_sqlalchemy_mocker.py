import pytest
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    DateTime,
    inspect
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from pymocker.mocker import Mocker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
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

mocker = Mocker()

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

    @pytest.fixture(scope="function")
    def db_session(self, postgres_db:str):
        """
        A function-scoped fixture to provide a database session for tests.
        """
        engine = create_engine(postgres_db)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.rollback()
        session.close()
        Base.metadata.drop_all(engine)

    def test_sqlalchemy_factory_creation(self):
        """
        Tests that Mocker can create a factory for a SQLAlchemy model.
        """
        @mocker.mock()
        class UserFactory(SQLAlchemyFactory):
            __model__ = User
        assert UserFactory.__model__ == User
        assert hasattr(UserFactory, "build")

    def test_sqlalchemy_build_instance(self, db_session: Session):
        """
        Tests that the factory can build an instance without persisting it.
        """
        @mocker.mock()
        class UserFactory(SQLAlchemyFactory):
            __model__ = User
        user_instance = UserFactory.build()
        assert isinstance(user_instance, User)
        assert inspect(user_instance).transient

    def test_sqlalchemy_create_instance(self, db_session: Session):
        """
        Tests that the factory can create and persist an instance.
        """
        @mocker.mock(session=db_session)
        class UserFactory(SQLAlchemyFactory):
            __model__ = User
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
        @mocker.mock(session=db_session, set_relationships=True)
        class UserFactory(SQLAlchemyFactory):
            __model__ = User
        @mocker.mock(session=db_session, set_relationships=True)
        class PostFactory(SQLAlchemyFactory):
            __model__ = Post
        
        try:
            SQLAlchemyFactory.register_factory(User, UserFactory)

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
        finally:
            SQLAlchemyFactory.unregister_factory(User)

    def test_generated_data_types(self, db_session: Session):
        """
        Tests that the generated data types match the model's column types.
        """
        @mocker.mock(session=db_session, set_relationships=True)
        class UserFactory(SQLAlchemyFactory):
            __model__ = User

        @mocker.mock(session=db_session, set_relationships=True)
        class PostFactory(SQLAlchemyFactory):
            __model__ = Post
        
        try:
            SQLAlchemyFactory.register_factory(User, UserFactory)
            post_instance = PostFactory.create_sync()

            assert isinstance(post_instance.id, int)
            assert isinstance(post_instance.title, str)
            assert isinstance(post_instance.content, str)
            assert isinstance(post_instance.user_id, int)
            assert isinstance(post_instance.created_at, datetime.datetime)
            assert isinstance(post_instance.rating, float)
        finally:
            SQLAlchemyFactory.unregister_factory(User)

    def test_batch_creation(self, db_session: Session):
        """
        Tests creating a batch of instances.
        """
        @mocker.mock(session=db_session)
        class UserFactory(SQLAlchemyFactory):
            __model__ = User
        
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
