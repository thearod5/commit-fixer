from unittest import TestCase

import responses

from safa.api.safa_client import SafaClient
from tests.mocker import Mocker


class TestCreateProject(TestCase):
    @responses.activate
    def test_create_project(self):
        client = SafaClient()

        project_name = "test_name"
        project_description = "test_description"
        project_data = {"prop1": "test"}

        Mocker.mock_auth(self, Mocker.DEFAULT_EMAIL, Mocker.DEFAULT_PASSWORD)
        Mocker.mock_create_project(self, project_data)

        client.login(email=Mocker.DEFAULT_EMAIL, password=Mocker.DEFAULT_PASSWORD)
        project_response = client.create_project(project_name, project_description)
        self.assertEqual(project_data, project_response)
