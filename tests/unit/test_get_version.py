import uuid
from unittest import TestCase

import responses

from tests.unit.mocker import Mocker


class TestGetProjectData(TestCase):
    @responses.activate
    def test_get_project_data(self):
        """
        Tests that user is able to retrieve a project's data.
        """
        version_id = str(uuid.uuid4())
        project_data = {"name": "blah"}

        Mocker.mock_auth(self)
        Mocker.mock_get_project_data(self, project_data)

        client = Mocker.get_client()
        client.login(email=Mocker.DEFAULT_EMAIL, password=Mocker.DEFAULT_PASSWORD)

        retrieved_project_data = client.get_version(version_id)
        self.assertEqual(project_data, retrieved_project_data)
