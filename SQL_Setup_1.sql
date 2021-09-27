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

INSERT INTO leaveTypesWithBalance (name, starting_balance) VALUES ('Annual', 21);
INSERT INTO leaveTypesWithBalance (name, starting_balance) VALUES ('Emergency', 5);
INSERT INTO leaveTypesWithBalance (name, starting_balance) VALUES ('Sick', 365);
INSERT INTO leaveTypesWithBalance (name, starting_balance) VALUES ('Unpaid', 365);

INSERT INTO leaveStatus (name) VALUES ('Pending');
INSERT INTO leaveStatus (name) VALUES ('Approved');
INSERT INTO leaveStatus (name) VALUES ('Rejected');