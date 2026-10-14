# Analytics engineering case — environnement reproductible

Socle de démonstration prêt à adapter aux consignes du case. Les données et conclusions
ci-dessous sont fictives ; elles servent à vérifier l'installation, pas à répondre au futur sujet.

## Démarrage rapide pour le recruteur

Prérequis : Git et **uv 0.13.1**, accès Internet pour la première installation.
Python 3.12.12 est téléchargé automatiquement par uv. Aucune base serveur, aucun compte cloud,
aucun secret et aucun éditeur spécifique ne sont nécessaires pour exécuter la démonstration.

1. Installer uv : [instructions officielles](https://docs.astral.sh/uv/getting-started/installation/).
   Sous Windows : `winget install --id astral-sh.uv --exact`.
   Ouvrir un nouveau terminal après l'installation.
2. Cloner le dépôt puis entrer dans son dossier :

   ```text
   git clone https://github.com/Tridog21/tech_case_repo.git
   cd tech_case_repo
   ```

   Si vous avez reçu une archive, l'extraire puis ouvrir un terminal dans `analytics-case`.
3. Exécuter :

```text
uv sync --locked
uv run --locked python scripts/case.py demo
```

La première commande installe les versions exactes de `uv.lock` dans `.venv`.
La deuxième importe les données, construit les modèles, teste les données et le code,
compare les résultats à la référence et génère la documentation dbt.
Tout échec retourne un code de sortie non nul ; la dernière ligne doit afficher `SUCCESS`.

Résultats attendus :

| Date | Commandes terminées | Revenu |
|---|---:|---:|
| 2026-01-01 | 2 | 150.00 |
| 2026-01-02 | 2 | 100.00 |
| **Total** | **4** | **250.00** |

La commande annulée de 25.00 est exclue du revenu.

Consulter `reports/generated/daily_revenue.csv` et `reports/generated/manifest.json`.
Le manifeste fournit les empreintes du fichier source et du verrou des dépendances.
La référence indépendante est `data/sample/expected_daily_revenue.csv`.

## Commandes utiles

Toutes les commandes ci-dessous se lancent depuis le dossier du projet :

```text
# Diagnostic de Python, de l'adaptateur et de la connexion dbt
uv run --locked python scripts/case.py doctor

# Recalcul des résultats sans lancer les tests Python
uv run --locked python scripts/case.py run

# Qualité du code et tests de l'import (les tests dbt sont exécutés par run/demo)
uv run --locked python scripts/case.py check

# Documentation interactive : ouvrir http://127.0.0.1:8080, arrêter avec Ctrl+C
uv run --locked python scripts/case.py docs

# Exécuter avec un autre jeu de données
uv run --locked python scripts/case.py run --input data/raw/orders.csv
```

`demo` est réservé aux données de référence ; `run` accepte vos propres données.
Les tables sont reconstruites à chaque exécution : relancer n'ajoute aucun doublon.
Une entrée invalide est rejetée avant modification des données brutes existantes.
Un échec dbt arrête la commande avant l'export ; les anciens exports peuvent rester présents,
donc ne considérez un résultat valide que si la commande courante se termine avec succès.

## Tester avec vos données

Copier un CSV UTF-8 dans `data/raw/`. En-tête exact :

```csv
order_id,customer_id,order_date,amount,status
10,201,2026-02-01,42.50,completed
11,202,2026-02-01,10.00,cancelled
```

Contraintes : identifiants entiers positifs, `order_id` unique, date `YYYY-MM-DD`,
montant positif ou nul avec au plus deux décimales et inférieur à 10 milliards,
statut `completed` ou `cancelled`, au moins une ligne. Le séparateur est la virgule et
le séparateur décimal le point. L'exemple ci-dessus doit produire un revenu de **42.50**.

Pour vérifier un rejet, remplacer un montant par `-1` ou dupliquer un `order_id`.
Le message doit indiquer la ligne fautive et la commande doit échouer.
Les données réelles, bases locales, secrets et exports générés sont exclus de Git.

## Architecture et livrables

`CSV → validation Python → raw.orders → stg_orders → daily_revenue → CSV + manifeste`

- `scripts/` : import, validation, exécution et exports.
- `dbt/` : transformations SQL, tests et documentation des colonnes.
- `tests/` : tests d'import, rejet des données invalides, protection des données existantes.
- `docs/` : architecture, décisions, dépannage et préparation de la livraison.
- `reports/report.md` : trame du rapport métier à compléter lorsque les consignes arrivent.
- `.github/workflows/verify.yml` : reproduction sur Windows, Linux et macOS une fois publié.

La base est dans `warehouse/case.duckdb`. Fermer les autres connexions avant un recalcul.
Pour repartir de zéro, travailler dans un nouveau clone ou une nouvelle extraction.
La reproductibilité porte sur les valeurs et la référence CSV ; les logs et métadonnées dbt
peuvent contenir des dates d'exécution et ne sont pas identiques octet par octet.

Voir [le guide technique](docs/guide.md), [le suivi de validation](docs/validation.md)
et [la trame du rapport](reports/report.md).
