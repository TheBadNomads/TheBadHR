import datetime
import Utilities as utils
import os
import UI
import collections
import hikari

from Channels import Channels
from hikari.emojis import Emoji
from db import db
from Leave import leave_db

async def ProcessLeaveRequest(ctx, member, client, leave_type, start_date, end_date, reason):
    is_request_valid, message = IsLeaveRequestValid(member.id, start_date, end_date)
    if is_request_valid:
        return await SubmitRequest(ctx, member, client, start_date, end_date, leave_type, reason)   
        
    else:
        return message

async def SubmitRequest(ctx, member, client, start_date, end_date, leave_type, reason):
    message_id = await SendLeaveRequestToChannel(ctx, client, start_date, end_date, leave_type, reason)
    return AddLeaveRequestToDB(member, message_id, start_date, end_date, leave_type, "Pending", reason)
    
async def SendLeaveRequestToChannel(ctx, client, start_date, end_date, leave_type, reason):
    embed = UI.CreateLeaveEmbed(ctx, start_date, end_date, leave_type, reason)
    #channel = Channels.GetLeaveApprovalsChannel(client)
    reply = await ctx.respond(embed = embed)
    msg = await reply.message()
    await AddEmojisToLeaveMessage(msg)
    return msg.id

def AddLeaveRequestToDB(member, message_id, start_date, end_date, leave_type, leave_status, reason):
    work_days = utils.GetWorkDays(start_date, end_date)
    remaining_emergency_count = leave_db.GetRemainingEmergencyLeavesCount(member.id)
    annual_leave_balance = leave_db.GetAnnualLeaveBalance(member.id)
    for day in work_days:
        is_emergency = utils.IsEmergencyLeave(day, leave_type)
        is_unpaid = utils.IsUnpaidLeave(leave_type, annual_leave_balance, is_emergency, remaining_emergency_count)
        if ((leave_type == "Annual") and not (is_unpaid)):
            annual_leave_balance -= 1
        leave_db.InsertLeave(member.id, message_id, leave_type, day, reason, "", leave_status, is_emergency, is_unpaid)
    return (db.GetCaption(1))
                
async def HandleLeaveReactions(client, payload, token):
    message = await client.rest.fetch_message(payload.channel_id, payload.message_id)

    embed = message.embeds[0]

    action = UI.ParseEmoji(payload.emoji_id)
    if action == None:
        return

    if payload.member.is_bot:
        return
    
    if not (utils.IsAdmin(payload.member)):
        return
        
    if action == "Reverted":
        if not (leave_db.IsLeaveRequestPending(payload.message_id)):
            leave_db.UpdateLeaveStatus(payload.message_id, "Pending")
            await UI.UpdateLeaveEmbed(client, payload.member, embed, "Pending", payload.channel_id, payload.message_id, token)
            await InformMemberAboutLeaveStatus(client, payload.message_id, embed, payload.member, action, token)
            await message.remove_all_reactions()
            await AddEmojisToLeaveMessage(message)
    elif leave_db.IsLeaveRequestPending(payload.message_id):
        leave_db.UpdateLeaveStatus(payload.message_id, action)
        await UI.UpdateLeaveEmbed(client, payload.member, embed, action, payload.channel_id, payload.message_id, token)
        await InformMemberAboutLeaveStatus(client, payload.message_id, embed, payload.member, action, token)

async def InformMemberAboutLeaveStatus(client, request_id, embed, admin, status, token):
    member = await client.rest.fetch_user(utils.GetMemberIDFromEmbed(embed))

    reason = utils.GetFieldFromEmbed(client, embed, "reason")
    leave_type = utils.GetFieldFromEmbed(client, embed, "leave type")
    start_date = utils.GetFieldFromEmbed(client, embed, "start date")
    end_date = utils.GetFieldFromEmbed(client, embed, "end date")

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    reply_embed = UI.CreateInformMemberOfLeaveStatusEmbed(request_id, status, admin.display_name, reason, leave_type, start_date, end_date)
    channel = await client.rest.create_dm_channel(member)
    await channel.send(embed = reply_embed)

