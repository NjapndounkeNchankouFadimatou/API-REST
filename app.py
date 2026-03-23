import sqlite3
import os
from datetime import date as today_date
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'blog.db')

# ══════════════════════════════════════════════════════════════
# BASE DE DONNÉES
# ══════════════════════════════════════════════════════════════

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            titre     TEXT NOT NULL,
            contenu   TEXT NOT NULL,
            auteur    TEXT NOT NULL,
            date      TEXT NOT NULL,
            categorie TEXT NOT NULL,
            tags      TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()

def row_to_dict(row):
    if row is None:
        return None
    d = dict(row)
    d['tags'] = [t.strip() for t in d['tags'].split(',') if t.strip()]
    return d

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def ok(data, code=200):
    return jsonify(data), code

def err(msg, code=400):
    return jsonify({"erreur": msg}), code

# ══════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return ok({
        "message": "API Blog INF222",
        "version": "1.0.0",
        "docs": "/docs"
    })

# POST /api/articles – Créer un article
@app.route('/api/articles', methods=['POST'])
def creer_article():
    data = request.get_json()
    if not data:
        return err("Corps JSON manquant.", 400)

    manquants = [c for c in ['titre', 'contenu', 'auteur', 'categorie'] if not str(data.get(c, '')).strip()]
    if manquants:
        return err(f"Champs obligatoires manquants : {', '.join(manquants)}.", 400)

    tags = data.get('tags', [])
    if not isinstance(tags, list):
        return err("Le champ 'tags' doit être une liste.", 400)

    conn = get_db()
    cur = conn.execute(
        'INSERT INTO articles (titre, contenu, auteur, date, categorie, tags) VALUES (?,?,?,?,?,?)',
        (data['titre'].strip(), data['contenu'].strip(), data['auteur'].strip(),
         data.get('date', str(today_date.today())), data['categorie'].strip(), ', '.join(tags))
    )
    conn.commit()
    new_id = cur.lastrowid
    article = row_to_dict(conn.execute('SELECT * FROM articles WHERE id=?', (new_id,)).fetchone())
    conn.close()
    return ok({"message": "Article créé avec succès.", "article": article}, 201)

# GET /api/articles/search – Rechercher (AVANT /<id>)
@app.route('/api/articles/search', methods=['GET'])
def rechercher():
    query = request.args.get('query', '').strip()
    if not query:
        return err("Paramètre 'query' requis.", 400)
    conn = get_db()
    like = f'%{query}%'
    rows = conn.execute('SELECT * FROM articles WHERE titre LIKE ? OR contenu LIKE ?', (like, like)).fetchall()
    conn.close()
    articles = [row_to_dict(r) for r in rows]
    return ok({"articles": articles, "total": len(articles)})

# GET /api/articles – Lister / filtrer
@app.route('/api/articles', methods=['GET'])
def lister_articles():
    query = 'SELECT * FROM articles WHERE 1=1'
    params = []
    for col in ['categorie', 'auteur', 'date']:
        val = request.args.get(col)
        if val:
            query += f' AND {col} = ?'
            params.append(val)
    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    articles = [row_to_dict(r) for r in rows]
    return ok({"articles": articles, "total": len(articles)})

# GET /api/articles/<id> – Lire un article
@app.route('/api/articles/<int:article_id>', methods=['GET'])
def lire_article(article_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM articles WHERE id=?', (article_id,)).fetchone()
    conn.close()
    article = row_to_dict(row)
    if article is None:
        return err(f"Article {article_id} introuvable.", 404)
    return ok({"article": article})

# PUT /api/articles/<id> – Modifier un article
@app.route('/api/articles/<int:article_id>', methods=['PUT'])
def modifier_article(article_id):
    conn = get_db()
    if conn.execute('SELECT id FROM articles WHERE id=?', (article_id,)).fetchone() is None:
        conn.close()
        return err(f"Article {article_id} introuvable.", 404)

    data = request.get_json()
    if not data:
        conn.close()
        return err("Corps JSON manquant.", 400)

    allowed = {'titre', 'contenu', 'categorie', 'tags'}
    sets, params = [], []
    for key, val in data.items():
        if key in allowed:
            if key == 'tags' and isinstance(val, list):
                val = ', '.join(val)
            sets.append(f'{key} = ?')
            params.append(val)

    if not sets:
        conn.close()
        return err("Aucun champ modifiable fourni (titre, contenu, categorie, tags).", 400)

    params.append(article_id)
    conn.execute(f'UPDATE articles SET {", ".join(sets)} WHERE id=?', params)
    conn.commit()
    article = row_to_dict(conn.execute('SELECT * FROM articles WHERE id=?', (article_id,)).fetchone())
    conn.close()
    return ok({"message": "Article mis à jour avec succès.", "article": article})

# DELETE /api/articles/<id> – Supprimer un article
@app.route('/api/articles/<int:article_id>', methods=['DELETE'])
def supprimer_article(article_id):
    conn = get_db()
    if conn.execute('SELECT id FROM articles WHERE id=?', (article_id,)).fetchone() is None:
        conn.close()
        return err(f"Article {article_id} introuvable.", 404)
    conn.execute('DELETE FROM articles WHERE id=?', (article_id,))
    conn.commit()
    conn.close()
    return ok({"message": f"Article {article_id} supprimé avec succès."})

# ══════════════════════════════════════════════════════════════
# LANCEMENT
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    init_db()
    print("✅ Base de données initialisée.")
    print("🚀 Serveur démarré sur http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
