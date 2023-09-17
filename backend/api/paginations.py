from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10

    def get_page_size(self, request):
        page_size = int(request.query_params.get('limit', self.page_size))

        return max(page_size, 1)
