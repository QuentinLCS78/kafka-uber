# 🚕 Mini Uber / Tracking Taxi avec Kafka

## Description

Ce projet simule un système de suivi de taxi en temps réel utilisant **Apache Kafka** comme système de messagerie. 

Un **producer** Python envoie les positions GPS d'un taxi qui se déplace dans Paris, ces positions sont transportées par **Kafka**, et un **consumer** Streamlit les consomme pour afficher la position du taxi sur une carte interactive en temps réel.

## Choix de technologie

Nous avons choisi Apache Kafka car c’est l’outil le plus adapté pour gérer des données en continu et en temps réel, comme les positions GPS du taxi. Kafka permet d’envoyer et de consommer des messages avec une très faible latence, de manière fiable, scalable et indépendante entre producer et consumer. Il peut stocker les messages même si l’application Streamlit n’est pas encore lancée, et il s’intègre parfaitement dans un écosystème Big Data moderne (Spark, Hadoop, Hive, etc.). C’est donc la solution idéale pour un projet de type “Mini Uber”.

## Kafka dans l’écosystème Big Data

Dans un écosystème Big Data, Kafka joue le rôle de “canal d’ingestion” : il récupère des flux continus de données (logs, capteurs, positions GPS, transactions…) et les transmet en temps réel aux autres outils de la plateforme. Les données envoyées dans Kafka peuvent ensuite être traitées par Spark Streaming ou Flink, stockées dans HDFS ou Hive, analysées par des moteurs SQL, ou visualisées dans des dashboards. Kafka sert donc de couche centrale de streaming permettant de connecter facilement la collecte, le traitement et l’analyse des données au sein d’une architecture Big Data moderne.

## Challenges rencontrés


Les principaux challenges rencontrés ont été liés à la configuration de Kafka et aux échanges entre le producer et le consumer. Nous avons notamment eu des erreurs “NoBrokersAvailable” lorsque Kafka n’était pas correctement démarré, des problèmes de PATH Java, ainsi que des difficultés à faire communiquer Streamlit avec le flux Kafka en temps réel. Nous avons aussi dû ajuster la fréquence d’envoi des positions GPS pour éviter les blocages, et corriger plusieurs erreurs dues au virtualenv ou au topic non créé. En suivant les logs, en recréant proprement le venv, en vérifiant le broker et en testant séparément chaque composant, nous avons pu résoudre ces problèmes progressivement.

## Architecture

```
┌─────────────────┐
│   Producer      │
│  (producer.py)  │
│                 │
│  Envoie positions│
│  GPS toutes les │
│  1 seconde      │
└────────┬────────┘
         │
         │ Messages JSON
         │ {id, lat, lon}
         ▼
┌─────────────────┐
│     Kafka       │
│                 │
│ Topic:          │
│ taxi_positions  │
└────────┬────────┘
         │
         │ Consommation
         │ continue
         ▼
┌─────────────────┐
│   Consumer      │
│  Streamlit App  │
│                 │
│  Affiche carte  │
│  interactive    │
│  avec Folium    │
└─────────────────┘
```

## Structure du projet

```
projet_kafka/
│
├── producer/
│   └── producer.py              # Producer Kafka qui envoie les positions GPS
│
├── consumer/
│   └── streamlit_consumer.py    # Application Streamlit avec carte en temps réel
│
├── docs/
│   └── INSTALL.md               # Guide d'installation et d'exécution détaillé
│
├── requirements.txt             # Dépendances Python
└── README.md                    # Ce fichier
```

## Prérequis

- Python 3.8 ou supérieur
- Java (nécessaire pour Kafka)
- Apache Kafka installé et configuré

> 📖 Pour un guide d'installation détaillé pas à pas, consultez **[docs/INSTALL.md](docs/INSTALL.md)**

## Installation rapide

### 1. Créer l'environnement virtuel

```powershell
cd projet_kafka
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2. Installer les dépendances

```powershell
pip install -r requirements.txt
```

### 3. Lancer Kafka

Assurez-vous que Kafka est démarré :
- Zookeeper (si nécessaire pour votre version)
- Broker Kafka sur `localhost:9092`

### 4. Créer le topic

```powershell
bin\windows\kafka-topics.bat --create --topic taxi_positions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

## Utilisation

### Lancer le producer

Dans un premier terminal :

```powershell
venv\Scripts\Activate.ps1
python producer/producer.py
```

Vous devriez voir les messages de position envoyés dans la console :
```
[PRODUCER] Position envoyée : id=1, lat=48.856600, lon=2.352200
```

### Lancer le consumer Streamlit

Dans un second terminal :

```powershell
venv\Scripts\Activate.ps1
streamlit run consumer/streamlit_consumer.py
```

