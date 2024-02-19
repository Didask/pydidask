import json
import subprocess
import uuid
from enum import Enum
from pathlib import Path

import yaml
from IPython.core.display import HTML, display
from pymongo.mongo_client import MongoClient
from tqdm import tqdm

PATH_CONFIG = Path(__file__).parent / "../config/config.yml"


### YAML CONFIG LOADING
def load_config(path_config=PATH_CONFIG):
    with open(path_config, "r") as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)


CONFIG = load_config()


### URI BUILDER
def build_mongodb_uri(env, with_credentials=True, config=CONFIG):
    username = config["mongodb"]["username"]
    password = config["mongodb"]["password"]
    url = config["mongodb"][f"cluster_url_{env}"]

    if env in ["production", "backup"]:
        credentials = f"{username}:{password}@" if with_credentials else ""
        uri = f"mongodb+srv://{credentials}{url}"
    elif env == "local":
        uri = f"mongodb://{url}"
    else:
        raise ValueError("env should be production, backup or local")
    return uri


def build_mongo_client(env, config=CONFIG):
    uri = build_mongodb_uri(env, config)
    return MongoClient(uri)


MONGO_CLIENTS = {
    "production": build_mongo_client("production"),
    "backup": build_mongo_client("backup"),
    "local": build_mongo_client("local"),
}


def get_mongo_client(env):
    return MONGO_CLIENTS[env]


PATH_MONGO_LOCAL = Path(CONFIG["mongodb"]["path_local"])
PATH_MONGO_LOCAL_DATA = PATH_MONGO_LOCAL / "data"
PATH_MONGO_LOCAL_DB = PATH_MONGO_LOCAL_DATA / "db"
PATH_MONGO_LOCAL_ARCHIVES = PATH_MONGO_LOCAL_DATA / "archives"


###############


### test_mongo_client
def test_mongo_client(mongo_client, print_ok=True):
    try:
        mongo_client.admin.command("ping")
        if print_ok:
            print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)


def get_mongo_version(mongo_client):
    print(mongo_client.server_info()["version"])


### pull database from remote cluster to local
def dump_database(
    env,
    db_name,
    path_local_archives=PATH_MONGO_LOCAL_ARCHIVES,
    verbose=False,
    debug=False,
    config=CONFIG,
):
    """Dumps a database from the remote cluster to the local archive"""

    uri = build_mongodb_uri(env=env, with_credentials=False)
    username = config["mongodb"]["username"]
    password = config["mongodb"]["password"]

    command = [
        "mongodump",
        "--uri",
        str(uri),
        "--username",
        username,
        "--password",
        password,
        "--db",
        db_name,
        "--out",
        str(path_local_archives),
    ]

    if debug:
        print("command: " + " ".join(command))
    try:
        output = subprocess.run(command, capture_output=True, check=True)
        error = None
    except subprocess.CalledProcessError as e:
        output = None
        error = e
    finally:
        if verbose:
            print(f"- dumping db '{db_name}'" + (error is not None) * " (ERROR)")
        return (output, error)


def dump_databases(
    env: str,
    db_name: str | list[str] | None = None,
    path_local_archives=PATH_MONGO_LOCAL_ARCHIVES,
    verbose=False,
    debug=False,
    config=CONFIG,
):
    if isinstance(db_name, str):
        db_name = [db_name]
    if db_name is None:
        db_name = list_database_names(MONGO_CLIENTS[env])

    outputs = list()
    for dbn in tqdm(db_name):
        out = dump_database(env, dbn, path_local_archives, verbose, debug, config)
        outputs.append(out)
    return outputs


def restore_database(
    db_name,
    path_local_archives=PATH_MONGO_LOCAL_ARCHIVES,
    mongo_client_local=MONGO_CLIENTS["local"],
    verbose=False,
    debug=False,
):
    """Restores a database on the local MongoDB server"""
    # first, drop the database if it already exists
    # mongo_client_local.drop_database(db_name)

    command = [
        "mongorestore",
        "--drop",
        "--db",
        db_name,
        str(path_local_archives / db_name),
    ]

    if debug:
        print(" ".join(command))
    try:
        output = subprocess.run(command, capture_output=True, check=True)
        error = None
    except subprocess.CalledProcessError as e:
        output = None
        error = e
    finally:
        if verbose:
            print(f"- restoring db '{db_name}'" + (error is not None) * " (ERROR)")
        return (output, error)


