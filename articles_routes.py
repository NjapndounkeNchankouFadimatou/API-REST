"""
articles_routes.py – All /api/articles endpoints (Blueprint)
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from database import db
from article import Article

articles_bp = Blueprint("articles", __name__, url_prefix="/api/articles")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def ok(data=None, message="Succès", status=200, **extra):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    body.update(extra)
    return jsonify(body), status


def err(message="Erreur", status=400, errors=None):
    body = {"success": False, "message": message}
    if errors:
        body["errors"] = errors
    return jsonify(body), status


def validate_article(data: dict, partial=False) -> list[str]:
    problems = []
    required = ["titre", "contenu", "auteur", "categorie"]
    for field in required:
        if not partial and field not in data:
            problems.append(f"'{field}' est obligatoire.")
        elif field in data and not str(data[field]).strip():
            problems.append(f"'{field}' ne peut pas être vide.")
    return problems


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/articles/search  (declared BEFORE <int:id> route)
# ─────────────────────────────────────────────────────────────────────────────

@articles_bp.route("/search", methods=["GET"])
def search_articles():
    """
    Rechercher des articles par titre ou contenu.
    ---
    tags:
      - Articles
    parameters:
      - name: query
        in: query
        type: string
        required: true
        description: Texte à rechercher dans le titre ou le contenu
    responses:
      200:
        description: Liste des articles correspondants
      400:
        description: Paramètre 'query' manquant
    """
    query_text = request.args.get("query", "").strip()
    if not query_text:
        return err("Le paramètre 'query' est requis.", 400)

    like = f"%{query_text}%"
    results = Article.query.filter(
        db.or_(Article.titre.ilike(like), Article.contenu.ilike(like))
    ).all()
    return ok([a.to_dict() for a in results], f"{len(results)} article(s) trouvé(s).")


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/articles
# ─────────────────────────────────────────────────────────────────────────────

@articles_bp.route("", methods=["GET"])
def get_articles():
    """
    Récupérer tous les articles (filtrables).
    ---
    tags:
      - Articles
    parameters:
      - name: categorie
        in: query
        type: string
      - name: auteur
        in: query
        type: string
      - name: date
        in: query
        type: string
        description: Format YYYY-MM-DD
    responses:
      200:
        description: Liste des articles
    """
    query = Article.query

    categorie = request.args.get("categorie")
    auteur    = request.args.get("auteur")
    date_str  = request.args.get("date")

    if categorie:
        query = query.filter(Article.categorie.ilike(f"%{categorie}%"))
    if auteur:
        query = query.filter(Article.auteur.ilike(f"%{auteur}%"))
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter(db.func.date(Article.date) == date_obj)
        except ValueError:
            return err("Format de date invalide. Utilisez YYYY-MM-DD.", 400)

    articles = query.order_by(Article.date.desc()).all()
    return ok([a.to_dict() for a in articles],
              f"{len(articles)} article(s) récupéré(s).",
              count=len(articles))


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/articles
# ─────────────────────────────────────────────────────────────────────────────

@articles_bp.route("", methods=["POST"])
def create_article():
    """
    Créer un nouvel article.
    ---
    tags:
      - Articles
    parameters:
      - in: body
        name: body
        required: true
        schema:
          required: [titre, contenu, auteur, categorie]
          properties:
            titre:
              type: string
              example: "Introduction au Web"
            contenu:
              type: string
              example: "Le web est composé de HTML, CSS et JavaScript..."
            auteur:
              type: string
              example: "Charles"
            categorie:
              type: string
              example: "Technologie"
            tags:
              type: string
              example: "web, html, css"
    responses:
      201:
        description: Article créé
      422:
        description: Erreur de validation
    """
    body = request.get_json(silent=True)
    if body is None:
        return err("Le corps de la requête doit être du JSON valide.", 400)

    errors = validate_article(body)
    if errors:
        return err("Validation échouée.", 422, errors=errors)

    article = Article(
        titre     = body["titre"].strip(),
        contenu   = body["contenu"].strip(),
        auteur    = body["auteur"].strip(),
        categorie = body["categorie"].strip(),
        tags      = body.get("tags", ""),
    )
    db.session.add(article)
    db.session.commit()
    return ok(article.to_dict(), "Article créé avec succès.", 201)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/articles/<id>
# ─────────────────────────────────────────────────────────────────────────────

@articles_bp.route("/<int:article_id>", methods=["GET"])
def get_article(article_id: int):
    """
    Récupérer un article par son ID.
    ---
    tags:
      - Articles
    parameters:
      - name: article_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Article trouvé
      404:
        description: Article introuvable
    """
    article = db.session.get(Article, article_id)
    if article is None:
        return err(f"Article {article_id} introuvable.", 404)
    return ok(article.to_dict(), "Article récupéré.")


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/articles/<id>
# ─────────────────────────────────────────────────────────────────────────────

@articles_bp.route("/<int:article_id>", methods=["PUT"])
def update_article(article_id: int):
    """
    Mettre à jour un article (remplacement complet).
    ---
    tags:
      - Articles
    parameters:
      - name: article_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          required: [titre, contenu, auteur, categorie]
          properties:
            titre:
              type: string
            contenu:
              type: string
            auteur:
              type: string
            categorie:
              type: string
            tags:
              type: string
    responses:
      200:
        description: Article mis à jour
      404:
        description: Article introuvable
    """
    article = db.session.get(Article, article_id)
    if article is None:
        return err(f"Article {article_id} introuvable.", 404)

    body = request.get_json(silent=True)
    if body is None:
        return err("Le corps de la requête doit être du JSON valide.", 400)

    errors = validate_article(body, partial=False)
    if errors:
        return err("Validation échouée.", 422, errors=errors)

    article.titre     = body["titre"].strip()
    article.contenu   = body["contenu"].strip()
    article.auteur    = body["auteur"].strip()
    article.categorie = body["categorie"].strip()
    article.tags      = body.get("tags", article.tags)

    db.session.commit()
    return ok(article.to_dict(), "Article mis à jour.")


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /api/articles/<id>
# ─────────────────────────────────────────────────────────────────────────────

@articles_bp.route("/<int:article_id>", methods=["DELETE"])
def delete_article(article_id: int):
    """
    Supprimer un article.
    ---
    tags:
      - Articles
    parameters:
      - name: article_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Article supprimé
      404:
        description: Article introuvable
    """
    article = db.session.get(Article, article_id)
    if article is None:
        return err(f"Article {article_id} introuvable.", 404)

    deleted = article.to_dict()
    db.session.delete(article)
    db.session.commit()
    return ok(deleted, "Article supprimé.")
