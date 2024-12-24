from google.apps import meet_v2
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/meetings.space.created']
creds = Credentials.from_authorized_user_file('token.json', SCOPES)


# TODO(developer) - Надо переделать на получение токена из .env.
async def sample_create_space():
    # Create a client
    client = meet_v2.SpacesServiceAsyncClient(credentials=creds)
    # Initialize request argument(s)
    request = meet_v2.CreateSpaceRequest(
    )
    request.space.config.access_type = 1
    # Make the request
    response = await client.create_space(request=request)
    # Handle the response
    return response


async def sample_get_space(name):
    # Create a client
    client = meet_v2.SpacesServiceAsyncClient(credentials=creds)

    # Initialize request argument(s)
    request = meet_v2.GetSpaceRequest(
        name=name,
    )

    # Make the request
    response = await client.get_space(request=request)

    # Handle the response
    return response


async def sample_list_conference_records():
    # Create a client
    client = meet_v2.ConferenceRecordsServiceAsyncClient(credentials=creds)

    # Initialize request argument(s)
    request = meet_v2.ListConferenceRecordsRequest(
    )

    # Make the request
    page_result = await client.list_conference_records(request=request)

    # Handle the response
    return page_result


async def end(sapace):
    client = meet_v2.SpacesServiceAsyncClient(credentials=creds)

    # Initialize request argument(s)
    request = meet_v2.EndActiveConferenceRequest(
        name=sapace,
    )

    # Make the request
    await client.end_active_conference(request=request)


async def sample_list_participants(name):
    # Create a client
    client = meet_v2.ConferenceRecordsServiceAsyncClient(credentials=creds)

    # Initialize request argument(s)
    request = meet_v2.ListParticipantsRequest(
        parent=name,
    )

    # Make the request
    page_result = await client.list_participants(request=request)

    # Handle the response
    async for response in page_result:
        print(response)


async def sample_get_conference_record(name):
    # Create a client
    client = meet_v2.ConferenceRecordsServiceAsyncClient(credentials=creds)

    # Initialize request argument(s)
    request = meet_v2.GetConferenceRecordRequest(
        name=name,
    )

    # Make the request
    response = await client.get_conference_record(request=request)

    # Handle the response
    return response


async def sample_update_space():
    # Create a client
    client = meet_v2.SpacesServiceAsyncClient(credentials=creds)

    # Initialize request argument(s)
    request = meet_v2.UpdateSpaceRequest(
    )

    # Make the request
    response = await client.update_space(request=request)

    # Handle the response
    print(response)
