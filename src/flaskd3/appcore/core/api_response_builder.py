from flask import jsonify
from flask.helpers import make_response

from flaskd3.common.utils.json_utils import make_jsonify_ready


class ApiResponseBuilder(object):
    @staticmethod
    def build_success_response_from_aggregate(aggregate, schema):
        data = schema(unknown="EXCLUDE").dump(aggregate.data())
        response = make_jsonify_ready(
            dict(
                data=data,
                errors=list(),
                meta=dict(),
                resourceVersion=aggregate.get_latest_version(),
            )
        )
        return make_response(jsonify(response), 200)

    @staticmethod
    def build_success_response_from_aggregates(aggregates, schema, meta=None):
        data = []

        for aggregate in aggregates:
            data.append(schema(unknown="EXCLUDE").dump(aggregate.data()))

        if not meta:
            meta = dict()
        else:
            data_len = len(data)
            meta = dict(
                start=meta.start,
                limit=meta.limit,
                end=meta.start + data_len,
                count=data_len,
            )
        response = make_jsonify_ready(dict(data=data, errors=list(), meta=meta))
        return make_response(jsonify(response), 200)

    @staticmethod
    def build_success_response_from_data(data_obj, schema=None, version=None, many=False, meta=None):
        if data_obj:
            data_dict = dict(
                data=schema(unknown="EXCLUDE").dump(data_obj, many=many),
                errors=list(),
                meta=meta.to_dict() if meta else dict(),
            )
        else:
            data_dict = dict()
        if version:
            data_dict["resourceVersion"] = version
        response = make_jsonify_ready(data_dict)
        return make_response(jsonify(response), 200)

    @staticmethod
    def build_raw(data, schema):
        data = schema(unknown="EXCLUDE").dump(data)
        return make_response(jsonify(data), 200)

    @staticmethod
    def build(status_code, data=None, errors=None, meta=None, resource_version=None):
        if not meta:
            meta = dict()
        if data is None:
            data = dict()
        if not errors:
            errors = list()
        response = dict(data=data, errors=errors, meta=meta)
        if resource_version:
            response["resource_version"] = resource_version
        response = make_jsonify_ready(response)
        response = make_response(jsonify(response), status_code)
        return response
