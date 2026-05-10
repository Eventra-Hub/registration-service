from fastapi import HTTPException
from bson import ObjectId

from app.db.mongo import users_collection
from app.core.security import (
    hash_password,
    verify_password,
    create_token
)
from app.events.publisher import publish_user_created


class UserService:

    async def register_user(self, data):

        existing = await users_collection.find_one(
            {"email": data.email}
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )

        user = {
            "email": data.email,
            "name": data.name,
            "password": hash_password(data.password),
            "role": data.role or "attendee",
            "bio": "",
            "avatar_url": ""
        }

        result = await users_collection.insert_one(user)

        user_id = str(result.inserted_id)

        # publish event to RabbitMQ
        await publish_user_created({
            "id": user_id,
            "email": data.email,
            "name": data.name
        })

        token = create_token(user_id)

        return {
            "access_token": token
        }

    async def login_user(self, data):

        user = await users_collection.find_one(
            {"email": data.email}
        )

        if not user or not verify_password(
            data.password,
            user["password"]
        ):

            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        token = create_token(str(user["_id"]))

        return token

    async def get_profile(self, user_id):

        user = await users_collection.find_one(
            {"_id": ObjectId(user_id)}
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user.get("role", ""),
            "bio": user.get("bio", ""),
            "avatar_url": user.get("avatar_url", "")
        }

    async def update_profile(self, user_id, data):

        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "name": data.name,
                    "bio": data.bio,
                    "avatar_url": data.avatar_url
                }
            }
        )

        updated_user = await users_collection.find_one(
            {"_id": ObjectId(user_id)}
        )

        return {
            "id": str(updated_user["_id"]),
            "email": updated_user["email"],
            "name": updated_user["name"],
            "role": updated_user.get("role", ""),
            "bio": updated_user.get("bio", ""),
            "avatar_url": updated_user.get("avatar_url", "")
        }
