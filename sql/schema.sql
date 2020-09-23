DROP TABLE IF EXISTS manager, subscription, rating, resource, usr, offering, course, slot_schedule, slot, organisation;

CREATE TABLE organisation
(
    org_id serial PRIMARY KEY,
    name TEXT not null,
    type TEXT,

    UNIQUE(name)
);

CREATE TABLE slot
(
    slot_id serial PRIMARY KEY,
    slot_code VARCHAR(6),
    org_id INT,

    UNIQUE(org_id, slot_code),

    FOREIGN KEY(org_id)
        REFERENCES organisation(org_id)
);

CREATE TABLE slot_schedule
(
    slot_id INT,
    day INT,
    start_time TIME,
    end_time TIME,

    PRIMARY KEY(slot_id, day),

    FOREIGN KEY(slot_id)
        REFERENCES slot
);

CREATE TABLE course
(
    course_id serial PRIMARY KEY,
    kyc TEXT,
    type TEXT,
    -- theory, practice, both
    title TEXT,
    course_code TEXT,
    org_id INT,

    FOREIGN KEY(org_id)
        REFERENCES organisation(org_id),

    UNIQUE(course_code, org_id)
);

CREATE TABLE offering
(
    offering_id serial PRIMARY KEY,
    course_id INT,

    practice_rating REAL DEFAULT 0.0,
    content_rating REAL DEFAULT 0.0,
    theory_rating REAL DEFAULT 0.0,
    litemeter REAL DEFAULT 0.0,
    nratings INT DEFAULT 0,

    cal_link TEXT,
    grading_scheme TEXT,
    instructor TEXT,

    slot_id INT,
    start_date DATE,
    end_date DATE,

    previous_offering_id INT DEFAULT NULL,

    FOREIGN KEY(course_id)
        REFERENCES course(course_id),

    FOREIGN KEY(previous_offering_id)
        REFERENCES offering(offering_id),

    FOREIGN KEY(slot_id)
        REFERENCES slot(slot_id)
);

CREATE TABLE usr
(
    user_id serial PRIMARY KEY,
    email TEXT UNIQUE,
    token JSON
);

CREATE TABLE rating
(
    user_id INT,
    offering_id INT,
    practice_rating REAL DEFAULT 0.0,
    content_rating REAL DEFAULT 0.0,
    theory_rating REAL DEFAULT 0.0,
    litemeter REAL DEFAULT 0.0,

    PRIMARY KEY(user_id, offering_id),

    FOREIGN KEY(user_id)
        REFERENCES usr(user_id),

    FOREIGN KEY(offering_id)
        REFERENCES offering(offering_id)
);

CREATE TABLE manager
(
    user_id INT,
    org_id INT,
    PRIMARY KEY(user_id, org_id),

    FOREIGN KEY(user_id)
        REFERENCES usr(user_id),

    FOREIGN KEY(org_id)
        REFERENCES organisation(org_id)
);

CREATE TABLE resource
(
    resource_id serial PRIMARY KEY,
    offering_id INT,
    user_id INT,
    type TEXT,
    --test, quiz, exam, midsem, tutorial, assignment

    link TEXT,
    --optional

    about TEXT,

    FOREIGN KEY(offering_id)
        REFERENCES offering(offering_id),

    FOREIGN KEY(user_id)
        REFERENCES usr(user_id)
);

CREATE TABLE subscription
(
    user_id INT not null,
    offering_id INT not null,

    FOREIGN KEY(user_id)
        REFERENCES usr(user_id),

    FOREIGN KEY(offering_id)
        REFERENCES offering(offering_id)
);


SELECT version();