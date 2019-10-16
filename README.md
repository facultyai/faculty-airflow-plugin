# Faculty Airflow Plugin

The *Faculty Airflow Plugin* lets you interact with Faculty services
from [Apache Airflow](https://airflow.apache.org/). Currently, the
only supported mode of interaction is triggering jobs.

## Installation

You can install this plugin from Pypi into the Python environment that
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

```
    :param job_id                       The Faculty job id
    :type job_id                        string
    :param job_parameter_values         The parameters to be passed into the job run
    :type job_parameter_values          dict
    :param polling_period_seconds       The time to wait between polling to get the job run status
    :type polling_period_seconds        int
    :param project_id                   The project id for the job. 
    :type project_id                    string
```
