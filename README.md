# Airflow Faculty Plugin

The *Airflow Faculty Plugin* lets you interact with Faculty services
from [Apache Airflow](https://airflow.apache.org/). Currently, the
only supported mode of interaction is triggering jobs.

## Installation

You can install this plugin from PyPI into the Python environment that
executes the DAG:

```
pip install airflow-faculty-plugin
```

To interact with platform resources, you will need to pass in
credentials. Generate CLI credentials and save them in
``~/.config/faculty/credentials`` on the driver.

## Operators

### FacultyJobRunNowOperator

This operator triggers a Faculty job run and waits for an end event
for the job run (such as COMPLETED or ERROR).

Use this operator in your DAG as follows:

```py
from airflow import DAG

from airflow.operators.faculty import FacultyJobRunNowOperator

dag = DAG("faculty_job_tutorial")

run_job = FacultyJobRunNowOperator(
    job_id="260938d9-1ed8-47eb-aaf2-a0f9d8830e3a",
    project_id="e88728f6-c197-4f01-bdf2-df3fc92bfe4d",
    polling_period_seconds=10,
    task_id="trigger_job",
    dag=dag
)
```

The operator accepts the following parameters:

- `job_id`: the ID of the job to trigger. To find the ID, run
   `faculty job list -v` in the project that this job is in.
- `project_id`: the ID of the job to trigger. To find the ID,
   run `echo $FACULTY_PROJECT_ID` in the terminal of a server
   in this project.
- `polling_period_seconds`: The number of seconds between checks for
   whether the job has completed. Use a low number if you expect
   the job to finish quickly, and a high number if the job is
   longer. Defaults to 30s.
- `job_parameter_values`: a dictionary mapping parameter names
   to the values they should take in this run. For instance,
   if the job requires the parameter `NUMBER_ESTIMATORS`, pass in:
   `{"NUMBER_ESTIMATORS": "50"}`
