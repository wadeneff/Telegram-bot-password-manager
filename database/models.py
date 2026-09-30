from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    username: Mapped[str]
    tg_id: Mapped[int] = mapped_column(unique=True)

class UserAcc(Base):
    __tablename__ = 'user_acc'

    userId: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str]
    password: Mapped[str]
    passwords: Mapped["Passwords"] = relationship("Passwords", back_populates="user", cascade="all, delete-orphan", uselist=False)

class Passwords(Base):
    __tablename__ = 'passwords'

    userid: Mapped[int] = mapped_column(ForeignKey('user_acc.userId'), name='userid', primary_key=True)
    tg: Mapped[str|None]
    vk: Mapped[str|None]
    dis: Mapped[str|None]
    steam: Mapped[str|None]
    google: Mapped[str|None]
    yandex: Mapped[str|None]
    other: Mapped[str|None]
    other1: Mapped[str|None]
    other2: Mapped[str|None]
    other3: Mapped[str|None]
    other4: Mapped[str|None]
    other5: Mapped[str|None]
    user: Mapped["UserAcc"] = relationship("UserAcc", back_populates="passwords")
