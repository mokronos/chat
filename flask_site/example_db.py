from werkzeug.security import generate_password_hash


def add_data(db):
    db.executemany(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            [("admin", generate_password_hash("95@WtTjjMFKyZN6")),
             ("admin2", generate_password_hash("95@WtTjjMFKyZN5"))]
            )
    db.executemany(
            'INSERT INTO argument (title, content, user_id, id) VALUES (?, ?, ?, ?)',
            [("Socrates", "Mortality of Socrates", 1, 1),
             ("Mammals", "Backbones of Mammals", 2, 2),
             ("Black crows", "Inductive crow color", 1, 3)]
            )
    db.executemany(
            'INSERT INTO premise (title, content, user_id, id) VALUES (?, ?, ?, ?)',
            [("Man", "Socrates is a man.", 1, 1),
             ("Mortality", "All men are mortal.", 1, 2),
             ("Backbone", "All mammals have backbones.", 1, 3),
             ("Whales", "Whales are mammals. thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text thisis long extra text", 2, 4),
             ("Crows", "Every crow i've seen is black.", 2, 5)
             ]
            )
    db.executemany(
            'INSERT INTO conclusion (title, content, user_id, id) VALUES (?, ?, ?, ?)',
            [("Socrates", "Socrates is mortal.", 1, 1),
             ("Whales have backbones.", "This is an example conclusion 2", 1, 2),
             ("Crows", "All crows are black.", 2, 3)]
            )
    db.executemany(
            'INSERT INTO argument_premise (argument_id, premise_id) VALUES (?, ?)',
            [(1, 1), (1, 2), (2, 3), (2, 4), (3, 5)]
            )
    db.executemany(
            'INSERT INTO argument_conclusion (argument_id, conclusion_id) VALUES (?, ?)',
            [(1, 1), (2, 2), (3, 3)]
            )
    db.commit()

if __name__ == "__main__":
    from .db import get_db
    add_data(get_db())
