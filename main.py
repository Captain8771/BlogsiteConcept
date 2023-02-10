import random

import quart as q
import os

app = q.Quart(__name__)
app.blog_cache = {}


class Constants:
    ip = "127.0.0.1"
    port = 8771
    secure = False
    domain = f"http{'s' if secure else ''}://{ip}:{port}"


class BlogMeta:
    def __init__(self, mdfile: str, filename: str = "error"):
        self.filename = filename.split("/")[-1]
        self.content = mdfile[mdfile.find("-->\n") + 4:]
        mdfile = mdfile[mdfile.find("<!--META"):mdfile.find("-->")]
        mdfile = mdfile.split("\n")
        mdfile = mdfile[1:len(mdfile) - 1]
        for line in mdfile:
            name = line.split(":")[0]
            value = line.split(":")[1:len(line.split(":"))][0].strip()
            setattr(self, name, value)


async def gen_preview(blog: BlogMeta):
    if getattr(blog, "preview", False):
        return blog.preview  # type: ignore
    else:
        con = blog.content
        con = con[con.find("<!--START content-->") + len("<!--START content-->"):]
        con = con.replace("\n", "  ")
        return con[:25].strip(" ") + "..."


@app.get("/")
async def home():
    return await q.render_template("home.html.jinja2", C=Constants)


@app.get("/blog")
async def blog():
    blogs = [f for f in os.listdir("./blogs") if not f.startswith("404")]
    blogMetas = []
    for blog in blogs:
        with open(f"./blogs/{blog}", "r") as f:
            blogMetas.append(BlogMeta(f.read(), f.name))

    return await q.render_template("bloglist.html.jinja2", C=Constants, blogs=blogMetas, gen_preview=gen_preview)


@app.get("/blog/<blog>")
async def gblog(blog: str):
    try:
        with open(f"blogs/{blog}", "r") as f:
            return await q.render_template("blog.html.jinja2", C=Constants, BlogMeta=BlogMeta(f.read(), f.name))
    except FileNotFoundError:
        with open(f"blogs/404-{random.randint(random.choice([1, 2, 2, 2, 2]), 4)}.md", "r") as f:
            return await q.render_template("blog.html.jinja2", C=Constants, BlogMeta=BlogMeta(f.read(), f.name))


@app.get("/assets/<path:asset>")
async def get_asset(asset):
    return await q.send_from_directory("./assets", asset)


if __name__ == "__main__":
    app.run(Constants.ip, port=Constants.port)
