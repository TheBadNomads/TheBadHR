import os

class LeaveChannels:

    LeaveRequestsChannel = None

    @staticmethod
    async def GetLeaveRequestsChannel(client):
        if(LeaveChannels.LeaveRequestsChannel == None):
            LeaveChannels.LeaveRequestsChannel = await client.fetch_channel(int(os.getenv("TestChannel_id")))

        return LeaveChannels.LeaveRequestsChannel