CREATE TABLE leaveTypesWithBalance (
    [name] varchar(255) NOT NULL PRIMARY KEY,
    [starting_balance] float NOT NULL
);

CREATE TABLE leaveStatus (
    [name] varchar(255) NOT NULL PRIMARY KEY
);

CREATE TABLE members (
    id bigint NOT NULL PRIMARY KEY,
    [name] varchar(255) NOT NULL,
    [email] varchar(255) NOT NULL,
    [start_date] datetime,
    [leave_date] datetime
);

CREATE TABLE leaves (
    id int NOT NULL IDENTITY(1,1) PRIMARY KEY,
    [member_id] bigint NOT NULL FOREIGN KEY REFERENCES members(id),
    [request_id] bigint NOT NULL,
    [leave_type] varchar(255) NOT NULL FOREIGN KEY REFERENCES leaveTypesWithBalance(name),
    [date] datetime NOT NULL,
    [reason] varchar(255),
    [remark] varchar(255),
    [leave_status] varchar(255) NOT NULL FOREIGN KEY REFERENCES leaveStatus(name)
);

CREATE TABLE leavesBalance (
    id int NOT NULL IDENTITY(1,1) PRIMARY KEY,
    [member_id] bigint NOT NULL FOREIGN KEY REFERENCES members(id),
    [leave_type] varchar(255) NOT NULL FOREIGN KEY REFERENCES leaveTypesWithBalance(name),
    [balance] float NOT NULL
);

CREATE TABLE Captions (
    id int NOT NULL IDENTITY(1,1) PRIMARY KEY,
    [caption_title] varchar(255) NOT NULL UNIQUE,
    [caption_message_en] varchar(255) NOT NULL,
);

INSERT INTO leaveTypesWithBalance (name, starting_balance) VALUES ('Annual', 21);
INSERT INTO leaveTypesWithBalance (name, starting_balance) VALUES ('Emergency', 5);
INSERT INTO leaveTypesWithBalance (name, starting_balance) VALUES ('Sick', 365);
INSERT INTO leaveTypesWithBalance (name, starting_balance) VALUES ('Unpaid', 365);

INSERT INTO leaveStatus (name) VALUES ('Pending');
INSERT INTO leaveStatus (name) VALUES ('Approved');
INSERT INTO leaveStatus (name) VALUES ('Rejected');

INSERT INTO Captions (caption_title, caption_message_en) VALUES ('LeaveRequestSent', 'Your leave request has been sent');
INSERT INTO Captions (caption_title, caption_message_en) VALUES ('LeaveRequestApproved', 'Your leave request was approved');
INSERT INTO Captions (caption_title, caption_message_en) VALUES ('LeaveRequestRejected', 'Your leave request was rejected');
INSERT INTO Captions (caption_title, caption_message_en) VALUES ('InvalidDatesError', 'Please select valid dates');
INSERT INTO Captions (caption_title, caption_message_en) VALUES ('LeaveRequestFailedError', 'Your Request has failed, try again later');
INSERT INTO Captions (caption_title, caption_message_en) VALUES ('NotEnoughBalanceError', 'You dont have enough leaves to request');