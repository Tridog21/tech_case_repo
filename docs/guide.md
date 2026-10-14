# Guide technique

## Choix et limites

- DuckDB : moteur analytique embarqué ; aucun port ni service à configurer.
- dbt Core + dbt-duckdb : couches staging et mart, références explicites et tests.
- Python/uv : environnement isolé et versions verrouillées, Python épinglé dans `.python-version`.
- DECIMAL(12,2) : calcul exact des montants ; aucune devise réelle n'est définie dans la démo.
- Import complet : adapté à un petit case ; la démo charge le CSV en mémoire.
- La granularité du mart est une date comportant au moins une commande terminée.
  Les journées sans commande terminée sont absentes ; aucun calendrier n'est ajouté.
- Pas de dimension client disponible : on ne peut pas tester l'intégrité référentielle client
  avant de disposer de cette source. Ajouter ce contrôle lors de l'adaptation au vrai case.
- Pas d'incrémental, orchestration ni infrastructure cloud avant réception des exigences.

## Adapter au sujet

1. Lire les critères de notation, outils imposés et règles d'utilisation des données/assistants.
2. Définir les grains, clés, métriques, dates, fuseaux et règles métier.
3. Adapter le contrat d'entrée, les sources, modèles, tests et données de référence.
4. Remplacer les résultats de démonstration dans le README et compléter le rapport.
5. Refaire le parcours du recruteur dans un environnement neuf.
6. Si un autre moteur est imposé, adapter le profil, le dialecte SQL et tester sur ce moteur.

## Dépannage

- `uv` introuvable : rouvrir le terminal après installation, puis `uv --version`.
- Dépendances incohérentes : `uv sync --locked`. Ne pas modifier le verrou à la livraison.
- Verrouillage DuckDB : fermer l'outil qui utilise le fichier avant de relancer.
- CSV refusé : contrôler la ligne et le format indiqué par le message.
- Erreur de connexion : lancer `doctor`. Le script fournit le chemin absolu de la base à dbt.
- Serveur de documentation : `docs` reste actif jusqu'à Ctrl+C ; aucun hébergement public.
- Git : rouvrir le terminal après l'installation ; VS Code utilise le dépôt local.

## Git et GitHub

Le dépôt local suffit pour commencer. Avant le premier commit, vérifier l'identité :

```text
git config user.name "Votre nom"
git config user.email "Votre adresse Git ou adresse noreply GitHub"
git add .
git commit -m "Prepare reproducible analytics case starter"
```

Préférer une identité configurée dans le dépôt plutôt qu'un changement global.
Relire `git diff --cached` avant le commit. Vérifier les règles de partage de l'entreprise.
Le dépôt distant reste optionnel. Lorsqu'il est retenu et le compte connu :

```text
gh auth login --web --git-protocol https
gh repo create NOM-DU-DEPOT --private --source . --remote origin --push
```

La connexion est effectuée par le propriétaire du compte dans le navigateur.
Le workflow est prêt, mais ses trois plateformes ne sont vérifiées qu'après un run réussi
sur GitHub. Ne pas déclarer un support multiplateforme vérifié sur cette seule base.

## Checklist de remise

- README de démarrage rapide suivi avec succès depuis un clone neuf.
- Données partageables ou démonstration fictive avec valeurs attendues.
- Versions verrouillées et tests passant ; workflow vert si GitHub utilisé.
- Rapport terminé, hypothèses et limites explicites, dictionnaire et lineage accessibles.
- Aucun secret, aucune donnée confidentielle ni chemin propre au poste dans Git.
- Accès du recruteur vérifié si dépôt privé ; lien et commande de lancement dans le message de remise.
