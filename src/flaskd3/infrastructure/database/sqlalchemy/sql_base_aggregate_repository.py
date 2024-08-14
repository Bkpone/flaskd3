import logging
from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import lazyload
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from flaskd3.infrastructure.database.base_repository import BaseRepository
from flaskd3.infrastructure.database.constants import DBType
from flaskd3.infrastructure.database.sqlalchemy.db_adapter import DBAdapter
from flaskd3.common.exceptions import (
    AggregateNotFound,
    DatabaseError,
    OutdatedVersion,
    ValidationException,
)

logger = logging.getLogger(__name__)


class SQLABaseAggregateRepository(BaseRepository):
    aggregate_class = None
    entity_map = {}
    exclude_key_map = None

    and_ = and_
    or_ = or_

    def __init__(self, db_service_provider):
        self.db = db_service_provider.get_db_service(DBType.RDS).get_db()

    @classmethod
    def get_name(cls):
        return cls.name

    def save(self, aggregate):
        """
        Saves the aggregate in DB

        :param aggregate:
        """
        aggregate.validate_entity()
        models = DBAdapter(self.entity_map, self, self.exclude_key_map).to_db_models(aggregate)
        self._save_all(models)

    def save_all(self, aggregates):
        """
        Saves the aggregate in DB

        :param aggregate:
        """
        models = []
        for aggregate in aggregates:
            aggregate.validate_entity()
            models.extend(DBAdapter(self.entity_map, self, self.exclude_key_map).to_db_models(
                aggregate))
        if models:
            self._save_all(models)

    def update(self, aggregate):
        """

        :param aggregate:
        :return:
        """
        if not aggregate.is_dirty and not aggregate.deleted:
            return
        aggregate.update_version()
        aggregate.validate_entity()
        models = DBAdapter(self.entity_map, self, self.exclude_key_map).to_db_models(aggregate)
        self._update_all(models)

    def update_all(self, aggregates, force_update=False):
        """

        :param aggregates:
        :param force_update:
        :return:
        """
        models = []
        for aggregate in aggregates:
            if not force_update and not aggregate.is_dirty:
                continue
            aggregate.update_version()
            aggregate.validate_entity()
            models.extend(DBAdapter(self.entity_map, self, self.exclude_key_map).to_db_models(aggregate))
        if models:
            self._update_all(models)

    def delete(self, aggregate):
        models = DBAdapter(self.entity_map, self, self.exclude_key_map).to_db_models(aggregate)
        self._delete_all(models)

    def delete_all(self, aggregates):
        models = list()
        for aggregate in aggregates:
            models.extend(DBAdapter(self.entity_map, self, self.exclude_key_map).to_db_models(aggregate))
        self._delete_all(models)

    def get_or_create(self, aggregate):
        loaded_aggregate = self.load(aggregate_id=aggregate.aggregate_id)
        if aggregate:
            return loaded_aggregate
        return self.save(aggregate)

    def load(self, aggregate_id, version=None, for_update=False, is_shallow=False):
        aggregate = DBAdapter(self.entity_map, self, self.exclude_key_map).load_aggregate(
            self.aggregate_class,
            aggregate_id=aggregate_id,
            for_update=for_update,
            is_shallow=is_shallow,
        )
        if version is not None and version != aggregate.version:
            raise OutdatedVersion(self.aggregate_class.__name__, aggregate_id, aggregate.version)
        return aggregate

    def load_many(
        self,
        aggregate_ids,
        for_update=False,
        nowait=True,
        find_all=True,
        load_shallow=False,
        meta=None,
    ):
        aggregate_ids = set(aggregate_ids)
        aggregate_model_class = self.entity_map[self.aggregate_class.__name__]
        queries = [getattr(aggregate_model_class, self.aggregate_class.get_primary_key()).in_(aggregate_ids)]
        aggregates = DBAdapter(self.entity_map, self, self.exclude_key_map).load_aggregates(
            self.aggregate_class, for_update, nowait, None, load_shallow, queries, meta
        )
        if find_all and len(aggregates) != len(aggregate_ids):
            missing_ids = aggregate_ids.copy()
            for aggregate in aggregates:
                missing_ids.remove(aggregate.primary_id)
            raise AggregateNotFound(self.aggregate_class.entity_name(), missing_ids)
        return aggregates

    def load_by_keys(self, for_update=False, no_wait=True, load_shallow=False, meta=None, **queries):
        return DBAdapter(self.entity_map, self, self.exclude_key_map).load_aggregates(
            self.aggregate_class,
            for_update=for_update,
            nowait=no_wait,
            order_by=None,
            load_shallow=load_shallow,
            queries=queries,
            meta=meta,
        )

    def load_all(self, load_shallow=False):
        queries = dict()
        aggregates = DBAdapter(self.entity_map, self, self.exclude_key_map).load_aggregates(
            self.aggregate_class,
            for_update=False,
            order_by=None,
            nowait=True,
            load_shallow=load_shallow,
            queries=queries,
            meta=None,
        )
        return aggregates

    def load_multiple(self, **queries):
        aggregates = DBAdapter(self.entity_map, self, self.exclude_key_map).load_aggregates(
            self.aggregate_class,
            for_update=False,
            order_by=None,
            nowait=True,
            load_shallow=False,
            queries=queries,
            meta=None,
        )
        return aggregates

    def load_multiple_shallow(self, **queries):
        aggregates = DBAdapter(self.entity_map, self, self.exclude_key_map).load_aggregates(
            self.aggregate_class,
            for_update=False,
            order_by=None,
            nowait=True,
            load_shallow=True,
            queries=queries,
            meta=None,
        )
        return aggregates

    def load_multiple_queries(self, for_update, nowait, order_by, load_shallow, meta, *queries):
        aggregates = DBAdapter(self.entity_map, self, self.exclude_key_map).load_aggregates(
            self.aggregate_class,
            for_update,
            nowait,
            order_by,
            load_shallow,
            queries,
            meta,
        )
        return aggregates

    def load_multiple_queries_readonly(self, order_by, load_shallow, meta, *queries):
        aggregates = DBAdapter(self.entity_map, self, self.exclude_key_map).load_aggregates(
            self.aggregate_class, False, True, order_by, load_shallow, queries, meta
        )
        return aggregates

    def load_aggregates_by_models(self, models, load_shallow=False):
        return DBAdapter(self.entity_map, self, self.exclude_key_map).load_aggregates_by_models(self.aggregate_class, models, load_shallow)

    def session(self):
        """
        returns session
        :return:
        """
        return self.db.session()

    def _save(self, item):
        """
        :param item:
        :return:
        """
        try:
            self.session().add(item)
            self.session().flush()
        except Exception as exp:
            logger.exception("DatabaseError")
            raise DatabaseError(exp.__str__())
        return item

    def _update(self, item):
        """
        :param item:
        :return:
        """
        try:
            self.session().merge(item)
            self.session().flush()
        except Exception as exp:
            raise DatabaseError(exp.__str__())
        return item

    def _update_all(self, items):
        """
        updates multiple items
        :param items:
        :return:
        """
        for item in items:
            self.session().merge(item)
        self.session().flush()
        return items

    def _save_all(self, items):
        """
        updates multiple items
        :param items:
        :return:booking
        """
        self.session().add_all(items)
        self.session().flush()
        return items

    def filter(self, model, *queries, for_update=False, nowait=True, order_by=None, meta=None):
        """
        :param model:
        :param queries:
        :param for_update:
        :param nowait:
        :return:
        """
        queryset = self.session().query(model)
        queryset = queryset.filter(*queries)
        if for_update:
            queryset = queryset.with_for_update(nowait=nowait)
        if order_by is not None:
            queryset = queryset.order_by(order_by)
        if meta:
            queryset = queryset.limit(meta.limit).offset(meta.start)
        return queryset

    def filter_by(self, model, for_update=False, nowait=True, meta=None, **queries):
        """
        :param model:
        :param queries:
        :param for_update:
        :param nowait:
        :param meta:
        :return:
        """
        queryset = self.session().query(model)
        queryset = queryset.filter_by(**queries)
        if meta:
            queryset = queryset.limit(meta.limit).offset(meta.start)
        if for_update:
            queryset = queryset.with_for_update(nowait=nowait)
        return queryset

    def mark_deleted(self, model, filter_queries, exclude=None):
        queryset = self.filter(model, *filter_queries)
        if exclude:
            exclude_queries = []
            for item in exclude:
                exclude_queries.append(~item)
            queryset = queryset.filter(*exclude_queries)
        queryset.update({"deleted": True}, synchronize_session=False)

    def filter_by_join(self, models, join_clause, *queries):
        """
        :param models:
        :param join_clause:
        :param queries:
        :return:
        """
        queryset = self.session().query(*models).filter(join_clause)
        items = queryset.filter(*queries)
        return items

    def get(self, model, **queries):
        """

        :param model:
        :param queries:
        :return:
        """
        queryset = self.session().query(model)

        for attr, value in queries.items():
            if value and not isinstance(value, datetime):
                value = "%s" % value
            queryset = queryset.filter(getattr(model, attr) == value)
        try:
            return queryset.one()
        except NoResultFound:
            return None
        except MultipleResultsFound:
            message = "Multiple objects %s found" % model
            raise ValidationException(description=message)
        except Exception as exp:
            raise DatabaseError(exp.__str__())

    def get_for_update(self, model, nowait=True, **queries):
        """
        The query will lock the row that is returned.
        If the transaction cannot lock the row (which will happen when some other transactions have obtained the lock),
        then:
            - If `nowait=True`, the query will fail with error
            - If `nowait=False`, the query will wait for the lock to get released.

        :param model:
        :param nowait:
        :param queries:
        :return:
        """
        queryset = self.session().query(model)
        for attr, value in queries.items():
            if value:
                value = "%s" % value
            queryset = queryset.filter(getattr(model, attr) == value)

        # Forcing lazy load here because
        # https://www.postgresql.org/message-id/21634.1160151923@sss.pgh.pa.us
        queryset = queryset.options(lazyload("*"))
        try:
            return queryset.with_for_update(nowait=nowait).one()
        except NoResultFound:
            return None
        except MultipleResultsFound:
            message = "Multiple objects %s found" % model
            raise ValidationException(description=message)
        except Exception as exp:
            raise DatabaseError(exp.__str__())

    def _delete_all(self, items):
        """
        delete multiple items
        :param items:
        :return:booking
        """
        for item in items:
            self.session().delete(item)
        self.session().flush()
        return items

    def delete_by_query(self, model, *queries):
        queryset = self.session().query(model)
        return queryset.filter(*queries).delete(synchronize_session="fetch")
