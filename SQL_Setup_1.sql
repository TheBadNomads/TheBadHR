CREATE TABLE leaveTypes (
    [name] varchar(255) NOT NULL PRIMARY KEY
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
    [leave_type] varchar(255) NOT NULL FOREIGN KEY REFERENCES leaveTypes(name),
    [leave_status] varchar(255) NOT NULL FOREIGN KEY REFERENCES leaveStatus(name),
    [date] datetime NOT NULL,
    [reason] varchar(255),
    [remark] varchar(255)
);

CREATE TABLE leavesBalance (
    id int NOT NULL IDENTITY(1,1) PRIMARY KEY,
    [member_id] bigint NOT NULL FOREIGN KEY REFERENCES members(id),
    [leave_type] varchar(255) NOT NULL FOREIGN KEY REFERENCES leaveTypes(name),
    [balance] float NOT NULL
);

INSERT INTO leaveTypes (name) VALUES ('Annual');
INSERT INTO leaveTypes (name) VALUES ('Emergency');
INSERT INTO leaveTypes (name) VALUES ('Sick');
INSERT INTO leaveTypes (name) VALUES ('Unpaid');