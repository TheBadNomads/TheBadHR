ALTER TABLE leaves
ADD is_emergency BIT NOT NULL;
ADD is_unpaid BIT NOT NULL;

DELETE FROM leavesBalance WHERE leave_type = 'Emergency';
DELETE FROM leavesBalance WHERE leave_type = 'Unpaid';

DELETE FROM leaveTypesWithBalance WHERE name = 'Emergency';
DELETE FROM leaveTypesWithBalance WHERE name = 'Unpaid';
