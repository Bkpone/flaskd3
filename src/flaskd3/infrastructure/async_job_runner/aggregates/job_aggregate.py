from datetime import datetime

from flaskd3.types.base_entity import BaseEntity
from flaskd3.types.type_info import TypeInfo
from flaskd3.infrastructure.async_job_runner.constants import AsyncJobStatus
from flaskd3.common.value_objects import JobData


class JobAggregate(BaseEntity):

    is_multi_tenant = True

    job_id = TypeInfo(str, primary_key=True)
    extra_data = TypeInfo(dict)
    run_time = TypeInfo(datetime, allow_none=True)
    job_name = TypeInfo(str, allow_none=True)
    status = TypeInfo(AsyncJobStatus)
    response = TypeInfo(str, allow_none=True)
    tries = TypeInfo(int, default=0, required=False)
    created_at = TypeInfo(datetime)
    modified_at = TypeInfo(datetime)

    def update_status(self, status, response, should_append=True):
        if status == AsyncJobStatus.FAILED:
            self.tries += 1
        self.status = status
        if not isinstance(response, str):
            response = str(response)
        if self.response and response and should_append:
            self.response += response
        else:
            self.response = response
        return self

    def get_job_data(self):
        return JobData(job_id=self.job_id, job_name=self.job_name, run_time=self.run_time, data=self.extra_data)
