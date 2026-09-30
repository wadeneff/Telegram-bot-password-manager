from database.models import Base, Passwords, UserAcc, Users
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = "sqlite+aiosqlite:///database/database.sql"

engine = create_async_engine(DATABASE_URL, echo=True)
asyncSession = async_sessionmaker(engine, expire_on_commit=False)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def test():
    async with asyncSession() as s, s.begin():
        query = select(UserAcc)
        result = await s.execute(query)
        users = result.scalar()
        return users

async def addUser(name: str, username: str, tg_id: int) -> None:
    async with asyncSession() as s, s.begin():
        query = select(Users).where(Users.tg_id == tg_id)
        result = await s.execute(query)
        userExists = result.scalar_one_or_none()

        if not userExists:
            newUser = Users(
                name=name,
                username=username,
                tg_id=tg_id,
            )
            s.add(newUser)
            await s.commit()

async def reg(login: str, password:str):
    async with asyncSession() as s, s.begin():
        query = select(UserAcc).where(UserAcc.login == login)
        result = await s.execute(query)
        userExists = result.scalar_one_or_none()

        if not userExists:
            newUserAcc = UserAcc(
                login=login,
                password=password,
                passwords=Passwords()
            )
            s.add(newUserAcc)
            await s.commit()
            return newUserAcc.userId
        else:
            return False

async def authing(login: str, password: str):
    async with asyncSession() as s, s.begin():
        query = select(UserAcc).where(UserAcc.login == login, UserAcc.password == password)
        result = await s.execute(query)
        userExists = result.scalar_one_or_none()

        if not userExists:
            return None
        else:
            return userExists.userId

async def getPassword(aId: int, social: str):
    async with asyncSession() as s, s.begin():
        column = getattr(Passwords, social, None)
        if column is None:
            return 'Empty'

        query = select(column).where(Passwords.userid == aId)
        result = await s.execute(query)

        return result.scalar()

async def editPassword(aId: int, social: str, password: str):
    async with asyncSession() as s, s.begin():
        query = select(Passwords).where(Passwords.userid == aId)
        result = await s.execute(query)
        user_passwords = result.scalar_one_or_none()
        setattr(user_passwords, social, password)
        await s.commit()
        return Passwords.userid
