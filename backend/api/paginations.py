from rest_framework.pagination import PageNumberPagination

from .constants import PAGE_SIZE, MIN_PAGE_SIZE


class CustomPagination(PageNumberPagination):
    page_size = PAGE_SIZE

    def get_page_size(self, request):
        page_size = int(request.query_params.get('limit', self.page_size))

        return max(page_size, MIN_PAGE_SIZE)
