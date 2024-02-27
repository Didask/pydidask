# circle API reference: https://api.circle.so/#98273257-cde7-44bc-bd45-5e0278d3acb0
# intercom API reference: https://developers.intercom.com/docs/references/rest-api/api.intercom.io/Articles/article/


import html
import sys
from pathlib import Path
from typing import Optional

sys.path.append("../..")
import requests
from dev.utils import RenderJSON, load_config, render_json
from requests.exceptions import HTTPError


def call_api(url: str, method: str, **kwargs):
    """
    Makes an API call using the specified HTTP method.

    Args:
    - url (str): The URL of the API endpoint.
    - method (str): The HTTP method to use (e.g., 'get', 'post', 'put', 'delete').
    - **kwargs: Arbitrary keyword arguments that are passed directly to requests.request.
      These can include parameters like 'data', 'json', 'headers', and 'timeout'.

    Returns:
    - response: The Response object returned by the requests call.

    Raises:
    - HTTPError: If the response contains an HTTP error status code.
    """
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Handle specific HTTP errors here
    except requests.exceptions.RequestException as err:
        print(
            f"Error during requests to {url}: {err}"
        )  # Handle other requests errors here
    finally:
        return response


class CircleAPI:

    CIRCLE_API_KEY = load_config()["circle"]["api_key"]
    CIRCLE_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CIRCLE_API_KEY}",
    }

    CIRCLE_URL_ROOT = "https://app.circle.so/api/v1"
    CIRCLE_URL_ME = f"{CIRCLE_URL_ROOT}/me"
    CIRCLE_URL_COMMUNITY = f"{CIRCLE_URL_ROOT}/communities"
    CIRCLE_URL_SPACE_GROUPS = f"{CIRCLE_URL_ROOT}/space_groups"
    CIRCLE_URL_SPACES = f"{CIRCLE_URL_ROOT}/spaces"
    CIRCLE_URL_POSTS = f"{CIRCLE_URL_ROOT}/posts"
    CIRCLE_URL_COURSE_LESSONS = f"{CIRCLE_URL_ROOT}/course_lessons"
    CIRCLE_URL_COURSE_SECTIONS = f"{CIRCLE_URL_ROOT}/course_sections"
    CIRCLE_URL_MEMBERS = f"{CIRCLE_URL_ROOT}/community_members"

    ID_COMMUNITY_DIDASK = 52148

    @classmethod
    def api_get_me(cls, render: bool = True):
        url = f"{cls.CIRCLE_URL_ME}"
        response = call_api(url, "get", headers=cls.CIRCLE_HEADERS)
        if render:
            render_json(response.json())
        return response.json()

    @classmethod
    def api_get_communities(cls, render: bool = True):
        url = f"{cls.CIRCLE_URL_COMMUNITY}"
        response = call_api(url, "get", headers=cls.CIRCLE_HEADERS)
        if render:
            render_json(response.json())
        return response.json()

    @classmethod
    def api_get_space_groups(
        cls, community_id: Optional[int] = None, render: bool = True
    ):
        if community_id is None:
            community_id = cls.ID_COMMUNITY_DIDASK
        url = f"{cls.CIRCLE_URL_SPACE_GROUPS}?community_id={community_id}"
        response = call_api(url, "get", headers=cls.CIRCLE_HEADERS)
        if render:
            render_json(response.json())
        return response.json()

    @classmethod
    def api_get_spaces(cls, community_id: Optional[int] = None, render: bool = True):
        if community_id is None:
            community_id = cls.ID_COMMUNITY_DIDASK
        url = f"{cls.CIRCLE_URL_SPACES}?community_id={community_id}"
        response = call_api(url, "get", headers=cls.CIRCLE_HEADERS)
        if render:
            render_json(response.json())
        return response.json()

    @classmethod
    def api_get_posts(
        cls,
        community_id: Optional[int] = None,
        space_id: Optional[int] = None,
        space_group_id: Optional[int] = None,
        render: bool = True,
    ):
        if community_id is None:
            community_id = cls.ID_COMMUNITY_DIDASK
        url = f"{cls.CIRCLE_URL_POSTS}?community_id={community_id}&per_page=100"
        if space_group_id is not None:
            url += f"&space_group_id={space_id}"
        if space_id is not None:
            url += f"&space_id={space_id}"

        page_num = 1
        output = list()
        while True:
            url_page = f"{url}&page={page_num}"
            response = call_api(url_page, "get", headers=cls.CIRCLE_HEADERS)
            if len(response.json()) == 0:
                break
            output += response.json()
            page_num += 1
        if render:
            render_json(output)
        return output

    @classmethod
    def api_get_course_lessons(
        cls, community_id: Optional[int] = None, render: bool = True
    ):
        if community_id is None:
            community_id = cls.ID_COMMUNITY_DIDASK
        url = f"{cls.CIRCLE_URL_COURSE_LESSONS}?community_id={community_id}"
        response = call_api(url, "get", headers=cls.CIRCLE_HEADERS)
        if render:
            render_json(response.json())
        return response.json()

    @classmethod
    def api_get_course_lessons(
        cls, community_id: Optional[int] = None, render: bool = True
    ):
        if community_id is None:
            community_id = cls.ID_COMMUNITY_DIDASK
        url = f"{cls.CIRCLE_URL_COURSE_LESSONS}?community_id={community_id}"
        response = call_api(url, "get", headers=cls.CIRCLE_HEADERS)
        if render:
            render_json(response.json())
        return response.json()

    @classmethod
    def api_get_course_sections(
        cls, community_id: Optional[int] = None, render: bool = True
    ):
        if community_id is None:
            community_id = cls.ID_COMMUNITY_DIDASK
        url = f"{cls.CIRCLE_URL_COURSE_SECTIONS}?community_id={community_id}"
        response = call_api(url, "get", headers=cls.CIRCLE_HEADERS)
        if render:
            render_json(response.json())
        return response.json()

    @classmethod
    def api_get_members(cls, render: bool = True):
        url = f"{cls.CIRCLE_URL_MEMBERS}?per_page=100"
        response = call_api(url, "get", headers=cls.CIRCLE_HEADERS)
        if render:
            render_json(response.json())
        return response.json()


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

    @classmethod
    def api_delete_article(cls, article_id: str, render: bool = True):
        url = f"{cls.INTERCOM_ARTICLES}/{article_id}"
        response = call_api(url, "delete", headers=cls.INTERCOM_HEADERS)
        if render:
            render_json(response.json())
        return response.json()
