#!/bin/bash
set -e

echo "🚀 Démarrage de Biantos Agency..."

# Attendre que la base de données soit prête (si PostgreSQL)
# if [ "$DATABASE" = "postgres" ]; then
#     echo "Waiting for postgres..."
#     while ! nc -z $SQL_HOST $SQL_PORT; do
#       sleep 0.1
#     done
#     echo "PostgreSQL started"
# fi

# Appliquer les migrations
echo "📊 Application des migrations..."
python manage.py migrate --noinput

# Créer le superutilisateur si les variables sont définies
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "👤 Création du superutilisateur..."
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL \
        2>/dev/null || echo "Superutilisateur déjà existant"
fi

# Collecter les fichiers statiques
echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo "✅ Biantos Agency est prêt!"
echo "🌐 Accédez à l'application sur http://localhost:8000"

# Exécuter la commande passée en argument
exec "$@"
