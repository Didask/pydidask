import html2text


def convert_html_to_text(body_html: str, include_links: bool = True) -> str:
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = not include_links
    body_md = text_maker.handle(body_html)
    return body_md
