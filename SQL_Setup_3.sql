sp_rename 'leaveTypesWithBalance', 'leaveTypes'

ALTER TABLE leaveTypes
DROP COLUMN starting_balance;

DELETE FROM leavesBalance WHERE leave_type = 'Sick';

DROP TABLE leavesBalance

CREATE TABLE extraBalance (
    id int NOT NULL IDENTITY(1,1) PRIMARY KEY,
    [creditor_id] bigint NOT NULL FOREIGN KEY REFERENCES members(id),
    [receiver_id] bigint NOT NULL,
    [leave_type] varchar(255) NOT NULL FOREIGN KEY REFERENCES leaveTypes(name),
    [date] datetime NOT NULL,
    [reason] varchar(255),
    [days_count] float NOT NULL
);
