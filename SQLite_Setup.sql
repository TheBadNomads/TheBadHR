CREATE TABLE leaveTypes (
    name varchar(255) NOT NULL PRIMARY KEY,
    starting_balance float NOT NULL
);

CREATE TABLE leaveStatus (
    name varchar(255) NOT NULL PRIMARY KEY
);

CREATE TABLE members (
    id bigint NOT NULL PRIMARY KEY,
    name varchar(255) NOT NULL,
    email varchar(255) NOT NULL,
    start_date TIMESTAMP,
    leave_date TIMESTAMP
);

CREATE TABLE leaves (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    member_id bigint NOT NULL,
    request_id bigint NOT NULL,
    leave_type varchar(255) NOT NULL,
    date TIMESTAMP NOT NULL,
    reason varchar(255),
    remark varchar(255),
    leave_status varchar(255) NOT NULL,
    is_emergency BOOLEAN NOT NULL CHECK (is_emergency IN (0, 1)),
    is_paid BOOLEAN NOT NULL CHECK (is_paid IN (0, 1)),
    FOREIGN KEY (leave_type) REFERENCES leaveTypes(name),
    FOREIGN KEY (member_id) REFERENCES members(id),
    FOREIGN KEY (leave_status) REFERENCES leaveStatus(name)
);

CREATE TABLE Captions (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    caption_title varchar(255) NOT NULL UNIQUE,
    caption_message_en varchar(255) NOT NULL
);

CREATE TABLE extraBalance (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    date TIMESTAMP NOT NULL,
    creditor_id bigint NOT NULL,
    recipient_id bigint NOT NULL,
    leave_type varchar(255) NOT NULL,
    reason varchar(255),
    days_count float NOT NULL,
    FOREIGN KEY (creditor_id) REFERENCES members(id),
    FOREIGN KEY (leave_type) REFERENCES leaveTypes(name)
);



INSERT INTO leaveStatus (name)
VALUES ('Pending');

INSERT INTO leaveStatus (name)
VALUES ('Approved');

INSERT INTO leaveStatus (name)
VALUES ('Rejected');

INSERT INTO leaveTypes (name, starting_balance)
VALUES ('Annual', 21);

INSERT INTO leaveTypes (name, starting_balance)
VALUES ('Sick', 365);

INSERT INTO Captions (caption_title, caption_message_en)
VALUES ('LeaveRequestSent', 'Your leave request has been sent');

INSERT INTO Captions (caption_title, caption_message_en)
VALUES ('LeaveRequestApproved', 'Your leave request was approved');

INSERT INTO Captions (caption_title, caption_message_en)
VALUES ('LeaveRequestRejected', 'Your leave request was rejected');

INSERT INTO Captions (caption_title, caption_message_en)
VALUES ('InvalidDatesError', 'Please select valid dates');

INSERT INTO Captions (caption_title, caption_message_en)
VALUES ('LeaveRequestFailedError', 'Your Request has failed, try again later');

INSERT INTO Captions (caption_title, caption_message_en)
VALUES ('NotEnoughBalanceError', 'You dont have enough leaves to request');