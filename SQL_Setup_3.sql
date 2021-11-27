sp_rename 'leaveTypesWithBalance', 'leaveTypes'

ALTER TABLE leaveTypes
DROP COLUMN starting_balance;