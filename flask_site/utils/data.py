from flask import g
from ..db import get_db

def get_all(request):

    db = get_db()
    q = request.args.get('q')
    own = request.args.get('own')
    if g.user:
        user = g.user['id']
    else:
        user = 0

    query = f"%{q if q else ''}%"

    items = db.execute("""
            SELECT U.*, user.username FROM (
            SELECT * FROM (
            SELECT 'argument' AS category, title, content, id, created, user_id FROM argument UNION
            SELECT 'premise' AS category, title, content, id, created, user_id FROM premise UNION
            SELECT 'conclusion' AS category, title, content, id, created, user_id FROM conclusion)
            AS U
            WHERE (title LIKE ? OR content LIKE ? OR category LIKE ?) AND (? = 0 OR user_id = ?)
            ORDER BY title DESC) AS U
            JOIN user ON user.id = U.user_id
            """, (query, query, query, 1 if own == 'on' and user else 0, user)).fetchall()

    return items

def fetch_items_for_user(category):

    if category not in ['argument', 'premise', 'conclusion']:
        return []

    db = get_db()

    items = db.execute(f"SELECT * FROM {category} WHERE user_id = ?", (g.user['id'],)).fetchall()

    return items
