from unittest import TestCase

from safa_sdk.safa_client import SafaClient
from tests.mocker import Mocker


class TestCreateProject(TestCase):
    def test_create_project(self):
        client = SafaClient()

        project_name = "test_name"
        project_description = "test_description"
        project_data = {"prop1": "test"}
        Mocker.mock_create_project(self, project_data)
        project_response = client.create_project(project_name, project_description)
        self.assertEqual(project_data, project_response)
