import coreschema
from rest_framework.filters import BaseFilterBackend
import coreapi
from rest_framework import filters


class QueryParamBasedFilter(filters.BaseFilterBackend):
    def get_search_fields(self, view, request):
        """
        Search fields are obtained from the view, but the request is always
        passed to this method. Sub-classes can override this method to
        dynamically change the search fields based on request content.
        """
        return getattr(view, 'query_params', None)

    def get_schema_fields(self, view):
        sf_result = self.get_search_fields(view, None)
        results = []
        i =0
        for field in sf_result:

            newField = None
            if field['type'].upper() =='float'.upper():
                newField = coreapi.Field(
                    name=field['name'],
                    required=False, location='query',
                    schema=coreschema.Number(
                        title=field['name'],
                        description=field['description'] if 'description' in field else None
                    )
                )
            elif field['type'].upper =='int'.upper():
                newField = coreapi.Field(
                    name=field['name'],
                    required=False, location='query',
                    schema=coreschema.Integer(
                        title=field['name'],
                        description=field['description'] if 'description' in field else None
                    )
                )
            else:
                newField = coreapi.Field(
                    name=field['name'],
                    required=False, location='query',
                    schema=coreschema.String(
                        title=field['name'],
                        description=field['description'] if 'description' in field else None
                    )
                )
            if newField is not None:
                results.append(newField)

        return results

