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


import os
import json
import errno
from datetime import datetime
from collections import namedtuple

import pytz


AccessToken = namedtuple("AccessToken", ["token", "expires_at"])


class AccessTokenStore(object):
    def __init__(self, tokens=None):
        self.tokens = tokens or {}

    @staticmethod
    def _hash_profile(profile):
        return str(hash(profile))

    def __getitem__(self, profile):
        return self.tokens[self._hash_profile(profile)]

    def __setitem__(self, profile, access_token):
        self.tokens[self._hash_profile(profile)] = access_token

    def get(self, profile):
        try:
            return self[profile]
        except KeyError:
            return None


def _is_valid_access_token(access_token_or_none):
    if access_token_or_none is None:
        return False
    else:
        return access_token_or_none.expires_at >= datetime.now(tz=pytz.utc)



class AccessTokenMemoryCache(object):
    def __init__(self):
        self._store = AccessTokenStore()

    def get(self, profile):
        access_token = self._store.get(profile)
        return access_token if _is_valid_access_token(access_token) else None

    def add(self, profile, access_token):
        self._store[profile] = access_token
