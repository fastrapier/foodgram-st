from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Пагинация с возможностью указывать количество объектов через параметр 'limit'.
    """
    page_size_query_param = 'limit'
    page_size = 6
