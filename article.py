"""
article.py – Article ORM model
"""
from datetime import datetime, timezone
from database import db


class Article(db.Model):
    __tablename__ = "articles"

    id         = db.Column(db.Integer,     primary_key=True, autoincrement=True)
    titre      = db.Column(db.String(255), nullable=False)
    contenu    = db.Column(db.Text,        nullable=False)
    auteur     = db.Column(db.String(100), nullable=False)
    date       = db.Column(db.DateTime,    default=lambda: datetime.now(timezone.utc))
    categorie  = db.Column(db.String(100), nullable=False)
    tags       = db.Column(db.String(500), nullable=True)   # comma-separated

    def to_dict(self) -> dict:
        return {
            "id":        self.id,
            "titre":     self.titre,
            "contenu":   self.contenu,
            "auteur":    self.auteur,
            "date":      self.date.isoformat() if self.date else None,
            "categorie": self.categorie,
            "tags":      [t.strip() for t in self.tags.split(",")] if self.tags else [],
        }

    def __repr__(self) -> str:
        return f"<Article id={self.id} titre='{self.titre}'>"
