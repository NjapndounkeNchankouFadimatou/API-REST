# 📰 Blog Articles API

API REST complète pour la gestion d'articles de blog, construite avec **Flask + Flask-RESTX + SQLite**.

---

## 🚀 Installation

### 1. Cloner / récupérer les fichiers

```
app.py
requirements.txt
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer l'API

```bash
python app.py
```

L'API démarre sur **http://localhost:5000**  
La base de données `blog.db` est créée automatiquement au premier démarrage.

---

## 📖 Documentation Swagger UI

Accessible sur : **http://localhost:5000/docs**

---

## 🗂️ Modèle de données — Article

| Champ             | Type    | Obligatoire | Description                              |
|-------------------|---------|-------------|------------------------------------------|
| id                | integer | auto        | Identifiant unique (auto-incrémenté)     |
| titre             | string  | ✅ oui      | Titre de l'article (max 200 caractères)  |
| contenu           | text    | ✅ oui      | Corps complet de l'article               |
| auteur            | string  | ✅ oui      | Nom de l'auteur (max 100 caractères)     |
| categorie         | string  | non         | Catégorie (ex : Technologie, Lifestyle)  |
| tags              | string  | non         | Tags séparés par des virgules            |
| publie            | boolean | non         | Statut de publication (défaut : false)   |
| date_creation     | datetime| auto        | Date de création (UTC, ISO 8601)         |
| date_modification | datetime| auto        | Date de dernière modification (UTC)      |

---

## 🔌 Endpoints

| Méthode | Route                      | Description                          |
|---------|----------------------------|--------------------------------------|
| POST    | /api/articles/             | Créer un article                     |
| GET     | /api/articles/             | Lister tous les articles (+ filtres) |
| GET     | /api/articles/search       | Rechercher par mot-clé               |
| GET     | /api/articles/{id}         | Récupérer un article par ID          |
| PUT     | /api/articles/{id}         | Modifier un article (partiel OK)     |
| DELETE  | /api/articles/{id}         | Supprimer un article                 |

### Filtres disponibles sur `GET /api/articles/`

| Paramètre  | Exemple                              | Description              |
|------------|--------------------------------------|--------------------------|
| auteur     | `?auteur=Alice`                      | Filtrer par auteur       |
| categorie  | `?categorie=Technologie`             | Filtrer par catégorie    |
| publie     | `?publie=true` ou `?publie=false`    | Filtrer par publication  |

---

## 🧪 Exemples cURL

### ➕ Créer un article

```bash
curl -X POST http://localhost:5000/api/articles/ \
  -H "Content-Type: application/json" \
  -d '{
    "titre": "Introduction à Flask",
    "contenu": "Flask est un micro-framework Python très populaire...",
    "auteur": "Alice Dupont",
    "categorie": "Technologie",
    "tags": "python,flask,web",
    "publie": true
  }'
```

### 📋 Lister tous les articles

```bash
curl http://localhost:5000/api/articles/
```

### 🔍 Filtrer les articles publiés par catégorie

```bash
curl "http://localhost:5000/api/articles/?publie=true&categorie=Technologie"
```

### 🔎 Rechercher par mot-clé

```bash
curl "http://localhost:5000/api/articles/search?query=flask"
```

### 📄 Récupérer un article par ID

```bash
curl http://localhost:5000/api/articles/1
```

### ✏️ Modifier un article (mise à jour partielle)

```bash
curl -X PUT http://localhost:5000/api/articles/1 \
  -H "Content-Type: application/json" \
  -d '{
    "titre": "Introduction à Flask — Édition mise à jour",
    "publie": true
  }'
```

### 🗑️ Supprimer un article

```bash
curl -X DELETE http://localhost:5000/api/articles/1
```

---

## 📡 Codes de réponse HTTP

| Code | Signification              |
|------|----------------------------|
| 200  | Succès                     |
| 201  | Ressource créée            |
| 400  | Données invalides          |
| 404  | Ressource introuvable      |
| 500  | Erreur interne du serveur  |

---

## 🏗️ Structure du projet

```
.
├── app.py           # Code source complet de l'API
├── requirements.txt # Dépendances Python
├── README.md        # Cette documentation
└── blog.db          # Base SQLite (créée automatiquement)
