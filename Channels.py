import os

class Channels:

    LeaveApprovalsChannel = None

    @staticmethod
    async def GetLeaveApprovalsChannel(client):
        if(Channels.LeaveApprovalsChannel == None):
            Channels.LeaveApprovalsChannel = await client.fetch_channel(int(os.getenv("TestChannel_id")))

        return Channels.LeaveApprovalsChannel