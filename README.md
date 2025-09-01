# Echome Energies — Pipeline Newsletter PV (gratuit)

Ce dépôt contient un pipeline **100% gratuit** pour générer automatiquement une **newsletter HTML** sur le photovoltaïque :
- **GitHub Actions** (gratuit sur dépôts publics) exécute un script Python selon un **cron**.
- Les données proviennent de **sources officielles** : CRE (data.gouv.fr), Legifrance, EDF OA, Enedis.
- Le HTML est publié via **GitHub Pages** (répertoire `docs/`).

## Démarrage rapide
1. Créez un **dépôt public** sur GitHub, puis activez **Pages** en source `docs/` (paramètres > Pages).
2. Copiez ces fichiers dans le dépôt.
3. Modifiez `data/edito.md` avant chaque envoi (ou laissez vide si vous n’avez pas d’édito).
4. (Optionnel) Modifiez `config.yaml` pour changer la structure/blocs.
5. Lancement : le workflow tourne automatiquement (cron) et vous pouvez aussi faire **Run workflow** à la main.

## Local
```bash
pip install -r requirements.txt
python newsletter.py
# Ouvrir docs/index.html dans votre navigateur
```

## Structure par défaut (6 blocs basiques)
1) **Édito** (manuel)  
2) **Actu réglementaire** (liens Legifrance + EDF OA)  
3) **Chiffre du mois** (extrait automatiquement des jeux CRE)  
4) **Cas concret** (placeholder ; vous pouvez coder un calcul ROI)  
5) **Conseil pratique** (Enedis)  
6) **Contact & CTA** (fixe)

> Remarque : ce script **n’aspire pas** photovoltaique.info (robots.txt). Il se base sur les **sources primaires**.
