from typing import Dict, List


class QuerysetTransformerMixin:
    def transform_queryset(self, queryset) -> List[Dict]:
        result: List[Dict] = []

        if not queryset:
            return result

        keys: List[str] = [
            key for key in queryset[0].__dict__.keys() if not key.startswith("_")
        ]

        for item in queryset:
            d = {}

            for key in keys:
                d[key] = item.__dict__[key]

            result.append(d)

        return result