def GetRequestedLeavesBetween(member_id, start_date, end_date):
    work_days = utils.GetWorkDays(start_date, end_date)
    previous_leaves = leave_db.GetLeavesByMemberID(member_id)
    requested_leaves = []
    for leave in previous_leaves:
        if (leave["date"] in work_days):
           requested_leaves.append(leave)
    return requested_leaves

def IsLeaveRequestValid(member_id, start_date, end_date):
    if end_date < start_date:
        return (False, (db.GetCaption(3)))

    if (len(utils.GetWorkDays(start_date, end_date)) <= 0):
        return (False, ("This request consists of Holidays/Weekends ONLY"))

    previously_requested_days = utils.FilterOutLeavesByStatus(GetRequestedLeavesBetween(member_id, start_date, end_date), "rejected")
    if len(previously_requested_days) > 0:
        return (False, (f"Leave request already exists for {utils.ConvertDatesToStrings(utils.GetDatesOfLeaves(previously_requested_days))}"))
        
    return (True, "Success")

async def InsertRetroactiveLeave(member, message_id, start_date, end_date, leave_type, is_requested_late, is_unpaid_retroactive, reason):
    is_request_valid, message = IsLeaveRequestValid(member.id, start_date, end_date)
    print(is_request_valid)
    if is_request_valid:
        result = AddRetroactiveLeaveToDB(member.id, message_id, start_date, end_date, leave_type, "Approved", reason, is_requested_late, is_unpaid_retroactive)
        return result

    return message

def AddRetroactiveLeaveToDB(member_id, message_id, start_date, end_date, leave_type, leave_status, reason, is_emergency, is_unpaid):
    work_days = utils.GetWorkDays(start_date, end_date)
    remaining_emergency_count = leave_db.GetRemainingEmergencyLeavesCount(member_id)
    annual_leave_balance = leave_db.GetAnnualLeaveBalance(member_id)
    for day in work_days:
        is_unpaid = ((is_unpaid) or (utils.IsUnpaidLeave(leave_type, annual_leave_balance, is_emergency, remaining_emergency_count)))
        if ((leave_type == "Annual") and not (is_unpaid)):
            annual_leave_balance -= 1
        leave_db.InsertLeave(member_id, message_id, leave_type, day, reason, "", leave_status, is_emergency, is_unpaid)
    return ("Retroactive leave was inserted successfully")

def GetLeavesAcrossRange(start_date, end_date, member):
    leaves_group = GroupLeavesBy(leave_db.GetLeavesBetween(start_date, end_date, member), 'member_id')
    ordered_leaves = []
    for leaves_array in leaves_group:
        leaves_sub_group = GroupLeavesBy(leaves_array, 'request_id')
        ordered_leaves.append(leaves_sub_group)
    return ordered_leaves

def GroupLeavesBy(leaves, col_name):
    ordered_leaves = collections.defaultdict(list)
    for leave in leaves:
        ordered_leaves[leave[col_name]].append(leave)
    return list(ordered_leaves.values())

def IsMemberWorking(member_id, date):
    work_days = utils.GetWorkDays(date, date)
    if len(work_days) <= 0:
        return (False, "Holiday/Weekend")

    is_member_on_leave, reason = IsMemberOnLeave(member_id, date)
    if is_member_on_leave:
        return (False, reason)
        
    return (True, "Member is working on the selected date")

def IsMemberOnLeave(member_id, date):
    approved_leaves = list(filter(lambda leave: leave['date'] == date and leave['leave_status'] == "Approved", leave_db.GetLeavesByMemberID(member_id)))
    if (len(approved_leaves) <= 0):
        return (False, "Member is working on the selected date")
    return (True, GetReasonOfLeaves(approved_leaves))   

def GetReasonOfLeaves(leaves_array):
    if len(leaves_array) <= 0:
        return None

    return leaves_array[0]["reason"]

async def AddEmojisToLeaveMessage(message):
    await message.add_reaction(Emoji.parse(os.getenv("Approve_Emoji")))
    await message.add_reaction(Emoji.parse(os.getenv("Reject_Emoji")))
    await message.add_reaction(Emoji.parse(os.getenv("Revert_Emoji")))
