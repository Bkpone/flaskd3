import logging

from flaskd3.appcore.core.decorators import handle_db_commits
from flaskd3.infrastructure.error_tracker.factories.api_error_log_factory import (
    APIErrorLogFactory,
)

logger = logging.getLogger(__name__)


class APIErrorPersistenceService:
    def __init__(self, api_error_log_repository):
        self.api_error_log_repository = api_error_log_repository

    @handle_db_commits
    def process_message(self, message_data):
        try:
            api_error_log_aggregate = APIErrorLogFactory.create_entry_from_data(message_data)
        except Exception as e:
            logger.exception("Domain Event Create failed")
            return False
        self.api_error_log_repository.save(api_error_log_aggregate)
        return True
