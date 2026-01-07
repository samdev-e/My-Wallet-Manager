from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# Example custom pagination class with additional metadata in response.
# to use, set DEFAULT_PAGINATION_CLASS in REST_FRAMEWORK settings to this class.    
# in settings.py: (REST_FRAMEWORK dictionary)
# 'DEFAULT_PAGINATION_CLASS': 'backend.api.pagination.StandardResultsSetPagination',


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'  # allows frontend to override
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'total_items': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page_size,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
