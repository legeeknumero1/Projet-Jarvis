#!/bin/bash
# Script pour commiter le nettoyage de la documentation

echo " Nettoyage documentation Jarvis - Commit automatique"
echo ""

# Vérifier qu'on est dans un repo git
if [ ! -d .git ]; then
    echo " Erreur: Pas dans un dépôt git"
    exit 1
fi

echo " Fichiers modifiés:"
git status --short

echo ""
read -p "Continuer avec le commit? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo " Annulé"
    exit 1
fi

# Ajouter tous les changements
git add .gitattributes
git add .gitignore
git add docs/
git add CLEANUP_SUMMARY.md

# Supprimer les fichiers archivés de la racine (ils sont dans docs/archive/)
git rm -f POLYGLOT_ARCHITECTURE_ANALYSIS.md FRONTEND_ANALYSIS.md POLYGLOT_QUICK_REFERENCE.md RAPPORT_AUDIT_COMPLET_2025-10-26.md 2>/dev/null || true

# Commit
git commit -m "docs: reorganize documentation and fix GitHub linguist stats

- Add .gitattributes to exclude docs from language stats
- Archive obsolete documentation (250KB saved)
- Create docs/README.md index
- Update .gitignore to allow audit reports
- Centralize jarvis-secretsd docs in docs/

Impact:
- GitHub stats will show real code distribution (not 76% MD)
- Documentation better organized
- Archived files kept for history in docs/archive/

Refs: #linguist #documentation #cleanup"

echo ""
echo " Commit créé avec succès!"
echo ""
echo " Pour pousser sur GitHub:"
echo "   git push origin main"
echo ""
echo " Les stats GitHub se mettront à jour dans 1-2 heures"
