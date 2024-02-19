import sys

sys.path.append("../..")
import requests
from dev.utils import RenderJSON, load_config, render_json
from requests.exceptions import HTTPError


def call_api(url: str, method: str, **kwargs):
    """
    Makes an API call using the specified HTTP method.

    Args:
    - url (str): The URL of the API endpoint.
    - method (str): The HTTP method to use (e.g., 'get', 'post', 'put', 'delete').
    - **kwargs: Arbitrary keyword arguments that are passed directly to requests.request.
      These can include parameters like 'data', 'json', 'headers', and 'timeout'.

    Returns:
    - response: The Response object returned by the requests call.

    Raises:
    - HTTPError: If the response contains an HTTP error status code.
    """
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Handle specific HTTP errors here
    except requests.exceptions.RequestException as err:
        print(
            f"Error during requests to {url}: {err}"
        )  # Handle other requests errors here
    finally:
        return response
