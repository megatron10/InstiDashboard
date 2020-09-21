CREATE TABLE Organisation
(
    orgId serial PRIMARY KEY,
    name TEXT not null,
    type TEXT,
    UNIQUE(name)
);

CREATE TABLE Slot
(
    slotId serial PRIMARY KEY,
    slotCode VARCHAR(6),
    orgId INT,
    UNIQUE(orgId, slotCode),
    FOREIGN KEY(orgId)
        REFERENCES Organisation(orgId)
);

CREATE TABLE SlotSchedule
(
    slotId INT,
    day INT,
    startTime TIME,
    endTime TIME,
    PRIMARY KEY(slotId, day),
    FOREIGN KEY(slotId) REFERENCES Slot
);

CREATE TABLE Course
(
    courseId serial PRIMARY KEY,
    kyc text,
    type text,
    -- theory, practice, both
    title text,
    courseCode text,
    orgId INT,
    FOREIGN KEY(orgId)
        REFERENCES Organisation(orgId),
    UNIQUE(courseCode, orgId)
);

CREATE TABLE Offering
(
    offeringId serial PRIMARY KEY,
    courseId INT,

    practiceRating REAL DEFAULT 0.0,
    contentRating REAL DEFAULT 0.0,
    thoeryRating REAL DEFAULT 0.0,
    litemeter REAL DEFAULT 0.0,
    nratings INT DEFAULT 0,

    referenceBooks TEXT,
    gradingScheme TEXT,
    instructor TEXT,

    slotId INT,
    startDate DATE,
    endDate DATE,

    previousOfferingId INT DEFAULT NULL,

    FOREIGN KEY(courseId)
        REFERENCES Course(courseId),

    FOREIGN KEY(previousOfferingId)
        REFERENCES Offering(offeringId),

    FOREIGN KEY(slotId)
        REFERENCES Slot(slotId)
);

CREATE TABLE Usr
(
    userId serial PRIMARY KEY,
    email TEXT UNIQUE,
    token JSON
);

CREATE TABLE Resources
(
    resourceId serial PRIMARY KEY,
    offeringId INT,
    userId INT,
    type TEXT,
    --test, quiz, exam, midsem, tutorial, assignment
    link TEXT,
    --optional
    about TEXT,

    FOREIGN KEY(offeringId)
        REFERENCES Offering(offeringId),

    FOREIGN KEY(userId)
        REFERENCES Usr(userId)
);

CREATE TABLE Subscriptions
(
    userId INT not null,
    offeringId INT not null,

    FOREIGN KEY(userId)
        REFERENCES Usr(userId),

    FOREIGN KEY(offeringId)
        REFERENCES Offering(offeringId)
);