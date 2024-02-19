# circle API reference: https://api.circle.so/#98273257-cde7-44bc-bd45-5e0278d3acb0

from typing import Optional

from api import call_api, load_config, render_json


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
