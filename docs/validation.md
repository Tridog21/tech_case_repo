# Validation du setup

Validation locale effectuée le 14 octobre 2026 sous Windows 11 x64.

## Versions installées

| Outil | Version |
|---|---|
| VS Code | 1.141.1 |
| Git for Windows | 2.55.0.windows.5 |
| uv | 0.13.1 |
| Python | 3.12.12 |
| dbt Core | 1.12.6 |
| dbt-duckdb | 1.11.0 |
| DuckDB | 1.5.6 |

Les versions exactes des dépendances Python figurent dans `uv.lock`.
Extensions VS Code installées : Python, Pylance, Ruff et YAML.
Le Python du projet est géré par uv : utiliser `uv run` plutôt que l'alias Windows `python`.

## Vérifications réussies

- `doctor` : configuration valide et connexion DuckDB réussie.
- `demo` : 2 modèles construits, 15 tests dbt réussis, 11 tests Python réussis.
- Ruff : analyse et formatage réussis ; SQLFluff : analyse SQL réussie.
- CSV produit identique à la référence : 4 commandes terminées, revenu total de 250.00.
- Documentation dbt et catalogue générés.
- Réexécutions : résultats identiques ; le test d'import répété vérifie l'absence de doublons.
- Entrées invalides : montants, identifiants, dates, statuts, doublons et fichier sans données
  sont couverts ; un import invalide conserve les données brutes déjà présentes.
- Archive source extraite dans un dossier neuf, sans `.venv`, base ni sorties générées :
  `uv sync --locked` puis `demo` réussis avec les mêmes résultats et empreintes.
- Second CSV, exécuté par `run --input` : 1 commande terminée, revenu de 42.50,
  15 tests dbt réussis.

La reproduction dans un dossier neuf utilise le même poste Windows et le cache de
téléchargement uv, mais un nouvel environnement Python et une nouvelle base DuckDB.
Elle ne constitue pas un test sur un autre système d'exploitation.

## Éléments en attente

- Identité locale Git : `Tridog21`, adresse GitHub noreply liée à l'identifiant public du compte.
- Dépôt distant configuré : https://github.com/Tridog21/tech_case_repo.git, branche `main`.
- Résultats du workflow Windows/Linux/macOS à consulter dans l'onglet Actions du dépôt.
- Rapport métier et adaptation des modèles à réaliser lorsque les consignes seront connues.

Docker, PostgreSQL et les outils BI restent conditionnels aux exigences du case.
