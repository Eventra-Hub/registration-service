from app.db.mongo import users_collection
from app.core.security import hash_password, verify_password, create_token
from app.events.publisher import publish_user_created
from bson import ObjectId

class UserService:

    async def register_user(self, data):
        existing = await users_collection.find_one({"email": data.email})
        if existing:
            raise Exception("User already exists")

        user = {
            "email": data.email,
            "name": data.name,
            "password": hash_password(data.password)
        }

        result = await users_collection.insert_one(user)
        user_id = str(result.inserted_id)

        # publish event to RabbitMQ
        await publish_user_created({
            "id": user_id,
            "email": data.email,
            "name": data.name
        })

        return user_id

    async def login_user(self, data):
        user = await users_collection.find_one({"email": data.email})

        if not user or not verify_password(data.password, user["password"]):
            raise Exception("Invalid credentials")

        token = create_token(str(user["_id"]))
        return token