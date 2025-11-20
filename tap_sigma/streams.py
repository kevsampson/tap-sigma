"""Stream definitions for Sigma Computing API."""

from typing import Any, Dict, Optional

from singer_sdk import typing as th

from tap_sigma.client import SigmaStream


class AccountTypesStream(SigmaStream):
    """Account types stream."""

    name = "account_types"
    path = "/v2/account-types"
    primary_keys = ["accountTypeId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("accountTypeId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedAt", th.DateTimeType),
    ).to_dict()


class ConnectionsStream(SigmaStream):
    """Connections stream."""

    name = "connections"
    path = "/v2/connections"
    primary_keys = ["connectionId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("connectionId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("type", th.StringType),
        th.Property("description", th.StringType),
        th.Property("createdBy", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedBy", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
        th.Property("host", th.StringType),
        th.Property("port", th.IntegerType),
        th.Property("database", th.StringType),
        th.Property("schema", th.StringType),
        th.Property("warehouse", th.StringType),
        th.Property("role", th.StringType),
        th.Property("account", th.StringType),
        th.Property("useOAuth", th.BooleanType),
    ).to_dict()


class DatasetsStream(SigmaStream):
    """Datasets stream."""

    name = "datasets"
    path = "/v2/datasets"
    primary_keys = ["datasetId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("datasetId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("createdBy", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedBy", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
        th.Property("connectionId", th.StringType),
        th.Property("badge", th.StringType),
        th.Property("isSample", th.BooleanType),
    ).to_dict()


class DataModelsStream(SigmaStream):
    """Data models stream."""

    name = "data_models"
    path = "/v2/data-models"
    primary_keys = ["dataModelId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("dataModelId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("createdBy", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedBy", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
    ).to_dict()


class MembersStream(SigmaStream):
    """Members stream."""

    name = "members"
    path = "/v2/members"
    primary_keys = ["memberId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("memberId", th.StringType),
        th.Property("email", th.StringType),
        th.Property("firstName", th.StringType),
        th.Property("lastName", th.StringType),
        th.Property("type", th.StringType),
        th.Property("isActive", th.BooleanType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedAt", th.DateTimeType),
    ).to_dict()


class TeamsStream(SigmaStream):
    """Teams stream."""

    name = "teams"
    path = "/v2/teams"
    primary_keys = ["teamId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("teamId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("createdBy", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedBy", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
    ).to_dict()


class FilesStream(SigmaStream):
    """Files stream."""

    name = "files"
    path = "/v2/files"
    primary_keys = ["inodeId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("inodeId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("path", th.StringType),
        th.Property("type", th.StringType),
        th.Property("createdBy", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedBy", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
        th.Property("parentInodeId", th.StringType),
        th.Property("badge", th.StringType),
    ).to_dict()


class WorkbooksStream(SigmaStream):
    """Workbooks stream."""

    name = "workbooks"
    path = "/v2/workbooks"
    primary_keys = ["workbookId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("workbookId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("url", th.StringType),
        th.Property("path", th.StringType),
        th.Property("createdBy", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedBy", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
        th.Property("latestVersion", th.IntegerType),
        th.Property("badge", th.StringType),
    ).to_dict()


class WorkbookPagesStream(SigmaStream):
    """Workbook pages stream (child of workbooks)."""

    name = "workbook_pages"
    primary_keys = ["workbookId", "pageId"]
    replication_key = None
    parent_stream_type = WorkbooksStream

    @property
    def path(self) -> str:
        """Return the path for this stream."""
        return "/v2/workbooks/{workbookId}/pages"

    def get_url_params(
        self,
        context: Optional[Dict] = None,
        next_page_token: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get URL parameters including parent context."""
        params = super().get_url_params(context, next_page_token)
        return params

    schema = th.PropertiesList(
        th.Property("workbookId", th.StringType),
        th.Property("pageId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("createdBy", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedBy", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
    ).to_dict()

    def post_process(self, row: dict, context: Optional[Dict] = None) -> dict:
        """Add workbookId from context to each page record."""
        if context and "workbookId" in context:
            row["workbookId"] = context["workbookId"]
        return row


class FavoritesStream(SigmaStream):
    """Favorites stream."""

    name = "favorites"
    path = "/v2/favorites"
    primary_keys = ["favoriteId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("favoriteId", th.StringType),
        th.Property("inodeId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("type", th.StringType),
        th.Property("url", th.StringType),
        th.Property("createdBy", th.StringType),
        th.Property("createdAt", th.DateTimeType),
    ).to_dict()


class TagsStream(SigmaStream):
    """Tags stream."""

    name = "tags"
    path = "/v2/tags"
    primary_keys = ["tagId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("tagId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("inodeId", th.StringType),
        th.Property("version", th.IntegerType),
        th.Property("createdBy", th.StringType),
        th.Property("createdAt", th.DateTimeType),
    ).to_dict()


class UserAttributesStream(SigmaStream):
    """User attributes stream."""

    name = "user_attributes"
    path = "/v2/user-attributes"
    primary_keys = ["userAttributeId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("userAttributeId", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("defaultValue", th.StringType),
        th.Property("createdBy", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedBy", th.StringType),
        th.Property("updatedAt", th.DateTimeType),
    ).to_dict()


class WhoAmIStream(SigmaStream):
    """WhoAmI stream - returns current authenticated user info."""

    name = "whoami"
    path = "/v2/whoami"
    primary_keys = ["memberId"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("memberId", th.StringType),
        th.Property("email", th.StringType),
        th.Property("firstName", th.StringType),
        th.Property("lastName", th.StringType),
        th.Property("organizationId", th.StringType),
        th.Property("organizationName", th.StringType),
    ).to_dict()
