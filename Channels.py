import os

class LeaveChannels:

    LeaveApprovalsChannel = None

    @staticmethod
    async def GetLeaveApprovalsChannel(client):
        if(LeaveChannels.LeaveApprovalsChannel == None):
            LeaveChannels.LeaveApprovalsChannel = await client.fetch_channel(int(os.getenv("TestChannel_id")))

        return LeaveChannels.LeaveApprovalsChannel