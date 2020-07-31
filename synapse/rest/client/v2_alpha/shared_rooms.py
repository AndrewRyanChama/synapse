# -*- coding: utf-8 -*-
# Copyright 2020 Half-Shot
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging

from synapse.api.errors import Codes, SynapseError
from synapse.http.servlet import RestServlet

from ._base import client_patterns

logger = logging.getLogger(__name__)


class UserSharedRoomsServlet(RestServlet):
    """
    GET /uk.half-shot.msc2666/user/shared_rooms/{user_id} HTTP/1.1
    """

    PATTERNS = client_patterns(
        "/uk.half-shot.msc2666/user/shared_rooms/(?P<user_id>[^/]*)",
        releases=(),  # This is an unstable feature
    )

    def __init__(self, hs):
        super(UserSharedRoomsServlet, self).__init__()
        self.auth = hs.get_auth()
        self.store = hs.get_datastore()

    async def on_GET(self, request, user_id):
        requester = await self.auth.get_user_by_req(request)
        if user_id == requester.user.to_string():
            raise SynapseError(
                code=400,
                msg="'user_id' must not be the authenticated user",
                errcode=Codes.BAD_JSON,
            )

        rooms = await self.store.get_rooms_in_common_for_users(
            requester.user.to_string(), user_id
        )

        return 200, {"joined": rooms}


def register_servlets(hs, http_server):
    UserSharedRoomsServlet(hs).register(http_server)
