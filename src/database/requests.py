import json
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select, update, delete
from src.database.models import async_session, User, Subscribe, GPTMessage, Payment, Article, Blog
from sqlalchemy import desc
from sqlalchemy import func
import hashlib


async def set_user(telegram_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

        if not user:
            session.add(User(telegram_id=telegram_id,
                             subscribe="subscribes_free",
                             message_count=300))
            await session.commit()
            return True
        return False


async def set_user_id(login: str, password: str):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    async with async_session() as session:
        # Проверяем, существует ли пользователь с таким логином
        existing_user = await session.scalar(select(User).where(User.login == login))
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this login already exists.")

        # Создаем нового пользователя
        new_user = User(
            telegram_id=None,
            login=login,
            password=hashed_password,
            subscribe="subscribes_free",
            message_count=300
        )
        session.add(new_user)
        await session.commit()
        return True


async def get_user(identifier):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where((User.telegram_id == identifier) | (User.id == identifier))
        )

        if user:
            return {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "subscribe": user.subscribe,
                "subscribe_time": user.subscribe_time,
                "model_using": user.model_using,
                "prefix": user.prefix,
                "voice_model": user.voice_model,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "message_count": user.message_count,
                "max_length_sym": user.max_length_sym,
                "image_count": user.image_count,
                "voice_count": user.voice_count,
                "message_month": user.message_month,
                "admin": user.admin
            }


async def get_user_login(login):
    async with async_session() as session:
        query = select(User).where(User.login == login)
        user = await session.scalar(query)

        if user:
            return {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "subscribe": user.subscribe,
                "subscribe_time": user.subscribe_time,
                "model_using": user.model_using,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "message_count": user.message_count,
                "max_length_sym": user.max_length_sym,
                "image_count": user.image_count,
                "voice_count": user.voice_count,
                "message_month": user.message_month,
                "password": user.password
            }


async def get_subscribe():
    async with async_session() as session:
        result = await session.execute(select(Subscribe))
        subscribes = result.scalars().all()

        if subscribes:
            return [
                {column.name: getattr(subscribe, column.name) for column in Subscribe.__table__.columns}
                for subscribe in subscribes
            ]

        return None


async def add_subscribe(name: str, price: int):
    async with async_session() as session:
        new_subscribe = Subscribe(name=name, price=price)
        session.add(new_subscribe)
        await session.commit()
        await session.refresh(new_subscribe)
        return {"id": new_subscribe.id, "name": new_subscribe.name, "price": new_subscribe.price}


async def update_subscribe(subscribe_id: int, name: str = None, price: int = None):
    async with async_session() as session:
        result = await session.execute(select(Subscribe).where(Subscribe.id == subscribe_id))
        subscribe = result.scalar_one_or_none()

        if not subscribe:
            return None

        if name:
            subscribe.name = name
        if price:
            subscribe.price = price

        await session.commit()
        await session.refresh(subscribe)
        return {"id": subscribe.id, "name": subscribe.name, "price": subscribe.price}


async def create_user_payment(user_id, payment_id, subscribe, time, price):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where((User.telegram_id == user_id) | (User.id == user_id))
        )

        if user:
            payment = Payment(
                payment_id=payment_id,
                price=price,
                subscribe=subscribe,
                time=time,
                user_id=user.id
            )
            session.add(payment)
            await session.commit()
            return True

        return False


async def add_message_to_gpt(user_id, message):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where((User.telegram_id == user_id) | (User.id == user_id))
        )

        if user:
            # Сериализуем словарь message в JSON
            message_json = json.dumps(message)

            gpt_message = GPTMessage(
                message=message_json,  # Сохранение сообщения в формате JSON
                user_id=user.id
            )
            session.add(gpt_message)
            await session.commit()
            return True

        return False


async def get_user_messages(user_id):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where((User.telegram_id == user_id) | (User.id == user_id))
        )

        if user:
            result = await session.execute(
                select(GPTMessage)
                .where(GPTMessage.user_id == user.id)
                .order_by(desc(GPTMessage.created_at))  # Сортировка по убыванию (самое новое сообщение)
            )
            messages = result.scalars().all()

            return [
                {
                    "id": message.id,
                    "message": json.loads(message.message),
                    "created_at": message.created_at
                }
                for message in messages
            ]

        return None


