ALTER TABLE leaves
ADD is_emergency BIT NOT NULL;

DELETE FROM leavesBalance WHERE leave_type = 'Emergency';

DELETE FROM leaveTypesWithBalance WHERE name = 'Emergency';