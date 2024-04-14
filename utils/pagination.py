from rest_framework.pagination import PageNumberPagination


class PageNumberPaginationManual(PageNumberPagination):

    # page_size = 10  # 默认情况下，每一页显示的条数为10
    max_page_size = 50
    # page_query_param = 'page'
    page_size_query_param = 'size'
    page_query_description = '第几页'
    page_size_query_description = '每页几条'

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data['total_pages'] = self.page.paginator.num_pages
        response.data['current_page_num'] = self.page.number
        return response