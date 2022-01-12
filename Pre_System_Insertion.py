import csv
import Utilities as utils
import pandas
import os
import re

import datetime
from Leave import leave_interface, leave_db

input_path = input("Please enter the input path of your csv file:\n")
output_path = re.sub('.csv$', '_modified.csv', input_path)

members_dic = {
    "Ant"     : 158010930200838144,
    "Amr"     : 487749805636976651,
    "Alex"    : 475048962869428250,
    "Abdo"    : 202837588397129728,
    "Alberto" : 155752025798344704,
    "Noah"    : 252146643388858370,
    "Moody"   : 855503936365920296,
    "Hawas"   : 504953339067498496,
    "Brian"   : 174932293134188544,
    "Omar"    : 757347719135363192
}
automatic_leave_id = -1

def CreateNewHeader():
    file = open(input_path, 'r')
    data = csv.reader(file, delimiter = "\t")
    headers = next(data)[0].split(',')
    headers.pop(-1)
    headers.pop(-2)
    months = ["April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for i in range(9):
        headers[i + 1] = months[i]
    headers[0] = "Name"
    headers.append("is_emergency")
    return headers

def CreateNewBody():
    file = open(input_path, 'r')
    data = csv.reader(file, delimiter = "\t")
    body = []
    is_emergency = False
    for line in data:
        cols = line[0].split(',')
        header_name = cols[0]
        cols.pop(-1)
        cols.pop(-2)

        if header_name == "Total Leaves":
            break
        
        if header_name == "Emergency Leave":
            is_emergency = True

        if header_name == "Leave":
            is_emergency = False

        if header_name in members_dic:
            cols = ["0.0" if days_count == '' else days_count for days_count in cols]
            cols.append(is_emergency)
            body.append(cols)
    return body

def CreateNewSheet(header, body = None):
    file = open(output_path, 'w')
    writer = csv.writer(file)
    writer.writerow(header)
    for line in body:
        writer.writerow(line)
    file.close()
    return file.name

def InsertDataIntoDBFromCSV(file_name):
    df = pandas.read_csv(file_name)
    for index, row in df.iterrows():
        member_id = members_dic[row[0]]
        is_emergency = row[-1]
        for col in row.index[1:]:
            if col == "is_emergency":
                continue
            days_count = float(row[col])
            if days_count <= 0.0 :
                continue

            date = datetime.datetime(2021, datetime.datetime.strptime(col, '%B').month, 1)
            days_count_int_part = int(days_count)
            days_count_float_part = float(days_count - days_count_int_part)
            if days_count_float_part <= 0.0:
                InsertLeavesIntoDB(days_count_int_part, member_id, date, is_emergency)
            else:
                InsertLeavesIntoDB(days_count_int_part + 1, member_id, date, is_emergency)
                InsertExtraBalance(days_count_float_part, member_id, date)

def InsertLeavesIntoDB(days_count, member_id, date, is_emergency):
    if date.weekday() in [4, 5]:
        date = GetNextWeekDay(date)
    for i in range(days_count):
        leave_interface.AddRetroactiveLeaveToDB(member_id, automatic_leave_id, date, date, "Annual", "Approved", "", is_emergency, None)

def GetNextWeekDay(date):
    days_ahead = 6 - date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)
 
def InsertExtraBalance(days_count, member_id, date):
    finance_admin_id = int(os.getenv("Finance_Admins_ids").split(", ")[0])
    leave_db.InsertExtraBalance(date, finance_admin_id, member_id, "Annual", "", days_count)

def MainFunction():
    sheet_name = CreateNewSheet(CreateNewHeader(), CreateNewBody())
    InsertDataIntoDBFromCSV(sheet_name)
    os.remove(output_path)

MainFunction()
