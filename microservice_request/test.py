from unittest.mock import Mock


class RequestTestCaseMixin:
    """Usage:
    @mock.patch("microservice_request.services.ConnectionService._method")
    def test_usage(self, mocked_request):
        mock_resp = self._mock_response(json={"detail": False}, status_code=status.HTTP_200_OK)
        mocked_request.return_value = mock_resp
    """

    def _mock_response(
        self, status_code=200, json=None, raise_for_status=None, content_type="application/json", headers=None
    ):
        """
        since we typically test a bunch of different
        requests calls for a service, we are going to do
        a lot of mock responses, so it's usually a good idea
        to have a helper function that builds these things
        """
        if headers is None:
            headers = {}
        mock_resp = Mock()
        # mock raise_for_status call w/optional error
        mock_resp.raise_for_status = Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        # set status code and content
        mock_resp.status_code = status_code
        mock_resp.content_type = content_type
        mock_resp.headers = headers or {}
        # add json data if provided
        mock_resp.json = Mock(return_value=json)
        return mock_resp