async def get_assistant_messages(user_id):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where((User.telegram_id == user_id) | (User.id == user_id))
        )

        if user:
            result = await session.execute(
                select(GPTMessage)
                .where(GPTMessage.user_id == user.id)
                .where(func.json_extract(GPTMessage.message, '$.role') == "assistant")  # Используем json_extract
                .order_by(desc(GPTMessage.created_at))  # Сортировка по убыванию
            )
            messages = result.scalars().all()

            return [
                {
                    "id": message.id,
                    "message": json.loads(message.message),
                    "created_at": message.created_at
                }
                for message in messages
            ]

        return None


async def get_user_payments(user_id):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where((User.telegram_id == user_id) | (User.id == user_id))
        )

        if user:
            result = await session.execute(
                select(Payment)
                .where(Payment.user_id == user.id)
                .order_by(Payment.created_at.desc())
                .limit(1)  # Ограничиваем результат одной самой последней записью
            )
            payment = result.scalars().first()  # Берем первую (и единственную) запись

            return payment

        return None


async def update_user(user_id, subscribe=None, model_using=None, subscribe_time=None, prefix=None, voice_model=None,
                      admin=None, message_count=None, max_length_sym=None, image_count=None, voice_count=None):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where((User.telegram_id == user_id) | (User.id == user_id))
        )

        if user:
            # Обновляем только те поля, которые переданы
            if subscribe is not None:
                user.subscribe = subscribe
            if model_using is not None:
                user.model_using = model_using
            if subscribe_time is not None:
                user.subscribe_time = subscribe_time
            if prefix is not None:
                user.prefix = prefix
            if voice_model is not None:
                user.voice_model = voice_model
            if admin is not None:
                user.admin = admin
            if message_count is not None:
                user.message_count = message_count
            if max_length_sym is not None:
                user.max_length_sym = max_length_sym
            if image_count is not None:
                user.image_count = image_count
            if voice_count is not None:
                user.voice_count = voice_count

            # Обновляем время последнего изменения
            user.updated_at = func.now()

            # Сохраняем изменения в базе данных
            await session.commit()
            return True

        return False


async def update_user_message(user_id, max_length_sym=None, message_count=None, image_count=None, voice_count=None):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where((User.telegram_id == user_id) | (User.id == user_id))
        )

        if user:
            if message_count is not None:
                user.message_count = message_count
            if max_length_sym is not None:
                user.max_length_sym = max_length_sym
            if image_count is not None:
                user.image_count = image_count
            if voice_count is not None:
                user.voice_count = voice_count

            # Обновляем время последнего изменения
            user.updated_at = func.now()

            # Сохраняем изменения в базе данных
            await session.commit()
            return True

        return False


async def subscribe_search(name: str):
    async with async_session() as session:
        subscribe = await session.scalar(
            select(Subscribe).where((Subscribe.name == name))
        )

        if subscribe:
            return {
                "id": subscribe.id,
                "name": subscribe.name,
                "price": subscribe.price,
                "message_count": subscribe.message_count,
                "max_length_sym": subscribe.max_length_sym,
                "image_count": subscribe.image_count,
                "voice_count": subscribe.voice_count,
            }

        return False


async def get_articles():
    async with async_session() as session:
        result = await session.execute(select(Article).order_by(desc(Article.created_at)))
        articles = result.scalars().all()

        if articles:
            return [
                {
                    "id": article.id,
                    "title": article.title,
                    "text": article.text,
                    "img": article.img,
                    "link": article.link,
                    "created_at": article.created_at
                }
                for article in articles
            ]
        return None


async def get_blogs():
    async with async_session() as session:
        result = await session.execute(select(Blog).order_by(desc(Blog.created_at)))
        blogs = result.scalars().all()

        if blogs:
            return [
                {
                    "id": blog.id,
                    "title": blog.title,
                    "text": blog.text,
                    "img": blog.img,
                    "link": blog.link,
                    "created_at": blog.created_at
                }
                for blog in blogs
            ]
        return None


