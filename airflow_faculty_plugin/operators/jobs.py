import os
import time

from airflow.exceptions import AirflowException
from airflow.models import BaseOperator

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
    job_id : str
        ID of the job to trigger
    project_id : str
        Project ID of the job to trigger
    polling_period_seconds : int, optional
        The number of seconds between checks for whether the job has
        completed. Use a low number if you expect the job to finish
        quickly, and a high number if the job is longer. Defaults to
        30s.
    job_parameter_values : dict
        Dictionary mapping parameter names to the values they should take
    task_id : str
        Identifier for the Airflow task triggered by this job
    dag : DAG
        Reference to the DAG that owns this task.
    """

    ui_color = "#00aef9"
    ui_fgcolor = "#fff"

    def __init__(
        self,
        job_id,
        job_parameter_values=None,
        polling_period_seconds=30,
        project_id=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.job_id = job_id

        if job_parameter_values is not None:
            self.job_parameter_values = job_parameter_values
        else:
            self.job_parameter_values = {}

        self.polling_period_seconds = polling_period_seconds

        if project_id is not None:
            self.project_id = project_id
        else:
            self.project_id = os.environ["FACULTY_PROJECT_ID"]

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
        job_client = client("job")
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
                    log.info(
                        f"Run {run_id} completed successfully."
                    )
                    break

                else:
                    raise AirflowException(
                        f"Job {job_id} and run {run_id} failed "
                        f"with terminal state: {run_state}."
                    )
            else:
                log.info(
                    f"Run {run_id} in state: {run_state}. "
                    f"Sleeping for {self.polling_period_seconds}."
                )
                time.sleep(self.polling_period_seconds)

    def on_kill(self):
        """
        Cancels the job run on Faculty
        """
        # TODO: Use the Faculty job client to cancel the run.
        raise NotImplementedError
