from unittest import TestCase

from safa.api.client_factory import create_safa_client
from tests.live.live_test import LiveTest


class TestCreateDeleteProject(TestCase):
    def test_runner(self):
        """
        Tests that users are able to create and delete their project.
        """
        live_test = LiveTest()

        live_test.setup_git_repository()
        live_test.run_test(self, "~/projects/safa-cmd/tests/live/project_config")

        config = live_test.get_safa_config()
        client = create_safa_client(config)

        projects = [p for p in client.get_projects() if p["projectId"] == config.project_config.project_id]
        self.assertEqual(len(projects), 1)

        live_test.run_test(self, "~/projects/safa-cmd/tests/live/project_delete")

        projects = [p for p in client.get_projects() if p["projectId"] == config.project_config.project_id]
        self.assertEqual(len(projects), 0)

        live_test.cleanup()