def restore_databases(
    db_name: str | list[str] | None = None,
    path_local_archives=PATH_MONGO_LOCAL_ARCHIVES,
    mongo_client_local=MONGO_CLIENTS["local"],
    verbose=False,
    debug=False,
):
    if isinstance(db_name, str):
        db_name = [db_name]
    if db_name is None:
        db_name = list_database_names(MONGO_CLIENTS[env])

    outputs = list()
    for dbn in tqdm(db_name):
        out = restore_database(dbn, path_local_archives, verbose, debug)
        outputs.append(out)
    return outputs


def restore_databases_batch(
    path_local_archives=PATH_MONGO_LOCAL_ARCHIVES, verbose=False, debug=False
):
    command = ["mongorestore", "--drop", str(path_local_archives)]

    if debug:
        print(" ".join(command))
    try:
        output = subprocess.run(command, capture_output=True, check=True)
        error = None
    except subprocess.CalledProcessError as e:
        output = None
        error = e
    finally:
        return (output, error)


def pull_database(
    env,
    db_name,
    path_local_archives=PATH_MONGO_LOCAL_ARCHIVES,
    verbose=False,
    debug=False,
    config=CONFIG,
):
    """Dumps a database from remote cluster and restores it to local
    corresponds to: dump_database + restore_database
    """
    out_dump = dump_database(env, db_name, path_local_archives, verbose, debug, config)
    out_restore = restore_database(db_name, path_local_archives, verbose, debug)
    return [out_dump, out_restore]


def pull_databases(
    env,
    db_name,
    path_local_archives=PATH_MONGO_LOCAL_ARCHIVES,
    verbose=False,
    debug=False,
    config=CONFIG,
    restore_in_batch=False,
):
    if isinstance(db_name, str):
        db_name = [db_name]
    if db_name is None:
        db_name = list_database_names(MONGO_CLIENTS[env])

    outputs = list()

    ## dump everything then restore all archives in batch (faster)
    if restore_in_batch:
        for dbn in tqdm(db_name):
            out_dump = dump_database(
                env, dbn, path_local_archives, verbose, debug, config
            )
            outputs.append(out_dump)
        out_restore = restore_databases_batch()
        outputs.append(out_restore)
        return outputs

    ## dump then restore databases one by one
    else:
        for dbn in tqdm(db_name):
            out_dump = dump_database(
                env, dbn, path_local_archives, verbose, debug, config
            )
            out_restore = restore_database(dbn, path_local_archives, verbose, debug)
            outs = [out_dump, out_restore]
            outputs.append(outs)
        return outputs


### list database names
def get_all_database_names(mongo_client):
    tmp = list(mongo_client.list_databases())
    return [e["name"] for e in tmp]


def get_customers_database_infos(mongo_client):
    db_main = mongo_client["main"]

    selected_fields = [
        "dbUri",
        "name",
        "hostnames",
        "accountsLimit",
        "features",
        "licensePeriods",
        "licenseModel",
        "renewalDate",
    ]
    workspaces = [
        {k: v for (k, v) in e.items() if k in selected_fields}
        for e in db_main["Workspace"].find()
    ]
    for w in workspaces:
        w["dbName"] = w["dbUri"].split("/")[-1]
        w["hostnames"] = w["hostnames"][0]

    return workspaces


def get_customers_database_names(mongo_client):
    tmp = get_customers_database_infos(mongo_client)
    return [e["dbName"] for e in tmp]


def print_stderr(out):
    print(out.stderr.decode("utf-8"))


# ### JSON FORMATTING


