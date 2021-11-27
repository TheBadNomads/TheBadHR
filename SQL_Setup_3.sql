sp_rename 'leaveTypesWithBalance', 'leaveTypes'

ALTER TABLE leaveTypes
DROP COLUMN starting_balance;

DELETE FROM leavesBalance WHERE leave_type = 'Sick';

DROP TABLE leavesBalance