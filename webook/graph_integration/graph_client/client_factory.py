from azure.identity.aio import DefaultAzureCredential
from kiota_authentication_azure.azure_identity_authentication_provider import (
    AzureIdentityAuthenticationProvider,
)
from django.conf import settings
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient, GraphRequestAdapter


def create_graph_service_client() -> GraphServiceClient:
    """
    Create a new instance of Graph Service Client

    Returns:
        An instance of GraphServiceClient

    Raises:
        Exception if any of the required environment variables are missing
    """
    tenant_id = settings.AZURE_TENANT_ID
    client_id = settings.AZURE_CLIENT_ID
    client_secret = settings.AZURE_CLIENT_SECRET

    if not all([ tenant_id, client_id, client_secret ]):
        raise Exception("Configuration values missing, Graph Service client can not be instantiated.")

    credential = ClientSecretCredential(
        tenant_id=settings.AZURE_TENANT_ID,
        client_id=settings.AZURE_CLIENT_ID,
        client_secret=settings.AZURE_CLIENT_SECRET
    )

    return GraphServiceClient(credentials=credential)
