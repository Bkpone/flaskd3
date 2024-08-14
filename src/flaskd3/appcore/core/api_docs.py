import inspect

from apispec import APISpec
from apispec.exceptions import DuplicateComponentNameError
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flasgger import Swagger
from marshmallow import Schema

from flaskd3.appcore.schema.schema_manager import SchemaManager


ma_plugin = MarshmallowPlugin(schema_name_resolver=lambda schema: schema.__class__.__name__)


def get_swagger_doc_string(
    request_type,
    tag,
    operation_id,
    request_schema,
    response_schema,
    parameter_defs=None,
    description="API request",
    request_description="Request Payload",
    response_description="Response Payload",
    response_many=False,
    request_version=False,
    request_many=False,
    security=None,
    headers=None
):
    swagger_dict = dict()
    if security:
        swagger_dict["security"] = list()
        for entry in security:
            swagger_dict["security"].append(entry)
    parameters = []
    if headers:
        parameters.extend(headers)
    if parameter_defs:
        if inspect.isclass(parameter_defs) and issubclass(parameter_defs, Schema):
            for key, field in parameter_defs._declared_fields.items():
                parameters.append(
                    {
                        "name": key,
                        "in": "query",
                        "required": field.required,
                        "schema": {"type": "string"},
                    }
                )
        else:
            for parameter_def in parameter_defs:
                parameters.append(
                    {
                        "name": parameter_def["name"],
                        "in": parameter_def["loc"],
                        "required": parameter_def["required"],
                        "schema": {"type": parameter_def["item_type"]},
                    }
                )
    swagger_dict["parameters"] = parameters
    if response_many:
        response_data = {
            "type": "array",
            "items": {"$ref": "#/components/schemas/{}".format(response_schema.__name__)},
        }
    else:
        response_data = {"$ref": "#/components/schemas/{}".format(response_schema.__name__)} if response_schema else None

    if request_type in ["POST", "PUT", "PATCH"] and request_schema is not None:
        if request_many:
            request_data = {
                "type": "array",
                "items": {"$ref": "#/components/schemas/{}".format(request_schema.__name__)},
            }
        else:
            request_data = {"$ref": "#/components/schemas/{}".format(request_schema.__name__)}
        swagger_dict["requestBody"] = {
            "description": request_description,
            "required": True,
            "content": {"application/json": {"schema": {"type": "object", "properties": {"data": request_data}}}},
        }
        if request_version:
            swagger_dict["requestBody"]["content"]["application/json"]["schema"]["properties"]["resourceVersion"] = dict(type="integer")
    swagger_dict.update(
        {
            "deprecated": False,
            "operationId": operation_id,
            "tags": [tag],
            "description": description,
            "responses": {
                "200": {
                    "description": response_description,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "resourceVersion": "Integer",
                                    "data": response_data,
                                    "meta": {
                                        "type": "object",
                                        "additionalProperties": {},
                                    },
                                    "errors": {
                                        "type": "object",
                                        "items": {"$ref": "#/components/schemas/ApiErrorSchema"},
                                    },
                                },
                            }
                        }
                    },
                }
            },
        }
    )
    return swagger_dict


def get_swagger_post_string(domain, request_schema, response_schema, operation_id):
    return get_swagger_doc_string(
        request_type="POST",
        tag=domain,
        operation_id=operation_id,
        description="Create a new entity",
        request_description="request payload",
        response_description="The new object",
        request_schema=request_schema,
        response_schema=response_schema,
        response_many=False,
    )


def get_swagger_get_many_string(tag, request_schema, response_schema, operation_id):
    return get_swagger_doc_string(
        request_type="GET",
        tag=tag,
        operation_id=operation_id,
        description="Get filtered entities",
        request_description="request payload",
        response_description="The filtered entities",
        request_schema=request_schema,
        response_schema=response_schema,
        response_many=True,
    )


def setup_schema_definition(spec):
    schema_map = SchemaManager.get_schema_map()
    found_schemas = set()
    for name, schema_info in schema_map.items():
        try:
            schema_name = schema_info.class_obj.__name__
            if schema_name in found_schemas:
                continue
            found_schemas.add(schema_name)
            spec.components.schema(name, schema=schema_info.class_obj)
        except DuplicateComponentNameError:
            continue


def setup_paths(spec, api_module):
    for name, obj in inspect.getmembers(api_module):
        if inspect.isfunction(obj):
            spec.path(view=obj)


def init_docs(app, app_name, api_module_path, advanced_options):
    ctx = app.test_request_context()
    ctx.push()

    app.config["SWAGGER"] = {
        "title": app_name,
        "uiversion": 3,
        "doc_expansion": "none",
        "specs_route": "/view/apidocs",
    }
    spec = APISpec(title=app_name, version="1.0.0", openapi_version="3.0.2",
                   plugins=[FlaskPlugin(), ma_plugin], **advanced_options)
    setup_schema_definition(spec)
    setup_paths(spec, api_module=api_module_path)
    swagger_config = Swagger.DEFAULT_CONFIG
    swagger_config["openapi"] = "3.0.2"
    swagger_config["ui_params"] = dict(displayRequestDuration=True)
    sw = Swagger(template=spec.to_dict(), config=swagger_config)
    sw.init_app(app)
    ctx.pop()
