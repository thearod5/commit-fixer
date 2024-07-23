from unittest import TestCase

from tests.live.infra.live_test_controller import LiveTestController
from tests.live.infra.repo_factory import RepoFactory


class TestSearchProject(TestCase):
    def test_runner(self):
        """
        Tests that users are able to create and delete their project.
        """
        repo_factory = RepoFactory()
        print(repo_factory.repo_path)
        repo_factory.commit_file("test.txt", "hello world")

        # Step - Create project
        live_test = LiveTestController(repo_factory.repo_path)
        live_test.run_test(self, "~/projects/safa-cmd/tests/live/project_config")
        config, client = repo_factory.get_safa_client()
        project_id = config.project_config.project_id

        # Step - Perform project search
        live_test.run_test(self, "~/projects/safa-cmd/tests/live/project_search")

        # Step - Delete project
        live_test.run_test(self, "~/projects/safa-cmd/tests/live/project_delete", project_id=project_id)

        repo_factory.cleanup()
