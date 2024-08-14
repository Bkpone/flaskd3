from flaskd3.common.exceptions import ValidationException
from flaskd3.common.utils.json_utils import make_jsonify_ready
from flaskd3.common.utils.dateutils import current_datetime
from flaskd3.infrastructure.async_job_runner.factories.job_factory import JobFactory


class JobService(object):
    class JobHandler:
        def __init__(self, handler_func, update_progress, need_job_data=False):
            self.handler_func = handler_func
            self.update_progress = update_progress
            self.need_job_data = need_job_data

    def __init__(self, job_repository, recurring_job_repository):
        self._register = dict()
        self.job_repository = job_repository
        self.recurring_job_repository = recurring_job_repository

    def register(self, job_name, job_handler, update_progress=False, need_job_data=False):
        assert job_name not in self._register, "Duplicate Job %s" % job_name
        self._register[job_name] = JobService.JobHandler(job_handler, update_progress, need_job_data)

    def write(self, job_name, data, run_time=None):
        data = make_jsonify_ready(data)
        run_time = run_time if run_time else current_datetime()
        job_aggregate = JobFactory.create_job(job_name, data, run_time)
        self.job_repository.save(job_aggregate)
        return job_aggregate

    def write_recurring(self, name, job_name, data, schedule, is_active=True, schedule_pending=False):
        data = make_jsonify_ready(data)
        if not self._register.get(job_name):
            raise ValidationException("Invalid Job Name: {}".format(job_name))
        recurring_job_aggregate = JobFactory.create_recurring_job(name, job_name, data, schedule, is_active, schedule_pending)
        self.recurring_job_repository.save(recurring_job_aggregate)
        return recurring_job_aggregate

    def get_job(self, job_id):
        return self.job_repository.load(job_id)

    def update_job(self, job_aggregate):
        return self.job_repository.update(job_aggregate)

    def get_handler(self, job_name):
        return self._register[job_name]

    def get_recurring_jobs(self):
        return self.recurring_job_repository.load_all()
