import asyncio
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, select, delete
from sqlalchemy.orm import registry, Session

__mapper_registry = registry()
Base = __mapper_registry.generate_base()


class User(Base):
    __tablename__ = 'user'

    telegram_id = Column(Integer, primary_key=True)
    token = Column(String(64))

    def __repr__(self):
        return f'User(telegram_id={self.telegram_id!r}, token={self.token!r})'


class Database:
    """Обеспечивает доступ к базе данных."""

    __engine = create_engine("sqlite+pysqlite:///users.sqlite", echo=True, future=True)
    __lock = asyncio.Lock()

    def __init__(self):
        Base.metadata.create_all(self.__engine)

    def dispose(self):
        self.__engine.dispose()

    async def get_or_create_user(self, telegram_id: int) -> Optional[User]:
        """Возвращает пользователя из базы данных, или создаёт нового, если в базе его нет."""
        async with self.__lock:
            return await asyncio.to_thread(self.__get_or_create_user_sync, telegram_id)

    def __get_or_create_user_sync(self, telegram_id: int) -> Optional[User]:
        with Session(self.__engine) as session:
            user = self.__get_user(session, telegram_id)

            if user is not None:
                return user

            self.__create_user(session, telegram_id)

            session.commit()

            return self.__get_user(session, telegram_id)

    @staticmethod
    def __create_user(session: Session, telegram_id: int):
        session.add(User(telegram_id=telegram_id))

    @staticmethod
    def __get_user(session: Session, telegram_id: int) -> Optional[User]:
        statement = select(User).where(User.telegram_id == telegram_id)
        user = session.scalars(statement).first()
        return user

    async def create_new_user(self, telegram_id: int) -> Optional[User]:
        """Создаёт нового пользователя с удалением старой записи, если она была."""
        async with self.__lock:
            return await asyncio.to_thread(self.__create_new_user_sync, telegram_id)

    def __create_new_user_sync(self, telegram_id: int) -> Optional[User]:
        with Session(self.__engine) as session:
            self.__delete_user(session, telegram_id)
            self.__create_user(session, telegram_id)
            session.commit()
            return self.__get_user(session, telegram_id)

    @staticmethod
    def __delete_user(session: Session, telegram_id: int):
        session.execute(delete(User).where(User.telegram_id == telegram_id))

    async def update_token(self, telegram_id: int, token: str):
        """Обновляет токен пользователя."""
        async with self.__lock:
            return await asyncio.to_thread(
                self.__update_user_sync, telegram_id, token
            )

    def __update_user_sync(self, telegram_id: int, token: str):
        with Session(self.__engine) as session:
            user = self.__get_user(session, telegram_id)

            if user is None:
                return

            user.token = token
            session.commit()
