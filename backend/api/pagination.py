from rest_framework import pagination


class FoodgramPagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 6
