from unittest import TestCase

import responses

from safa.api.constants import SAFA_AUTH_TOKEN
from safa.api.safa_client import SafaClient
from tests.mocker import Mocker


class TestGetProjects(TestCase):
    @responses.activate
    def test_auth(self):
        """
        Tests that user is able to authenticate.
        """
        auth_token_value = "default_token_value"
        Mocker.mock_auth(self, Mocker.DEFAULT_EMAIL, Mocker.DEFAULT_PASSWORD, token_value=auth_token_value)

        client = SafaClient()
        client.login(email=Mocker.DEFAULT_EMAIL, password=Mocker.DEFAULT_PASSWORD)

        # Verify cookie exists
        retrieved_auth_token_value = client.http_client.get_cookie(SAFA_AUTH_TOKEN)
        self.assertEqual(auth_token_value, retrieved_auth_token_value)
