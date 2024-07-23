from unittest import TestCase

from tests.infra.live_test_controller import LiveTestController


class TestCreateDeleteProject(TestCase):
    def test_runner(self):
        """
        Tests that users are able to create and delete their project.
        """
        live_test = LiveTestController()
        live_test.cleanup()
        live_test.setup_git_repository()
        live_test.run_test(self, "~/projects/safa-cmd/tests/live/project_config")
        live_test.run_test(self, "~/projects/safa-cmd/tests/live/project_search")
        live_test.run_test(self, "~/projects/safa-cmd/tests/live/project_delete")
        live_test.cleanup()
