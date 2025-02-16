from sqlalchemy import BigInteger, String, Integer, DateTime, func, ForeignKey, Column, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncAttrs
from sqlalchemy import JSON
from sqlalchemy.orm import sessionmaker

# Create the engine
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

# Session maker
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    # id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True)
    login: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    password: Mapped[str | None] = mapped_column(String, nullable=True)
    subscribe: Mapped[str | None] = mapped_column(String, nullable=True)

    model_using: Mapped[str | None] = mapped_column(String, nullable=True, default="gpt-3.5-turbo")
    voice_model: Mapped[str | None] = mapped_column(String, nullable=True, default="pNInz6obpgDQGcFmaJgB")
    prefix: Mapped[str | None] = mapped_column(String, nullable=True)

    subscribe_time: Mapped[str | None] = mapped_column(String, nullable=True, default="4040-12-3")

    admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    message_count: Mapped[int] = mapped_column(Integer, default=30)
    max_length_sym: Mapped[int] = mapped_column(Integer, default=30)
    image_count: Mapped[int] = mapped_column(Integer, default=30)
    voice_count: Mapped[int] = mapped_column(Integer, default=30)

    # поля

    message_month: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class GPTMessage(Base):
    __tablename__ = 'gpt_messages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="messages")


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payment_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    subscribe: Mapped[str] = mapped_column(String, nullable=False)

    time: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Integer, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="payments")


class Subscribe(Base):
    __tablename__ = 'subscribes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    message_count: Mapped[int] = mapped_column(Integer, default=30)
    max_length_sym: Mapped[int] = mapped_column(Integer, default=30)
    image_count: Mapped[int] = mapped_column(Integer, default=30)
    voice_count: Mapped[int] = mapped_column(Integer, default=30)


class Blog(Base):
    __tablename__ = 'blogs'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    img: Mapped[str] = mapped_column(String, nullable=True)
    link: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )


class Article(Base):
    __tablename__ = 'articles'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    img: Mapped[str] = mapped_column(String, nullable=True)
    link: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )


User.messages = relationship("GPTMessage", back_populates="user", cascade="all, delete-orphan")
User.payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
