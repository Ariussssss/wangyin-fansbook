# coding=utf-8

from ebooklib import epub
import requests
import os
import base64
from bs4 import BeautifulSoup

if __name__ == "__main__":
    book = epub.EpubBook()
    book.set_identifier("sample123456")
    book.set_title("Wangyin Blog")
    book.set_language("zh")
    book.set_cover("cover.png", open('./cover.png', 'rb').read())
    book.add_author("Wangyin")
    base = "https://www.yinwang.org/"
    total = BeautifulSoup(requests.get(base).text, "html.parser")
    l = list(total.find_all("li", class_="list-group-item title"))
    toc_list = list()
    spine_list = ["nav"]

    for a in l:
        a_el = a.find("a")
        date_el = a.find("div", class_="date")
        file_name = f"./cache/{a_el.text}.html"
        if os.path.isfile(file_name):
            print(a_el["href"], a_el.text, "caching")
            res = open(file_name, "r").read()
        else:
            print(a_el["href"], a_el.text, "fetching")
            res = requests.get(base + a_el["href"]).text
            open(file_name, "w").write(res)
        article_html = BeautifulSoup(res, "html.parser")
        body = article_html.find("div", class_="inner")
        if not body or "c-sharp-disposable" in a_el["href"]:
            continue
        chapter = epub.EpubHtml(
            title=a_el.text, file_name=f"{a_el.text}.xhtml", lang="zh"
        )
        images = article_html.find_all("img")
        if images and len(images) > 0:
            for i in images:
                link = i.get('src')
                image_path = f'./cache/images/{os.path.basename(link)}'
                if not os.path.isfile(image_path):
                    with open(image_path, "wb") as f:
                        try:
                            f.write(requests.get(link).content)
                        except:
                            f.write(b'')
                with open(image_path, "rb") as f:
                    t = f.read() 
                    if t:
                        i['src'] = f'data:image/png;base64,{str(base64.b64encode(t).decode())}'
                    else:
                        i['src'] = ''
        chapter.content = str(date_el) + "".join(
            list(
                map(
                    lambda a: str(a),
                    body.contents,
                )
            )
        )
        spine_list.append(chapter)
        book.add_item(chapter)
        toc_list.append(chapter)

    # add navigation files
    book.toc = tuple(toc_list)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define css style
    style = """
@namespace epub "http://www.idpf.org/2007/ops";
body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
}
h2 {
     text-align: left;
     text-transform: uppercase;
     font-weight: 200;     
}
ol {
        list-style-type: none;
}
ol > li:first-child {
        margin-top: 0.3em;
}
nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}
nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
}
"""

    # add css file
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style,
    )
    book.add_item(nav_css)

    # create spine
    book.spine = spine_list

    # create epub file
    epub.write_epub("wangyin-blog.epub", book, {})
