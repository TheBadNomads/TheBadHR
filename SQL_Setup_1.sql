CREATE TABLE leaveTypes (
    id int NOT NULL IDENTITY(1,1) PRIMARY KEY,
    [name] varchar(255) NOT NULL
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
    [leave_type] int NOT NULL FOREIGN KEY REFERENCES leaveTypes(id),
    [leave_status] varchar(50) NOT NULL,
    [date] datetime NOT NULL,
    [reason] varchar(255),
    [remark] varchar(255)
);

CREATE TABLE leavesBalance (
    id int NOT NULL IDENTITY(1,1) PRIMARY KEY,
    [member_id] bigint NOT NULL FOREIGN KEY REFERENCES members(id),
    [leave_type] int NOT NULL FOREIGN KEY REFERENCES leaveTypes(id),
    [balance] float NOT NULL
);

INSERT INTO leaveTypes (name) VALUES ('Annual');
INSERT INTO leaveTypes VALUES ('Emergency');
INSERT INTO leaveTypes VALUES ('Sick');
INSERT INTO leaveTypes VALUES ('Unpaid');