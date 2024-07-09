from unittest import TestCase

import responses

from safa_cmd.safa.safa_client import SafaClient
from tests.mocker import Mocker


class TestProjects(TestCase):
    @responses.activate
    def test_projects(self):
        """
        Tests that user is able to retrieve their projects.
        """

        Mocker.mock_auth(self)
        Mocker.mock_get_projects(self, Mocker.DEFAULT_PROJECTS)

        client = SafaClient()
        client.login(Mocker.DEFAULT_EMAIL, Mocker.DEFAULT_PASSWORD)

        retrieved_projects = client.get_projects()
        self.assertEqual(Mocker.DEFAULT_PROJECTS, retrieved_projects)
