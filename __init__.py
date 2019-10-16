from airflow.plugins_manager import AirflowPlugin

from operators.faculty_operators import FacultyJobRunNowOperator


class FacultyPlugin(AirflowPlugin):
    name = "faculty"
    operators = [FacultyJobRunNowOperator]
