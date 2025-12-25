from celery.worker.state import requests

CORE_API = "http://127.0.0.1:8001/api"

def get_external_user(token):
    response = requests.get(
        f"{CORE_API}/profile/me/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    if response.status_code != 200:
        return None

    return response.json()
