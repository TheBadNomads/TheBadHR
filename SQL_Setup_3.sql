ALTER TABLE leaveTypesWithBalance
DROP COLUMN starting_balance

sp_rename 'leaveTypesWithBalance', 'leaveTypes'