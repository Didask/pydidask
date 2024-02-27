import html

import pandas as pd
from api_circle import CircleAPI
from api_intercom import IntercomAPI
from tqdm import tqdm


class MigrateCirclePostsToIntercom:

    DEFAULT_INTERCOM_AUTHOR = "Support technique"

    def __init__(self):
        self.space_groups = CircleAPI.api_get_space_groups(render=False)
        self.spaces = CircleAPI.api_get_spaces(render=False)
        self.df_collections_lookup = (
            pd.DataFrame(
                {
                    "name": [s["name"] for s in self.space_groups]
                    + [s["name"] for s in self.spaces],
                    "parent_name": [None] * len(self.space_groups)
                    + [s["space_group_name"] for s in self.spaces],
                    "circle_id": [s["id"] for s in self.space_groups]
                    + [str(s["id"]) for s in self.spaces],
                    "circle_parent_id": [None] * len(self.space_groups)
                    + [str(s["space_group_id"]) for s in self.spaces],
                    "intercom_id": None,
                    "intercom_parent_id": None,
                }
            )
            .sort_values("parent_name", ascending=True, na_position="first")
            .set_index("name")
        )

        self.find_intercom_id_for_collections()

    def find_intercom_id_for_collections(self):
        colls = IntercomAPI.api_get_collections(render=False)["data"]
        colls_name = [
            c["name"] for c in colls if c["name"] in self.df_collections_lookup.index
        ]
        colls_idx = [
            c["id"] for c in colls if c["name"] in self.df_collections_lookup.index
        ]

        ## set intercom id
        self.df_collections_lookup.loc[colls_name, "intercom_id"] = colls_idx

        ## set intercom parent id
        for i in range(len(self.df_collections_lookup)):
            coll_name = self.df_collections_lookup.index[i]
            parent_name = self.df_collections_lookup.iloc[i]["parent_name"]
            if parent_name is not None:
                self.df_collections_lookup.loc[coll_name, "intercom_parent_id"] = (
                    self.df_collections_lookup.loc[parent_name, "intercom_id"]
                )

    @classmethod
    def delete_all_intercom_collections(
        cls, are_you_sure: bool = False, display_progress: bool = True
    ):
        if not are_you_sure:
            raise ValueError('You have to set "are_you_sure" to True')
        collections_id = [
            e["id"]
            for e in IntercomAPI.api_get_collections(render=False)["data"]
            if e["parent_id"] is None
        ]
        if display_progress:
            collections_id = tqdm(collections_id)
        for coll_id in collections_id:
            IntercomAPI.api_delete_collection(coll_id=coll_id, render=False)

    @classmethod
    def delete_all_intercom_articles(
        cls, are_you_sure: bool = False, display_progress: bool = True
    ):
        if not are_you_sure:
            raise ValueError('You have to set "are_you_sure" to True')
        articles_id = [
            e["id"] for e in IntercomAPI.api_get_articles(render=False)["data"]
        ]
        if display_progress:
            articles_id = tqdm(articles_id)
        for a_id in articles_id:
            IntercomAPI.api_delete_article(article_id=a_id, render=False)

    def migrate_root_collections(self):
        root_collections = self.df_collections_lookup.index[
            self.df_collections_lookup["parent_name"].apply(lambda x: x is None)
        ]
        intercom_collections_created = [
            IntercomAPI.api_create_collection(n, render=False) for n in root_collections
        ]

        ## add intercom IDs to lookup table
        idx = [html.unescape(e["name"]) for e in intercom_collections_created]
        intercom_id = [e["id"] for e in intercom_collections_created]
        self.df_collections_lookup.loc[idx, "intercom_id"] = intercom_id

        ## add parent ID for intercom sub collections
        for i in range(len(self.df_collections_lookup)):
            coll_name = self.df_collections_lookup.index[i]
            parent_name = self.df_collections_lookup.iloc[i]["parent_name"]
            if parent_name is not None:
                self.df_collections_lookup.loc[coll_name, "intercom_parent_id"] = (
                    self.df_collections_lookup.loc[parent_name, "intercom_id"]
                )
        return intercom_collections_created

    def migrate_sub_collections(self):
        ## create sub collections
        sub_collections_name = self.df_collections_lookup.index[
            self.df_collections_lookup["parent_name"].apply(lambda x: x is not None)
        ]
        sub_collections_parent_id = self.df_collections_lookup.loc[
            sub_collections_name, "intercom_parent_id"
        ]
        intercom_sub_collections_created = [
            IntercomAPI.api_create_collection(name=n, parent_id=i, render=False)
            for (n, i) in sub_collections_parent_id.items()
        ]

        ## add intercom ID
        for e in intercom_sub_collections_created:
            self.df_collections_lookup.loc[html.unescape(e["name"]), "intercom_id"] = e[
                "id"
            ]
        return intercom_sub_collections_created

    def migrate_all_collections(self):
        out1 = self.migrate_root_collections()
        out2 = self.migrate_sub_collections()
        out = out1 + out2
        return out

    def migrate_all_articles(self, display_progress=False):

        ## get intercom admin IDs (authors are admins)
        intercom_admins = IntercomAPI.api_get_admins(render=False)["admins"]
        intercom_admins_id_lookup = {
            admin["name"]: admin["id"] for admin in intercom_admins
        }

        ## get Circle posts
        posts = CircleAPI.api_get_posts(render=False)
        res = list()
        if display_progress:
            posts = tqdm(posts)
        for p in posts:
            print(p["name"])
            r = IntercomAPI.api_create_article(
                title=p["name"],
                body=p["body"]["body"],
                author_id=intercom_admins_id_lookup.get(
                    p["user_name"],
                    intercom_admins_id_lookup[self.DEFAULT_INTERCOM_AUTHOR],
                ),
                state="published",
                parent_id=self.df_collections_lookup.loc[
                    p["space_name"], "intercom_id"
                ],
                render=False,
            )
            res.append(r)
        return res
