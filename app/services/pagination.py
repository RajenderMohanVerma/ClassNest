"""Helpers for keeping list filters intact while paginating."""

from urllib.parse import urlencode

RESERVED_PARAMS = {'page', 'per_page'}


def pagination_args(args, **overrides):
    """Return a query string of the active filters (without ``page``).

    Used together with ``partials/pagination.html`` so that sorting, searching
    and filtering survive a page change.
    """
    params = {
        key: value
        for key, value in args.items(multi=False)
        if key not in RESERVED_PARAMS and value not in ('', None)
    }
    for key, value in overrides.items():
        if value in ('', None):
            params.pop(key, None)
        else:
            params[key] = value
    return urlencode(params)


def page_link(base_args, page):
    query = pagination_args(base_args, page=page)
    return f'?{query}' if query else ''