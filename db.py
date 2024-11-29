import os

from sqlalchemy import create_engine, Column, String, Boolean, MetaData, Table, insert, select
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import exists

PSTGRE_SERVER = os.environ['PSTGRE_SERVER']
PSTGRE_USER = os.environ['PSTGRE_USER']
PSTGRE_PASS = os.environ['PSTGRE_PASS']
PSTGRE_DB = os.environ['PSTGRE_DB']

DATABASE_URL = f'postgresql://{PSTGRE_USER}:{PSTGRE_PASS}@{PSTGRE_SERVER}/{PSTGRE_DB}'

engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()


# ------------------- Define Models -------------------

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    real_name = Column(String, nullable=False)
    is_deleted = Column(Boolean)
    is_admin = Column(Boolean, default=False)
    is_ignore = Column(Boolean, default=False)


def create_audit_table(audit_name):
    metadata = MetaData()
    audit_table = Table(
        audit_name, metadata,
        Column('id', String, primary_key=True, nullable=False),
        Column('name', String, nullable=False),
        Column('answer', String, nullable=False),
    )
    audit_table.create(engine)
    return audit_table


# ------------------- Utility Functions -------------------

# Create all tables defined in the models
def create_tables():
    Base.metadata.create_all(engine)


# Drop all tables (useful for reset or testing)
def drop_tables():
    Base.metadata.drop_all(engine)


def update_users(users, to_admin=False, to_ignore=False, by_name=False):
    not_found_users = []
    for user in users:
        if by_name:
            user = user.replace('@', '')
            existing_user = session.query(User).filter_by(name=user).first()
            if existing_user:
                if to_ignore:
                    existing_user.is_ignore = not existing_user.is_ignore
                if to_admin:
                    existing_user.is_admin = not existing_user.is_admin
            else:
                not_found_users.append(user)
        else:
            if not user.get('is_bot') and user.get('id') != 'USLACKBOT':
                new_db_user = User(
                    id=user.get('id'),
                    name=user.get('name'),
                    real_name=user.get('profile').get('real_name'),
                    is_deleted=user.get('deleted')
                )
                existing_user = session.query(User).filter_by(id=user.get('id')).first()
                if existing_user:
                    if existing_user.is_deleted != new_db_user.is_deleted:
                        existing_user.is_deleted = new_db_user.is_deleted
                        print(f"User '{new_db_user.name}' found. Updating is_deleted to {new_db_user.is_deleted}.")
                else:
                    session.add(new_db_user)
    session.commit()
    return not_found_users


def get_users(command_name, second_table=None):
    if command_name == '/ignore_show':
        return session.query(User).filter_by(is_ignore=True).all()
    elif command_name == '/admin_show':
        return session.query(User).filter_by(is_admin=True).all()
    elif command_name == '/audit_stop':
        return session.query(second_table)
    elif command_name == '/audit_unanswered':
        return (
            session.query(User)
            .filter_by(is_deleted=False)
            .filter_by(is_ignore=False)  # Filter User.is_ignore == False
            .filter(~exists().where(second_table.c.id == User.id))  # Exclude users in audit_table
            .all()
        )
    return f"Unknown setup. Bugreport created"


def check_if_table_exist(table_name):
    metadata = MetaData()
    metadata.reflect(bind=engine)
    if table_name in metadata.tables:
        table = metadata.tables[table_name]
        return table
    else:
        return None


def add_row(table, data):
    inserting = insert(table).values(data)
    with engine.connect() as conn:
        conn.execute(inserting)
        conn.commit()


def select_table(table):
    with engine.connect() as connection:
        table_obj = select(table)
        result = connection.execute(table_obj)
        return result
