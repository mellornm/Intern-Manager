-- CREATE VENUE TABLE
CREATE TABLE IF NOT EXISTS venues (
    venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name TEXT NOT NULL,
    address TEXT,
    supervisor_name TEXT,
    supervisor_email TEXT,
    supervisor_phone TEXT,
    last_update TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
);

-- CREATE INTERN TABLE
CREATE TABLE IF NOT EXISTS interns (
    intern_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    registration_number TEXT UNIQUE NOT NULL,
    email TEXT,
    start_date TEXT,
    end_date TEXT,
    working_days TEXT,
    working_hours TEXT,
    venue_id INTEGER,
    term TEXT NOT NULL,
    last_update TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
);

-- CREATE DOCUMENTS TABLE
CREATE TABLE IF NOT EXISTS documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    intern_id INTEGER NOT NULL,
    document_name TEXT NOT NULL,
    status TEXT DEFAULT 'Pendente',
    feedback TEXT,
    last_update TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (intern_id) REFERENCES interns(intern_id) ON DELETE CASCADE
);

-- CREATE OBSERVATIONS TABLE
CREATE TABLE IF NOT EXISTS observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    intern_id INTEGER NOT NULL,
    observation TEXT NOT NULL,
    last_update TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (intern_id) REFERENCES interns(intern_id) ON DELETE CASCADE
);

-- CREATE MEETINGS TABLE
CREATE TABLE IF NOT EXISTS meetings (
    meeting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    intern_id INTEGER NOT NULL,
    meeting_date TEXT NOT NULL,
    is_intern_present INTEGER NOT NULL CHECK (is_intern_present IN (0, 1)),
    FOREIGN KEY (intern_id) REFERENCES interns(intern_id) ON DELETE CASCADE
);

-- CREATE EVALUATION CRITERIA TABLE
CREATE TABLE IF NOT EXISTS evaluation_criteria (
    criteria_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    weight REAL DEFAULT 1.0,
    last_update TEXT DEFAULT (datetime('now', 'localtime'))
);

-- CREATE GRADES TABLE
CREATE TABLE IF NOT EXISTS grades (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    intern_id INTEGER NOT NULL,
    criteria_id INTEGER NOT NULL,
    value REAL NOT NULL CHECK (value >= 0),
    last_update TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (intern_id) REFERENCES interns(intern_id) ON DELETE CASCADE,
    FOREIGN KEY (criteria_id) REFERENCES evaluation_criteria(criteria_id) ON DELETE RESTRICT,
    UNIQUE(intern_id, criteria_id) 
);