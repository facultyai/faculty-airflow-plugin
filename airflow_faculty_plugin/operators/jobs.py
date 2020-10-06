import os
import time
import uuid

from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from ..faculty import client
from ..faculty.clients.job import RunState


COMPLETED_RUN_STATES = {
    RunState.COMPLETED,
    RunState.FAILED,
    RunState.CANCELLED,
    RunState.ERROR,
}


class FacultyJobRunNowOperator(BaseOperator):
    """ Run a Faculty job and wait for it to finish

    Parameters
    ----------
    job_id_or_name : str
        ID or name of the job to trigger
    project_id : str
        Project ID of the job to trigger
    polling_period_seconds : int, optional
        The number of seconds between checks for whether the job has
        completed. Use a low number if you expect the job to finish
        quickly, and a high number if the job is longer. Defaults to
        30s.
    job_parameter_values : dict, optional
        Dictionary mapping parameter names to the values they should take.
        (templated)
    task_id : str
        Identifier for the Airflow task triggered by this job
    client_configuration : dict, optional
        The configuration with which to connect to the Faculty API.
        Use this to customise how to connect to Faculty. Refer to the
        docstring for the `client` method for a full description of parameters:
        https://github.com/facultyai/faculty/blob/master/faculty/__init__.py
    dag : DAG
        Reference to the DAG that owns this task.
    """

    template_fields = ["job_parameter_values"]

    ui_color = "#00aef9"
    ui_fgcolor = "#fff"

    @apply_defaults
    def __init__(
        self,
        job_id_or_name,
        job_parameter_values=None,
        polling_period_seconds=30,
        project_id=None,
        client_configuration=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if job_parameter_values is not None:
            self.job_parameter_values = job_parameter_values
        else:
            self.job_parameter_values = {}

        self.polling_period_seconds = polling_period_seconds

        if project_id is not None:
            self.project_id = project_id
        else:
            self.project_id = os.environ["FACULTY_PROJECT_ID"]

        if client_configuration is not None:
            self.client_configuration = client_configuration
        else:
            self.client_configuration = {}

        self.job_id = self._resolve_job_id(job_id_or_name)

    def _resolve_job_id(self, job_id_or_name):
        """ Resolve job ID from name """
        try:
            job_id = uuid.UUID(job_id_or_name)
            return job_id
        except ValueError:
            pass

        job_client = client("job", **self.client_configuration)
        job_names = job_client.list_names(self.project_id)
        job_ids = {v: k for k, v in job_names.items()}

        try:
            job_id = job_ids[job_id_or_name]
        except KeyError:
            raise ValueError(f"Job name {job_id_or_name} not found")

        return job_id

    def execute(self, context):
        """
        Triggers a run of a Faculty job based on the job id and parameters
        passed in
        """
        log = self.log
        project_id = self.project_id
        job_id = self.job_id
        job_parameter_values = self.job_parameter_values

        # Trigger job run parameters
        job_client = client("job", **self.client_configuration)
        log.info(
            "Jobs client is looking for service at URL "
            f"{job_client.session.service_url(job_client.SERVICE_NAME)}."
        )
        log.info(
            f"Creating a job run for job {job_id} in project {project_id} "
            f"with parameters {job_parameter_values}."
        )
        run_id = job_client.create_run(
            project_id, job_id, [job_parameter_values]
        )
        log.info(
            f"Triggered job {job_id} with run ID "
            f"{run_id} and parameters {job_parameter_values}."
        )

        while True:
            run_state = job_client.get_run_state(project_id, job_id, run_id)
            if run_state in COMPLETED_RUN_STATES:
                if run_state == RunState.COMPLETED:
                    log.info(f"Run {run_id} completed successfully.")
                    break

                else:
                    raise AirflowException(
                        f"Job {job_id} and run {run_id} failed "
                        f"with terminal state: {run_state}."
                    )
            else:
                log.info(
                    f"Run {run_id} in state: {run_state}. "
                    f"Sleeping for {self.polling_period_seconds}s."
                )
                time.sleep(self.polling_period_seconds)

    def on_kill(self):
        """
        Cancels the job run on Faculty
        """
        # TODO: Use the Faculty job client to cancel the run.
        raise NotImplementedError
