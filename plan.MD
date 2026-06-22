# TechMentor AI - Plan Complet de Développement (MVP)

## 1. Présentation du projet

### Nom

**TechMentor AI**

### Vision

TechMentor AI est une plateforme intelligente de mentorat académique et professionnel destinée aux étudiants en informatique.

Son objectif est d'aider les étudiants à :

* analyser leur profil actuel
* identifier leurs compétences
* détecter leurs lacunes
* définir un objectif de carrière
* obtenir une roadmap personnalisée
* progresser continuellement grâce à un mentor IA

---

## 2. Objectifs du MVP

À partir d'un CV et d'informations utilisateur, le système doit :

1. Extraire les informations du profil
2. Détecter les compétences techniques
3. Comparer ces compétences à un métier cible
4. Identifier les écarts de compétences
5. Générer une roadmap personnalisée
6. Recommander des projets
7. Fournir un chatbot mentor IA
8. Conserver l'historique des analyses
9. Réévaluer l'utilisateur après chaque roadmap

---

# 3. Architecture Générale

```text
┌─────────────────────────┐
│       Frontend          │
│        Next.js          │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│        FastAPI          │
│       Backend API       │
└────────────┬────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼

PostgreSQL      Qdrant
(Base métier)  (Vector DB)

      ▼             ▼

      LLM + RAG
```

---

# 4. Stack Technique

## Frontend

* Next.js
* TypeScript
* Tailwind CSS
* Shadcn UI
* Axios

---

## Backend

* FastAPI
* SQLAlchemy
* Alembic
* Pydantic

---

## Base de données

* PostgreSQL

---

## Vector Database

* Qdrant

---

## IA

* Modèle LLM (Roadium AI)

---

## RAG

* LangChain

---

## Parsing CV

* PyMuPDF
* PDFPlumber
* python-docx

---

## Déploiement

* Docker
* Docker Compose

---

# 5. Modules du Projet

---

# Module 1 : Authentification

## Fonctionnalités

* Inscription
* Connexion
* Déconnexion
* Réinitialisation mot de passe

### Tables

```text
users
```

### Champs

```text
id
firstname
lastname
email
password_hash
created_at
updated_at
```

---

# Module 2 : Profil Étudiant

## Fonctionnalités

L'étudiant renseigne :

* université
* filière
* niveau
* objectif professionnel

### Table

```text
student_profiles
```

### Champs

```text
id
user_id
university
department
academic_level
career_goal
github_url
```

---

# Module 3 : Upload CV

## Fonctionnalités

* Upload PDF
* Upload DOCX

### Pipeline

```text
Upload
↓
Extraction texte
↓
Nettoyage
↓
Analyse IA
```

### Table

```text
cv_files
```

---

# Module 4 : Extraction de Compétences

## Données extraites

### Informations personnelles

* nom
* email

### Formation

* diplômes
* établissements

### Expériences

* stages
* emplois

### Projets

* projets académiques
* projets personnels

### Compétences

* langages
* frameworks
* bases de données
* outils

### Certifications

* certifications obtenues

---

# Module 5 : Analyse GitHub

## Fonctionnalités

Analyse automatique :

* repositories
* langages
* activité
* projets

### Données récupérées

```text
Nombre de projets
Langages utilisés
Technologies détectées
```

### Table

```text
github_analysis
```

---

# Module 6 : Catalogue des Métiers

## Première version

### Backend Developer

Compétences :

* Java
* Spring Boot
* SQL
* Git
* Docker

---

### Data Scientist

Compétences :

* Python
* Pandas
* Numpy
* Machine Learning

---

### Data Engineer

Compétences :

* Python
* SQL
* Spark
* Airflow
* Docker

---

# Module 7 : Référentiel de Compétences

## Tables

```text
skills
career_paths
career_path_skills
```

### Exemple

```text
Python
SQL
Git
Docker
Spark
Airflow
```

---

# Module 8 : Skill Gap Analysis

## Entrée

Compétences utilisateur

VS

Compétences métier

---

## Sortie

```json
{
  "owned": [
    "Python",
    "SQL"
  ],
  "missing": [
    "Spark",
    "Docker"
  ]
}
```

---

# Module 9 : Système de Score

## Calcul

Score sur 100.

Exemple :

```text
Python = 20
SQL = 20
Git = 10

Score = 50/100
```

### Résultat

```text
Débutant
Intermédiaire
Avancé
```

---

# Module 10 : Base de Connaissances (RAG)

## Contenus

### Roadmaps

* Backend
* Data Engineer
* Data Scientist

### Certifications

* AWS
* Azure
* Google Cloud

### Ressources

* tutoriels
* guides
* documentations

---

# Module 11 : Générateur de Roadmap

## Entrées

* profil
* score
* compétences
* métier cible

---

## Sorties

### Mois 1

* SQL avancé

### Mois 2

* Docker

### Mois 3

* Spark

---

# Module 12 : Recommandation de Projets

## Débutant

* Gestion de bibliothèque
* Todo App

---

## Intermédiaire

* API REST complète
* Dashboard analytique

---

## Avancé

* Pipeline ETL
* Système temps réel

---

# Module 13 : Mentor IA

## Fonctionnalités

L'utilisateur peut discuter avec :

```text
Comment apprendre Docker ?
```

```text
Quel projet dois-je réaliser ?
```

```text
Comment obtenir un stage ?
```

---

## Contexte utilisé

* profil étudiant
* CV
* GitHub
* roadmap
* score
* historique

---

# Module 14 : Historique

## Conservation

* analyses
* scores
* roadmaps
* conversations

### Tables

```text
analysis_history
roadmaps
chat_sessions
messages
```

---

# Module 15 : Évaluation Continue

## Après une roadmap

### Quiz

Questions techniques

---

### Projet

Projet pratique

---

### Nouvelle évaluation

```text
Ancien score
↓
Nouveau score
↓
Nouveau niveau
↓
Nouvelle roadmap
```

---

# 6. Structure Backend

```text
backend/

app/

├── api/
├── core/
├── database/
├── models/
├── schemas/
├── services/
├── rag/
├── ai/
├── repositories/
├── utils/
└── main.py
```

---

# 7. Structure Frontend

```text
frontend/

src/

├── app/
├── components/
├── features/
├── services/
├── hooks/
├── store/
└── types/
```

---

# 8. Roadmap de Développement

## Phase 1

Infrastructure

* PostgreSQL
* FastAPI
* Next.js
* Docker

---

## Phase 2

Authentification

* utilisateurs
* profils

---

## Phase 3

Upload CV

* parsing
* extraction

---

## Phase 4

Référentiel métiers

* skills
* métiers

---

## Phase 5

Analyse des écarts

* score
* lacunes

---

## Phase 6

RAG

* Qdrant
* embeddings

---

## Phase 7

Roadmap IA

* génération
* recommandations

---

## Phase 8

Mentor IA

* chatbot
* mémoire utilisateur

---

## Phase 9

Historique

* analyses
* conversations

---

## Phase 10

Évaluation continue

* quiz
* progression

---

# 9. MVP Final

L'étudiant :

1. crée un compte
2. complète son profil
3. téléverse son CV
4. connecte son GitHub
5. choisit un métier
6. obtient son analyse
7. reçoit une roadmap
8. échange avec le mentor IA
9. réalise les projets recommandés
10. passe une évaluation
11. obtient un nouveau score
12. reçoit une nouvelle roadmap

Le système devient alors un véritable mentor numérique personnalisé capable d'accompagner l'étudiant tout au long de son parcours universitaire et professionnel.
