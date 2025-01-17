import os
import asyncio
import httpx
from cachetools import TTLCache
from dotenv import load_dotenv

load_dotenv()

UBW_API_URL = "https://prd-svc.ubw.unit.no/UBWHVL-web-api/v1"
UBW_USERNAME = "robot-reskontro"
UBW_PASSWORD = "vinterIjanuar2019"

import asyncio
user_cache = TTLCache(maxsize=100, ttl=300)  # Cache valid for 5 minutes

async def get_authorized_users():
    if "users" not in user_cache:
        async with httpx.AsyncClient() as client:
            try:
                API_URL = f'{UBW_API_URL}/objects/users'
                API_PARAMS = {
                    "companyId": "TF",
                    "select": "userName",
                    "filter": "rolesAndCompanies/any(rc: rc/roleId eq 'ORDRE')",
                }
                API_USERNAME = UBW_USERNAME
                API_PASSWORD = UBW_PASSWORD
                
                print(f"Request URL: {API_URL}")
                print(f"Request Params: {API_PARAMS}")
                print(f"Request Auth: {API_USERNAME}")

                response = await client.get(
                    API_URL,
                    params=API_PARAMS,
                    auth=(API_USERNAME, API_PASSWORD),
                )

                print(f"Response Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")

                response.raise_for_status()
                data = response.json()
                users = [user["userName"] for user in data]
                user_cache["users"] = users
            except Exception as e:
                print(f"Failed to fetch authorized users: {e}")
                user_cache["users"] = []
    return user_cache["users"]



async def main():
    authorized_users = await get_authorized_users()
    print(f"Total authorized users: {len(authorized_users)}")
    
    


if __name__ == "__main__":
    asyncio.run(main())