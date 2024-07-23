from unittest import TestCase

from tests.infra.constants import TEST_OUTPUT_DIR
from tests.infra.live_test_controller import LiveTestController
from tests.infra.repo_factory import RepoFactory


class TestCreateDeleteProject(TestCase):
    def test_runner(self):
        """
        Tests that users are able to create and delete their project.
        """

        repo_factory = RepoFactory(repo_folder_path=TEST_OUTPUT_DIR)
        repo_factory.commit_file("test.txt", "Hello World")

        # Create project and upload to SAFA
        live_test = LiveTestController(repo_factory.repo_path)
        live_test.run_test(self, "~/projects/safa-cmd/tests/live/project_config")

        config, client = repo_factory.get_safa_client()

        # VP - Verify that project exists
        projects = [p for p in client.get_projects() if p["projectId"] == config.project_config.project_id]
        self.assertEqual(len(projects), 1)

        # TODO: VP - Verify that artifacts were created

        # Step - Delete project
        live_test.run_test(self, "~/projects/safa-cmd/tests/live/project_delete")

        # VP - Verify that project is deleted.
        projects = [p for p in client.get_projects() if p["projectId"] == config.project_config.project_id]
        self.assertEqual(len(projects), 0)

        live_test.cleanup()
