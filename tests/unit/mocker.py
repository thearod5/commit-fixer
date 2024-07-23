import json
import re
from typing import Dict, List
from unittest import TestCase

import responses
from requests import PreparedRequest

from safa.api.constants import SAFA_AUTH_TOKEN
from safa.api.http_client import HttpClient
from safa.api.safa_client import SafaClient
from safa.constants import DEFAULT_BASE_URL

DEFAULT_AUTH_TOKEN = "auth_token"


class Mocker:
    DEFAULT_EMAIL = "alberto@safa.ai"
    DEFAULT_PASSWORD = "some_password"
    DEFAULT_PROJECTS = [{"name": "project1"}, {"name": "project2"}]
    BASE_URL = DEFAULT_BASE_URL

    @staticmethod
    def get_client() -> SafaClient:
        """
        Returns safa client with same base url as mocker.
        :return: Safa Client.
        """
        http_client = HttpClient(Mocker.BASE_URL)
        client = SafaClient(http_client=http_client)
        return client

    @staticmethod
    def mock_auth(tc: TestCase, email: str = DEFAULT_EMAIL, password: str = DEFAULT_PASSWORD,
                  token_value: str = DEFAULT_AUTH_TOKEN) -> None:
        """
        Creates mock authentication response.
        :return: None
        """

        def request_callback(request):
            request_json = json.loads(request.body)
            Mocker.assert_keys(tc, request_json, ["email", "password"])
            tc.assertEqual(email, request_json["email"])
            tc.assertEqual(password, request_json["password"])

            return 200, {'Set-Cookie': f"{SAFA_AUTH_TOKEN}={token_value}; Path=/; HttpOnly"}, json.dumps({})

        responses.add_callback(
            responses.POST,
            Mocker.BASE_URL + "/login",
            callback=request_callback,
            content_type='application/json'
        )

    @staticmethod
    def mock_get_projects(tc: TestCase, projects_data: List[Dict]) -> None:
        """
        Mocks endpoint for getting projects.
        :param tc: Test case used to assert request details.
        :param projects_data: The list of projects to return in response.
        :return: None
        """
        if projects_data is None:
            projects_data = Mocker.DEFAULT_PROJECTS

        def request_callback(request: PreparedRequest):
            Mocker.assert_auth_cookie(tc, request)
            return 200, {}, json.dumps(projects_data)

        responses.add_callback(
            responses.GET,
            Mocker.BASE_URL + "/projects",
            callback=request_callback,
            content_type='application/json'
        )

    @staticmethod
    def mock_get_project_data(tc: TestCase, project_data: Dict):
        def request_callback(request):
            Mocker.assert_auth_cookie(tc, request)
            return 200, {}, json.dumps(project_data)

        responses.add_callback(
            responses.GET,
            re.compile(rf"{Mocker.BASE_URL}/projects/versions/[0-9a-fA-F-]+"),
            callback=request_callback,
            content_type='application/json'
        )

    @staticmethod
    def mock_create_project(tc: TestCase, project_data: Dict) -> None:
        """
        Mocks request to create new project.
        :param tc: The test case used to make assertions.
        :param project_data: The project data to respond to request with.
        :return: None
        """

        def request_callback(request):
            Mocker.assert_auth_cookie(tc, request)
            request_body = json.loads(request.body)
            Mocker.assert_keys(tc, request_body, ["name", "description"])
            return 200, {}, json.dumps(project_data)

        responses.add_callback(
            responses.POST,
            re.compile(rf"{Mocker.BASE_URL}/projects"),
            callback=request_callback,
            content_type='application/json'
        )

    @staticmethod
    def assert_keys(tc: TestCase, obj: Dict, keys: List[str]) -> None:
        """
        Asserts that keys are present in object.
        :param tc: Test case used to make assertions.
        :param obj: The object to check for keys.
        :param keys: The keys to verify exist in object.
        :return: None
        """
        for key in keys:
            tc.assertIn(key, obj, msg=f"Expected ({key}) in {obj}")

    @staticmethod
    def assert_auth_cookie(tc: TestCase, request: PreparedRequest) -> None:
        """
        Asserts that request contains SAFA authentication cookie.
        :param tc: Test case used to make assertions.
        :param request: The request being checked.
        :return: None
        """
        cookies = request.headers.get('Cookie', '')
        tc.assertIn(f"{SAFA_AUTH_TOKEN}=auth_token", cookies, msg="Cookies did not contain SAFA token.")
