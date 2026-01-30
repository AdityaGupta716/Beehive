from flask import request

def parse_pagination_params(default_page=1, default_size=12, max_size=50):
    try:
        page = int(request.args.get('page', default_page))
    except (ValueError, TypeError):
        page = default_page
    try:
        page_size = int(request.args.get('page_size', default_size))
    except (ValueError, TypeError):
        page_size = default_size

    page = max(1, page)
    page_size = min(max(1, page_size), max_size)

    return page, page_size
