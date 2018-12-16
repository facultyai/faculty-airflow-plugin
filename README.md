# Faculty Airflow Plugin

## Operators

### FacultyJobRunNowOperator
This operator triggers a Faculty job run and waits for an end event for the job run (such as COMPLETED or ERROR).
It accepts the following parameters:

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