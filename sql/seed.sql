DELETE FROM organisation;

INSERT INTO organisation
    (Name, Type)
VALUES
    ('IITH', 'Insti'),
    ('Infero', 'Club');

INSERT INTO course
    (kyc, type, title, courseCode, orgId)
VALUES
    ('Learn Basic C in 2 weeks', 'practice', 'Basic C', 'INF000', 15),
    ('Not learn C in one sem', 'practice', 'IDP', 'ID1303', 14);

SELECT *
FROM Organisation;

DELETE FROM Slot;

INSERT INTO Slot
    (orgId, SlotCode)
VALUES
    (14, 'A'),
    (15, 'GN');

INSERT INTO SlotSchedule
    (slotId, day, startTime, endTime)
VALUES
    (2, 1, '21:00:00', '23:59:00'),
    (2, 2, '21:00:00', '23:59:00'),
    (2, 3, '21:00:00', '23:59:00'),
    (2, 4, '21:00:00', '23:59:00'),
    (2, 5, '21:00:00', '23:59:00'),
    (2, 6, '21:00:00', '23:59:00'),
    (3, 5, '00:00:00', '02:00:00'),
    (4, 5, '02:00:00', '05:00:00'),
    (1, 1, '09:00:00', '10:00:00');

SELECT *
FROM SlotSchedule INNER JOIN slot ON slot.slotId = slotSchedule.slotId;

INSERT INTO Offering
    (courseId, referenceBooks, gradingScheme, instructor, slotId, startDate, endDate, previousOfferingId)
VALUES
    (1, 'Slides', 'Lite', 'megatron10', 2, '2021-01-01', '2021-01-15', NULL);

SELECT *
FROM Offering INNER JOIN Course ON Offering.courseId = Course.courseId;

INSERT INTO Usr
    (email, token)
VALUES
    ('megatron10599@gmail.com', '{"key": "1"}');

SELECT *
FROM Usr;

INSERT INTO Subscriptions
    (userId, offeringId)
VALUES
    (1, 1);

SELECT *
FROM (Subscriptions INNER JOIN Usr ON Subscriptions.userId = Usr.userId)
    INNER JOIN
    Offering
    ON Subscriptions.offeringId = Offering.offeringId;

INSERT INTO Resources
    (offeringId, userId, type, link, about)
VALUES
    (1, 1, 'slides', 'dummyLink', 'basic C slides');

SELECT *
FROM Resources;