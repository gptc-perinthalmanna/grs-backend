import json
import os
from uuid import UUID

from fastapi.testclient import TestClient
from _tests.tests import run_tests, test_admin_user, post, new_response, new_post
from main import app
from models.posts import NewResponse, NewPost
from services.db.deta.postsDB import delete_post_permanently_db
from services.db.deta.userDB import permanently_delete_user_from_db
from services.user import get_user

client = TestClient(app)
user = test_admin_user


@app.delete("/users/{username}/", include_in_schema=False)
async def delete_user(username):
    if username == user['username']:
        userd = await get_user(username)
        if userd is None:
            return "User didn't Exists"
        await permanently_delete_user_from_db(userd)
        return "success"
    else:
        return "Invalid Operation"


@app.delete("/posts/delete/{post_id}/", include_in_schema=False)
async def delete_post(post_id: UUID):
    if str(post_id) == post['key']:
        await delete_post_permanently_db(post_id.hex)


# def test_read_main():
#     response = client.get("/test/")
#     assert response.status_code == 200
#     assert response.json() == "Ok"


# def test_read_item_bad_token():
#     response = client.post("/posts/all/", headers={"Authorization": "invalid_token"})
#     assert response.status_code == 401
#     assert response.json() == {"detail": "Not authenticated"}


# def test_validation_and_models():
#     run_tests()


# def test_delete_test_user():
#     response = client.delete(f"/users/{user['username']}/")
#     assert response.status_code == 200


# def test_create_new_user():
#     response = client.post("/users/new/", data=json.dumps(user))
#     assert response.status_code == 200


# def test_get_jwt():
#     response = client.post("/token", data={"username": user['username'], "password": user['password']})
#     os.environ['TOKEN'] = response.json()['access_token']
#     assert response.status_code == 200


# def test_get_my_details():
#     response = client.get("/users/me/", headers={"Authorization": f"Bearer {os.getenv('TOKEN')}"})
#     assert response.status_code == 200


# def test_get_all_users():
#     response = client.post("/posts/all/", headers={"Authorization": f"Bearer {os.getenv('TOKEN')}"})
#     assert response.status_code == 200


# def test_remove_the_post():
#     response = client.delete(f"/posts/delete/{post['key']}/", headers={"Authorization": f"Bearer {os.getenv('TOKEN')}"})
#     assert response.status_code == 200


# def test_create_new_post():
#     response = client.post("/posts/new/", data=NewPost(**new_post).json(), headers={"Authorization": f"Bearer {os.getenv('TOKEN')}"})
#     assert response.status_code == 200


# def test_get_single_post():
#     response = client.get(f"/posts/{post['key']}/", headers={"Authorization": f"Bearer {os.getenv('TOKEN')}"})
#     assert response.status_code == 200


# def test_get_all_post():
#     response = client.post("/posts/all/", headers={"Authorization": f"Bearer {os.getenv('TOKEN')}"})
#     assert response.status_code == 200


# def test_delete_single_post():
#     response = client.delete(f"/posts/{post['key']}/", headers={"Authorization": f"Bearer {os.getenv('TOKEN')}"})
#     assert response.status_code == 200


# def test_add_new_response():
#     response = client.post(f"/posts/response/new/", data=NewResponse(**new_response).json(), headers={"Authorization": f"Bearer {os.getenv('TOKEN')}"})
#     assert response.status_code == 200


# def test_delete_response():
#     response = client.delete(f"/posts/{post['key']}/response/0/", headers={"Authorization": f"Bearer {os.getenv('TOKEN')}"})
#     assert response.status_code == 200


# def test_clean_the_post():
#     response = client.delete(f"/posts/delete/{post['key']}/", headers={"Authorization": f"Bearer {os.getenv('TOKEN')}"})
#     assert response.status_code == 200


# def test_clean_test_user():
#     response = client.delete(f"/users/{user['username']}/")
#     assert response.status_code == 200
