# Copyright 2018-2020 Faculty Science Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid
from enum import Enum

from .base import BaseClient


class RunState(Enum):
    QUEUED = "queued"
    STARTING = "starting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ERROR = "error"


class JobClient(BaseClient):

    SERVICE_NAME = "steve"

    def create_run(self, project_id, job_id, parameter_value_sets=None):
        """Create a run for a job.

        When creating a run, each item in ``parameter_value_sets`` will be
        translated into an individual subrun. For example, to start a single
        run of job with ``file`` and ``alpha`` arguments:

        >>> client.create_run(
        >>>     project_id, job_id, [{"file": "data.txt", "alpha": "0.1"}]
        >>> )

        Pass additional entries in ``parameter_value_sets`` to start a run
        array with multiple subruns. For example, for a job with a single
        ``file`` argument:

        >>> client.create_run(
        >>>     project_id,
        >>>     job_id,
        >>>     [{"file": "data1.txt"}, {"file": "data2.txt"}]
        >>> )

        Many jobs do not take any arguments. In this case, simply pass a list
        containing empty parameter value dictionaries, with the number of
        entries in the list corresponding to the number of subruns you want:

        >>> client.create_run(project_id, job_id, [{}, {}])

        Parameters
        ----------
        project_id : uuid.UUID
        job_id : uuid.UUID
        parameter_value_sets : List[dict], optional
            A list of parameter value sets. Each set of parameter values will
            result in a subrun with those parameter values passed. Default:
            single subrun with no parameter values.

        Returns
        -------
        uuid.UUID
            The ID of the created run.
        """
        if parameter_value_sets is None:
            parameter_value_sets = [{}]

        endpoint = "/project/{}/job/{}/run".format(project_id, job_id)
        payload = {
            "parameterValues": [
                [
                    {"name": name, "value": value}
                    for name, value in parameter_values.items()
                ]
                for parameter_values in parameter_value_sets
            ]
        }
        response = self._post_raw(endpoint, json=payload)
        return uuid.UUID(response.json()["runId"])

    def get_run_state(self, project_id, job_id, run_identifier):
        """Get the state of a run.

        Parameters
        ----------
        project_id : uuid.UUID
        job_id : uuid.UUID
        run_identifier : uuid.UUID or int
            The ID of the run to get or its run number.

        Returns
        -------
        RunState
        """
        endpoint = "/project/{}/job/{}/run/{}".format(
            project_id, job_id, run_identifier
        )
        response = self._get_raw(endpoint)
        state_raw = response.json()["state"]
        return RunState(state_raw)
