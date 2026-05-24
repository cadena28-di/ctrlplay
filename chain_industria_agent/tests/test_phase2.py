"""Tests Fase 2 — Notion y GitHub (mocks)."""

from unittest.mock import MagicMock, patch

from src.integrations.github.client import GitHubClient
from src.integrations.notion.client import NotionClient


@patch("src.integrations.notion.client.settings")
@patch("src.integrations.notion.client.requests.request")
def test_notion_search(mock_request, mock_settings):
    mock_settings.notion_enabled = True
    mock_settings.notion_api_key = "secret"
    mock_settings.notion_version = "2022-06-28"
    mock_settings.notion_database_id = ""
    mock_settings.notion_parent_page_id = ""

    response = MagicMock()
    response.status_code = 200
    response.text = '{"results": []}'
    response.json.return_value = {"results": []}
    mock_request.return_value = response

    client = NotionClient()
    result = client.search("Chain Industria")
    assert result.success
    assert result.provider == "notion"


@patch("src.integrations.github.client.settings")
@patch("src.integrations.github.client.requests.request")
def test_github_list_issues(mock_request, mock_settings):
    mock_settings.github_enabled = True
    mock_settings.github_token = "ghp_test"
    mock_settings.github_repo = "org/repo"
    mock_settings.github_api_url = "https://api.github.com"

    response = MagicMock()
    response.status_code = 200
    response.text = '[{"number": 1, "title": "Test", "state": "open", "html_url": "http://x"}]'
    response.json.return_value = [
        {"number": 1, "title": "Test", "state": "open", "html_url": "http://x"}
    ]
    mock_request.return_value = response

    client = GitHubClient()
    result = client.list_issues()
    assert result.success
    assert len(result.data) == 1


@patch("src.integrations.notion.client.settings")
def test_notion_disabled_without_key(mock_settings):
    mock_settings.notion_enabled = False
    client = NotionClient()
    result = client.search("test")
    assert not result.success
    assert "NOTION_API_KEY" in (result.error or "")