Votre navigateur s'ouvrira automatiquement sur l'application Streamlit qui affichera :
- Une carte interactive centrée sur Paris
- Un marqueur représentant le taxi qui se déplace en temps réel
- Les dernières coordonnées reçues sous la carte

## Mes Setup notes

Lors de la mise en place du projet, nous avons rencontré plusieurs difficultés techniques liées à la configuration de Kafka. Nous avons d’abord tenté d’utiliser Kafka en mode KRaft (sans ZooKeeper), mais celui-ci refusait de démarrer correctement sur notre environnement Windows : erreurs de cluster ID, impossibilité d’initialiser les logs et plantages récurrents au lancement du broker. Après plusieurs essais et vérifications des logs, nous avons décidé de revenir à la version classique de Kafka basée sur ZooKeeper, qui s’est avérée beaucoup plus stable et simple à faire fonctionner.

Nous avons également dû ajuster le Java PATH pour que Kafka puisse se lancer, recréer plusieurs fois notre environnement virtuel Python à cause de conflits de dépendances, et résoudre l’erreur “NoBrokersAvailable” lorsque le broker n’était pas encore démarré ou lorsque le topic n’était pas créé. En testant chaque composant séparément (ZooKeeper → Kafka → producer → consumer) et en analysant attentivement les messages d’erreur, nous avons progressivement stabilisé tout l’environnement. Ces étapes nous ont permis de mieux comprendre le fonctionnement interne de Kafka et d’obtenir une configuration totalement opérationnelle.

## Fonctionnalités

### Producer (`producer/producer.py`)

- ✅ Simule un taxi qui se déplace à Paris
- ✅ Génère des positions GPS avec petites variations aléatoires
- ✅ Envoie les positions au topic Kafka toutes les 1 seconde
- ✅ Gestion d'erreurs si Kafka n'est pas disponible
- ✅ Format JSON : `{id, lat, lon, timestamp}`

### Consumer (`consumer/streamlit_consumer.py`)

- ✅ Application Streamlit moderne et interactive
- ✅ Carte Folium en temps réel avec marqueur du taxi
- ✅ Affichage des dernières coordonnées reçues
- ✅ Rafraîchissement automatique de la carte
- ✅ Statistiques des messages reçus

## Arrêt

- **Producer** : `Ctrl+C` dans le terminal
- **Streamlit** : `Ctrl+C` dans le terminal ou fermer l'onglet
- **Kafka** : Arrêter le broker et Zookeeper proprement si nécessaire

## Technologies utilisées

- **Python 3** : Langage principal
- **Apache Kafka** : Système de messagerie distribuée
- **kafka-python** : Client Python pour Kafka
- **Streamlit** : Framework pour créer des applications web interactives
- **Folium** : Bibliothèque Python pour créer des cartes Leaflet
- **streamlit-folium** : Intégration Folium dans Streamlit

## Screenshots
Lancement de Zookeeper
<img width="1696" height="455" alt="zookeeper" src="https://github.com/user-attachments/assets/c0f7297c-7a1c-4ddc-9375-f680acff9f9c" />

Lancement de Kafka
<img width="1687" height="277" alt="kafka" src="https://github.com/user-attachments/assets/0ce67b40-b172-43e0-936e-d7f6f83ed770" />

Lancement du producer
<img width="1166" height="732" alt="producer" src="https://github.com/user-attachments/assets/8b0050b2-f6fc-4211-b405-6807e5df3428" />

Lancement de Streamlit
<img width="1374" height="352" alt="streamlit" src="https://github.com/user-attachments/assets/115d607c-f1d7-463a-8bfc-889e64a1776f" />
<img width="1116" height="605" alt="1streamlite" src="https://github.com/user-attachments/assets/5d82284a-893d-4578-9c49-b32ccd7f5c96" />
<img width="1686" height="737" alt="2streamlite" src="https://github.com/user-attachments/assets/5ed2ebe7-391f-4047-8856-6b5a18c9f793" />
<img width="1532" height="226" alt="3treamlite" src="https://github.com/user-attachments/assets/1b417081-d016-485c-bec5-02ac7e8041c7" />
<img width="1722" height="699" alt="4streamlite" src="https://github.com/user-attachments/assets/5193b5b2-cfc8-4cd9-8c4e-571fffd348ca" />

## Documentation complète

Pour plus de détails sur l'installation, la configuration et le dépannage, consultez le guide complet :

👉 **[docs/INSTALL.md](docs/INSTALL.md)**

## Auteur

Projet créé pour apprendre et démontrer l'utilisation d'Apache Kafka avec Python.

## Licence

Ce projet est fourni à des fins éducatives.


