==================================================================================
 ✅  Projet SafeMail prêt pour Kubernetes créé dans 'safemail_k8s_project' ! 
==================================================================================

ÉTAPES:

1. Initialisez votre base de données externe :
   - Exécutez le script SQL 'db_init/init.sql' sur votre base de données RDS.

2. Construisez et poussez vos images Docker :
   export DOCKER_USER="votre_nom_dutilisateur_dockerhub" # ou votre registry
   docker build -t ${DOCKER_USER}/safemail-postfix:latest ./postfix
   docker build -t ${DOCKER_USER}/safemail-dovecot:latest ./dovecot
   docker build -t ${DOCKER_USER}/safemail-admin-app:latest ./admin-app
   docker push ${DOCKER_USER}/safemail-postfix:latest
   docker push ${DOCKER_USER}/safemail-dovecot:latest
   docker push ${DOCKER_USER}/safemail-admin-app:latest

3. Personnalisez les manifestes Kubernetes dans le dossier 'k8s/' :
   - Renommez tous les fichiers .yaml.sample en .yaml.
   - Dans '04-deployments.yaml.sample', remplacez 'VOTRE_REGISTRY' par votre nom d'utilisateur.
   - Dans '03-configmap.yaml.sample', définissez votre 'DOMAIN'.

4. Créez votre secret Kubernetes (adaptez le nom du secret si besoin) :
   kubectl create secret generic nxh-database-secret --namespace safemail \
     --from-literal=NXH_DATABASE_HOST='...' \
     --from-literal=NXH_DATABASE_PORT='...' \
     --from-literal=NXH_DATABASE_NAME='...' \
     --from-literal=NXH_DATABASE_USER='...' \
     --from-literal=NXH_DATABASE_PASSWORD='...' \
     --from-literal=NXH_FLASK_SECRET_KEY='une_cle_tres_longue_et_aleatoire'

5. Déployez l'application sur votre cluster :
   kubectl apply -f k8s/

6. Créez votre utilisateur administrateur (une fois les pods en cours d'exécution) :
   # Trouvez le nom du pod de l'application admin
   export ADMIN_POD=$(kubectl get pods -n safemail -l app=admin-app -o jsonpath='{.items[0].metadata.name}')
   # Exécutez la commande de création
   kubectl exec -n safemail $ADMIN_POD -- flask create-admin \
     --username 'admin' \
     --email 'admin@votre-domaine.com' \
     --password 'un_mot_de_passe_tres_securise'

7. Accédez à l'interface d'administration :
   # La meilleure méthode est de forwarder le port du service
   kubectl port-forward svc/admin-app-service -n safemail 8080:80
   # Ouvrez http://localhost:8080 dans votre navigateur.
