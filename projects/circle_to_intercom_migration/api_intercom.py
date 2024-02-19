# intercom API reference: https://developers.intercom.com/docs/references/rest-api/api.intercom.io/Articles/article/


import html
from typing import Optional

from api import call_api, load_config, render_json


class IntercomAPI:

    INTERCOM_API_KEY = load_config()["intercom"]["api_key"]
    INTERCOM_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {INTERCOM_API_KEY}",
    }

    INTERCOM_API_ROOT = "https://api.intercom.io"
    INTERCOM_COLLECTIONS = f"{INTERCOM_API_ROOT}/help_center/collections"
    INTERCOM_HELP_CENTERS = f"{INTERCOM_API_ROOT}/help_center/help_centers"
    INTERCOM_ARTICLES = f"{INTERCOM_API_ROOT}/articles"
    INTERCOM_ADMINS = f"{INTERCOM_API_ROOT}/admins"
    INTERCOM_TEAMS = f"{INTERCOM_API_ROOT}/teams"

    @staticmethod
    def html_unescape(l: list, key: str = "name"):
        """Apllies html.unescape on all values of a list of json objects, for a specific key"""
        for e in l:
            e[key] = html.unescape(e[key])
        return l

    @classmethod
    def api_get_collections(cls, render: bool = True):
        url = f"{cls.INTERCOM_COLLECTIONS}"

        response = call_api(url, "get", headers=cls.INTERCOM_HEADERS).json()
        res = {
            "type": response["type"],
            "data": response["data"],
            "total_count": response["total_count"],
            "total_pages": response["pages"]["total_pages"],
            "per_page": response["pages"]["per_page"],
        }
        while response["pages"].get("next", None) is not None:
            new_url = response["pages"]["next"]
            response = call_api(new_url, "get", headers=cls.INTERCOM_HEADERS).json()
            res["data"] += response["data"]

        ## escape the collection name
        res["data"] = IntercomAPI.html_unescape(res["data"], "name")

        if render:
            render_json(res)
        return res

    @classmethod
    def api_create_collection(
        cls, name: str, parent_id: Optional[int] = None, render: bool = True
    ):
        url = f"{cls.INTERCOM_COLLECTIONS}"
        payload = {"name": name}
        if parent_id is not None:
            payload["parent_id"] = parent_id
        response = call_api(url, "post", json=payload, headers=cls.INTERCOM_HEADERS)
        if render:
            render_json(response.json())
        return response.json()

    @classmethod
    def api_delete_collection(cls, coll_id: str, render: bool = True):
        url = f"{cls.INTERCOM_COLLECTIONS}/{coll_id}"
        response = call_api(url, "delete", headers=cls.INTERCOM_HEADERS)
        if render:
            render_json(response.json())
        return response.json()

    @classmethod
    def api_get_admins(cls, render: bool = True):
        url = f"{cls.INTERCOM_ADMINS}"
        response = call_api(url, "get", headers=cls.INTERCOM_HEADERS)
        if render:
            render_json(response.json())
        return response.json()

    @classmethod
    def api_get_help_centers(cls, render: bool = True):
        url = f"{cls.INTERCOM_HELP_CENTERS}"
        response = call_api(url, "get", headers=cls.INTERCOM_HEADERS)
        if render:
            render_json(response.json())
        return response.json()

    @classmethod
    def api_get_teams(cls, render: bool = True):
        url = f"{cls.INTERCOM_TEAMS}"
        response = call_api(url, "get", headers=cls.INTERCOM_HEADERS)
        if render:
            render_json(response.json())
        return response.json()

    @classmethod
    def api_get_articles(cls, render: bool = True):
        url = f"{cls.INTERCOM_ARTICLES}"
        response = call_api(url, "get", headers=cls.INTERCOM_HEADERS).json()
        res = {
            "type": response["type"],
            "data": response["data"],
            "total_count": response["total_count"],
            "total_pages": response["pages"]["total_pages"],
            "per_page": response["pages"]["per_page"],
        }
        while response["pages"].get("next", None) is not None:
            new_url = response["pages"]["next"]
            response = call_api(new_url, "get", headers=cls.INTERCOM_HEADERS).json()
            res["data"] += response["data"]

        ## escape the article title
        res["data"] = IntercomAPI.html_unescape(res["data"], "title")

        if render:
            render_json(res)
        return res

    @classmethod
    def api_create_article(
        cls,
        title: str,
        author_id: str,
        body: Optional[str],
        parent_id: Optional[str] = None,
        state: str = "published",
        render: bool = True,
    ):
        url = f"{cls.INTERCOM_ARTICLES}"
        payload = {
            "title": title,
            "author_id": author_id,
            "body": body,
            "parent_id": parent_id,
            "state": state,
        }
        response = call_api(url, "post", json=payload, headers=cls.INTERCOM_HEADERS)
        if response.status_code != 200:
            return response
        else:
            if render:
                render_json(response.json())
            return response.json()
