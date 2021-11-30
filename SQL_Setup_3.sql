sp_rename 'leaveTypesWithBalance', 'leaveTypes'

ALTER TABLE leaveTypes
DROP COLUMN starting_balance;

DROP TABLE leavesBalance

CREATE TABLE extraBalance (
    id int NOT NULL IDENTITY(1,1) PRIMARY KEY,
    [date] datetime NOT NULL,
    [creditor_id] bigint NOT NULL FOREIGN KEY REFERENCES members(id),
    [recipient_id] bigint NOT NULL,
    [leave_type] varchar(255) NOT NULL FOREIGN KEY REFERENCES leaveTypes(name),
    [reason] varchar(255),
    [days_count] float NOT NULL
);
