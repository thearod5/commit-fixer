import traceback
from typing import Any, Dict, Optional

import requests


class HttpClient:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None, global_parameters: Optional[Dict[str, Any]] = None):
        """
        Creates new HTTP client directed at REST API under base url.
        :param base_url: The URL of the REST API.
        :param headers: Additional headers to include in HTTP requests.
        :param global_parameters: Parameters used on every request.
        """
        self.base_url = base_url
        self.headers = headers if headers else {}
        self.session = requests.Session()
        self.global_parameters: Dict[str, str] = global_parameters if global_parameters else {}

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Performs GET request to endpoint.
        :param endpoint: Relative path to endpoint from base url.
        :param params: Additional parameters to include in request.
        :return: The request's response.
        """
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Any:
        """
        Performs POST request to endpoint.
        :param endpoint: Relative path to endpoint from base url.
        :param data: The data to include in request.
        :return: The requests' response.
        """
        return self._request("POST", endpoint, json=data, **kwargs)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """
        Performs PUT http request.
        :param endpoint: Relative path to endpoint from base url.
        :param data: The data to include in the HTTP request.
        :return: The request's response.
        """
        return self._request("PUT", endpoint, json=data)

    def delete(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """
        Performs a DELETE http request.
        :param endpoint: Relative path to endpoint from base url.
        :param data: The data to include in request.
        :return: Request response.
        """
        return self._request("DELETE", endpoint, json=data)

    def get_cookie(self, cookie_name: str, error: Optional[str] = None):
        """
        Retrieves cookie with given name.
        :param cookie_name: The name of the cookie to retrieve.
        :param error: The error message to display if not found.
        :return: The cookie value.
        """
        if error is None:
            error = f"Could not find cookie {cookie_name}"
        if cookie_name not in self.session.cookies:
            raise Exception(error)
        return self.session.cookies[cookie_name]

    def _request(self, method: str, endpoint_rel_path: str, **kwargs) -> Any:
        """
        Performs an HTTP request.
        :param method: The method of the request (e.g. POST, PUT, DELETE, GET)
        :param endpoint_rel_path: Relative path to endpoint from base url.
        :param kwargs: Additional keyword arguments to request method.
        :return: JSON response to request.
        """
        url = f"{self.base_url}/{endpoint_rel_path}"
        kwargs.update(**self.global_parameters)
        response = self.session.request(method, url, headers=self.headers, **kwargs)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            traceback.print_exc()
            raise Exception(f"HTTP error occurred: {e}")

        return response.json() if len(response.content) > 0 else {}
