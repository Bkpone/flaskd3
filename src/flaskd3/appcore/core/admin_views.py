# coding=utf-8
"""
Admin configuration file
"""
from flask_admin.base import Admin
from flask_admin.menu import MenuLink

from flaskd3.appcore.core.app_constants import APP_NAME
from flaskd3.types.base_admin_view import BaseAdminView
from flaskd3.infrastructure.database.sqlalchemy.sql_db_service import db
from flaskd3.common.utils.common_utils import search_class


def setup_admin(app, modules):
    """
    Setting Up Admin
    :param app:
    :param modules:
    :return:
    """
    admin = Admin(app, name=APP_NAME, template_mode="bootstrap3", url="/view/admin")
    admin_views = search_class(
        modules=modules,
        sub_module_name="admin_views",
        class_filters=[BaseAdminView],
        exclude_list=["ModelView", "BaseAdminView"],
        get_object=False,
    )
    for admin_view in admin_views.values():
        parameters = dict(
            model=admin_view.model_class,
            session=db.session,
            category=admin_view.view_category,
        )
        if getattr(admin_view, "view_name", None):
            parameters["name"] = admin_view.view_name
        admin.add_view(admin_view(**parameters))
    admin.add_link(MenuLink("API Docs", "/view/apidocs"))
    admin.add_link(MenuLink("logout", "/dc/logout"))
