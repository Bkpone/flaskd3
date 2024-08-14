from flaskd3.types.base_enum import BaseEnum


class DBType(BaseEnum):
    RDS = "rds", "RDS"
    NOSQL = "no_sql", "NO Sql"
    REDIS = "redis", "Redis Cache"
