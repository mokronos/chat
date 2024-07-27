DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS argument;
DROP TABLE IF EXISTS premise;
DROP TABLE IF EXISTS conclusion;
DROP TABLE IF EXISTS argument_premise;
DROP TABLE IF EXISTS argument_conclusion;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE argument (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE premise (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE argument_premise (
  argument_id INTEGER NOT NULL,
  premise_id INTEGER NOT NULL,
  FOREIGN KEY (argument_id) REFERENCES argument (id)
  FOREIGN KEY (premise_id) REFERENCES premise (id)
  UNIQUE (argument_id, premise_id)
);

CREATE TABLE conclusion (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE argument_conclusion (
  argument_id INTEGER NOT NULL,
  conclusion_id INTEGER NOT NULL,
  FOREIGN KEY (argument_id) REFERENCES argument (id)
  FOREIGN KEY (conclusion_id) REFERENCES conclusion (id)
  UNIQUE (argument_id, conclusion_id)
);
