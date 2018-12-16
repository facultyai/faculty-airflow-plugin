from airflow.plugins_manager import AirflowPlugin

from operators.faculty_operators import FacultyJobRunNowOperator


class FACULTYPlugin(AirflowPlugin):
    name = "faculty-plugin"
    operators = [FacultyJobRunNowOperator]