async def create_article(title, text, img=None, link=None):
    async with async_session() as session:
        article = Article(title=title, text=text, img=img, link=link)
        session.add(article)
        await session.commit()  # Коммит после добавления статьи
        return {"message": "Article created successfully", "id": article.id}


async def create_blog(title, text, img=None, link=None):
    async with async_session() as session:
        blog = Blog(
            title=title,
            text=text,
            img=img,
            link=link
        )
        session.add(blog)
        await session.commit()
        return {"message": "Blog created successfully", "id": blog.id}


async def update_blog(blog_id: int, title: str = None, text: str = None, img: str = None, link: str = None):
    async with async_session() as session:
        # Создаем запрос на обновление
        stmt = (
            update(Blog)
            .where(Blog.id == blog_id)
            .values(
                title=title if title is not None else Blog.title,
                text=text if text is not None else Blog.text,
                img=img if img is not None else Blog.img,
                link=link if link is not None else Blog.link
            )
        )
        # Выполняем запрос
        await session.execute(stmt)
        await session.commit()

        # Возвращаем обновленный блог
        updated_blog = await session.get(Blog, blog_id)
        if not updated_blog:
            raise HTTPException(status_code=404, detail="Blog not found")
        return updated_blog


async def update_article(article_id: int, title: str = None, text: str = None, img: str = None, link: str = None):
    async with async_session() as session:
        stmt = (
            update(Article)
            .where(Article.id == article_id)
            .values(
                title=title if title is not None else Article.title,
                text=text if text is not None else Article.text,
                img=img if img is not None else Article.img,
                link=link if link is not None else Article.link
            )
        )

        await session.execute(stmt)
        await session.commit()

        updated_article = await session.get(Article, article_id)
        if not updated_article:
            raise HTTPException(status_code=404, detail="Article not found")
        return updated_article


async def delete_blog(blog_id: int):
    async with async_session() as session:
        # Проверяем, существует ли блог с таким ID
        blog = await session.get(Blog, blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")

        # Создаем запрос на удаление
        stmt = delete(Blog).where(Blog.id == blog_id)
        await session.execute(stmt)
        await session.commit()

        return {"message": "Blog deleted successfully"}


async def delete_article(article_id: int):
    async with async_session() as session:
        # Проверяем, существует ли блог с таким ID
        article = await session.get(Article, article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Blog not found")

        # Создаем запрос на удаление
        stmt = delete(Article).where(Article.id == article_id)
        await session.execute(stmt)
        await session.commit()

        return {"message": "Blog deleted successfully"}


async def get_article_by_id(article_id):
    async with async_session() as session:
        article = await session.scalar(select(Article).where(Article.id == article_id))
        if article:
            return {
                "id": article.id,
                "title": article.title,
                "text": article.text,
                "img": article.img,
                "link": article.link,
                "created_at": article.created_at
            }
        return None


async def get_blog_by_id(blog_id):
    async with async_session() as session:
        blog = await session.scalar(select(Blog).where(Blog.id == blog_id))
        if blog:
            return {
                "id": blog.id,
                "title": blog.title,
                "text": blog.text,
                "img": blog.img,
                "link": blog.link,
                "created_at": blog.created_at
            }
        return None


async def remove_user_by_id(user_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))

        if user:
            await session.delete(user)
            await session.commit()
            return True

        return False


async def remove_user_by_telegram_id(telegram_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

        if user:
            await session.delete(user)
            await session.commit()
            return True

        return False


async def remove_blog(blog_id):
    async with async_session() as session:
        blog = await session.scalar(select(Blog).where(Blog.id == blog_id))

        if blog:
            await session.delete(blog)
            await session.commit()
            return True

        return False


async def remove_article(article_id):
    async with async_session() as session:
        article = await session.scalar(select(Article).where(Article.id == article_id))

        if article:
            await session.delete(article)
            await session.commit()
            return True

        return False


async def remove_message(message_id):
    async with async_session() as session:
        message = await session.scalar(select(GPTMessage).where(GPTMessage.id == message_id))

        if message:
            await session.delete(message)
            await session.commit()
            return True

        return False