class RenderJSON(object):
    def __init__(self, json_data):
        if isinstance(json_data, dict):
            self.json_str = json.dumps(json_data)
        else:
            self.json_str = json_data
        self.uuid = str(uuid.uuid4())
        # This line is missed out in most of the versions of this script across the web, it is essential for this to work interleaved with print statements
        self._ipython_display_()

    def _ipython_display_(self):
        display(
            HTML(
                '<div id="{}" style="height: auto; width:100%;"></div>'.format(
                    self.uuid
                )
            )
        )
        display(
            HTML(
                """<script>
        require(["https://rawgit.com/caldwell/renderjson/master/renderjson.js"], function() {
          renderjson.set_show_to_level(1)
          document.getElementById('%s').appendChild(renderjson(%s))
        });</script>
        """
                % (self.uuid, self.json_str)
            )
        )


def render_json(obj):
    if isinstance(obj, list):
        for o in obj:
            _ = RenderJSON(o)
    else:
        _ = RenderJSON(obj)


### PUBLICATIONS
COLL_PUBLICATIONS = "course"


class PUB_TYPE(Enum):
    COURSE = "Publication.Course"
    SINGLE_MODULE = "Publication.SingleModule"
    ADAPTIVE = "Publication.Adaptive"


def get_pubs(client, db_name):
    # input: db_name
    # output: list of all publication
    res = list(client[db_name][COLL_PUBLICATIONS].find({}))
    for pub in res:
        pub["db_name"] = db_name
    return res


def get_learners_group(client, db_name):
    # input: db_name
    # output: list of all publication
    res = list(client[db_name]["learners_group"].find({}))
    for pub in res:
        pub["db_name"] = db_name
    return res


def get_pub_type(pub):
    # input: list of publications (dict)
    # the publication type
    return pub["_cls"]


def get_pub_name(pub):
    return pub["name"]


def is_pub_category(pub, cat: PUB_TYPE):
    return pub["_cls"] == cat.value


def get_pub_chapters(pub):
    # input: list of publications (dict)
    # the publication type
    return


def get_pub_modules(pub):
    # input: list of publications (dict)
    # the publication type
    modules = list()


def cast_to_string(obj):
    if isinstance(obj, dict):
        return {key: cast_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [cast_to_string(item) for item in obj]
    else:
        return str(obj)


def render_json(d, return_res=False):
    e = cast_to_string(d)
    r = RenderJSON(e)
    if return_res:
        return r


def render_json_random(l):
    i = random.choice(range(len(l)))
    render_json(l[i])


from pywaffle import Waffle


def plot_waffle(cats, vals, title, is_pct):
    pal_ = list(sns.color_palette(palette="plasma_r", n_colors=len(cats)).as_hex())

    fig = plt.figure(
        FigureClass=Waffle,
        rows=20,
        columns=50,
        values=vals,
        colors=pal_,
        labels=[f"{c} ({str(round(v))+' %'*is_pct})" for (c, v) in zip(cats, vals)],
        figsize=(15, 6),
        legend={"loc": "upper right", "fontsize": 15},
    )
    plt.title(title, fontsize=20, pad=20)
    plt.tight_layout()
    plt.show()


def plot_treemap(cats, vals, title, is_pct=False):
    fig = px.treemap(
        names=[f"{c} ({round(v)}{" % "*is_pct})" for (c, v) in zip(cats, vals)],
        parents=[""] * len(cats),
        values=vals,
    )
    fig.update_traces(root_color="white", textposition="middle center", legend="legend")
    fig.update_layout(
        title=title,
        margin=dict(t=50, l=25, r=25, b=25),
        font=dict(size=20),
        title_x=0.5,
        title_y=0.95,
    )

    fig.update_layout(showlegend=True)
    fig.show()


def plot_proportion_bar(cats, vals, title, is_pct=False, show_legend=True):
    txt = [f"{c} ({str(round(v)) + is_pct*' %'})" for (c, v) in zip(cats, vals)]
    fig = px.bar(y=[""] * len(cats), x=vals, color=cats, orientation="h", text=txt)
    fig.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    fig.update_xaxes(visible=False, showticklabels=False)
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_layout(title=dict(text=title, font=dict(size=30), x=0.4, y=0.95))
    fig.update_layout(legend_title=None, showlegend=show_legend)
    fig.update_traces(insidetextanchor="middle")
    fig.update_traces(width=0.5)
    fig.show()
