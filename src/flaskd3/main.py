from flaskd3.appcore.core.schema_manager import SchemaManager
from flaskd3.appcore.core.app_config import setup_config
from flaskd3.appcore.core.admin_views import setup_admin
from flaskd3.appcore.core.api_docs import init_docs
from flaskd3.appcore.core.application_core import app_core
from flaskd3.appcore.core.extensions import register_extensions
from flaskd3.appcore.logging.logging_conf import configure_logging
from flaskd3.appcore.middlewares.middleware_registry import register_middleware
from flaskd3 import infrastructure
from flaskd3 import common


def setup_flask3d(app, app_info, application_service_modules, domain_modules, acl_modules, admin_view_modules,
                  serializers_modules, api_modules, config_module_map=None, api_spec_options=None):
    """
    Create the core app
    :return:
    """
    if not admin_view_modules:
        admin_view_modules = list()
    admin_view_modules.append(infrastructure)
    if not serializers_modules:
        serializers_modules = list()
    serializers_modules.append(common)
    setup_config(app, config_module_map)
    configure_logging(app)
    register_extensions(app)
    app_core.init(app, application_service_modules, domain_modules, acl_modules)
    setup_admin(app, admin_view_modules)
    register_middleware(app)
    SchemaManager.load_all_schemas(serializers_modules)
    init_docs(app, app_info.app_name, api_modules, api_spec_options)
    return app
