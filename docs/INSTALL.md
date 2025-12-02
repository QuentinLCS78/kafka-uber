# 📖 Guide d'Installation et d'Exécution

Guide pas à pas pour installer et exécuter le projet **Mini Uber / Tracking Taxi avec Kafka** sur Windows.

---

## ⚡ Démarrage rapide - Ordre des étapes IMPORTANT

**⚠️ Pour éviter les erreurs, suivez cet ordre exact :**

1. ✅ **Installez Python et Java** (voir section 1)
2. ✅ **Téléchargez et extrayez Kafka** (voir section 2)
3. ✅ **Créez l'environnement virtuel Python** (voir section 3)
4. ✅ **⚠️ INSTALLEZ les dépendances** : `pip install -r requirements.txt` (section 3, étape 4)
5. ✅ **Démarrez Kafka** (Zookeeper + Broker) (voir section 4)
6. ✅ **Créez le topic** après que Kafka soit démarré (voir section 4, étape 3)
7. ✅ **Lancez le producer** (voir section 5)
8. ✅ **Lancez le consumer Streamlit** (voir section 6)

**❌ Erreurs courantes :**
- `ModuleNotFoundError: No module named 'kafka'` → Vous n'avez pas fait l'étape 4 (installer les dépendances)
- `Broker may not be available` → Vous n'avez pas fait l'étape 5 (démarrer Kafka) avant l'étape 6 (créer le topic)

---

## 1️⃣ Prérequis

Avant de commencer, assurez-vous d'avoir installé :

### Python 3

- **Version requise** : Python 3.8 ou supérieur
- **Vérification** : Ouvrez PowerShell et tapez :
  ```powershell
  python --version
  ```
- **Installation** : Téléchargez depuis [python.org](https://www.python.org/downloads/) si nécessaire

### Java

Kafka nécessite Java pour fonctionner.

- **Version requise** : Java 8 ou supérieur (Java 11+ recommandé)
- **Vérification** :
  ```powershell
  java -version
  ```
- **Installation** : Téléchargez depuis [Oracle](https://www.oracle.com/java/technologies/downloads/) ou [OpenJDK](https://adoptium.net/)

### Apache Kafka

- **Téléchargement** : Rendez-vous sur [kafka.apache.org/downloads](https://kafka.apache.org/downloads)
- **Version recommandée** : Version stable la plus récente
- **Format** : Téléchargez le fichier `.tgz` (pour Windows, utilisez un outil comme 7-Zip pour extraire)

---

## 2️⃣ Installation de Kafka

### Étape 1 : Extraire Kafka

1. Téléchargez l'archive Kafka (exemple : `kafka_2.13-3.5.0.tgz`)
2. Extrayez l'archive dans un dossier accessible, par exemple :
   ```
   C:\kafka
   ```
3. Vous devriez avoir une structure comme :
   ```
   C:\kafka\
   ├── bin\
   ├── config\
   ├── libs\
   └── ...
   ```

### Étape 2 : Configuration de Kafka

La configuration par défaut fonctionne généralement pour un environnement de développement local. Vous pouvez laisser les fichiers de configuration tels quels dans `config\`.

**Note importante** : Kafka peut fonctionner avec ou sans Zookeeper selon la version :
- **Versions récentes (3.3+)** : Supportent le mode **KRaft** (sans Zookeeper)
- **Versions anciennes** : Nécessitent **Zookeeper**

Pour simplifier, ce guide couvre les deux approches.

---

## 3️⃣ Configuration de l'environnement Python

> ⚠️ **IMPORTANT** : Suivez les étapes dans l'ordre. Ne sautez pas l'installation des dépendances !

### Étape 1 : Naviguer vers le projet

```powershell
cd C:\Users\Quent\OneDrive\Bureau\kafka-uber
```

Ou le chemin où vous avez placé le projet.

### Étape 2 : Créer l'environnement virtuel

```powershell
python -m venv venv
```

### Étape 3 : Activer l'environnement virtuel

**PowerShell** :
```powershell
venv\Scripts\Activate.ps1
```

**Si vous obtenez une erreur d'exécution de scripts**, exécutez d'abord :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Invite de commande (cmd)** :
```cmd
venv\Scripts\activate.bat
```

Une fois activé, vous devriez voir `(venv)` au début de votre ligne de commande.

### Étape 4 : Installer les dépendances

**Avant d'installer, mettez à jour pip** (recommandé pour éviter les problèmes de compilation) :

```powershell
python -m pip install --upgrade pip
```

**Ensuite, installez les dépendances** :

```powershell
pip install -r requirements.txt
```

**⚠️ IMPORTANT : Cette étape est obligatoire avant de lancer les scripts Python !**

Vous devriez voir l'installation des packages :
- kafka-python
- streamlit
- folium
- streamlit-folium
- numpy (dépendance de streamlit, avec wheel précompilé)

**Vérification** : Pour vérifier que les packages sont bien installés :

```powershell
pip list | findstr kafka
pip list | findstr streamlit
pip list | findstr numpy
```

Vous devriez voir `kafka-python`, `streamlit` et `numpy` dans la liste.

> 💡 **Note** : Si vous rencontrez une erreur de compilation (notamment avec numpy), consultez la section de dépannage ci-dessous.

---

## 4️⃣ Lancement de Kafka

### Option A : Kafka avec Zookeeper (versions < 3.3)

#### Étape 1 : Démarrer Zookeeper

Ouvrez un **premier terminal PowerShell** et naviguez vers Kafka :

```powershell
cd C:\kafka
```

Démarrez Zookeeper :

```powershell
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
```

Laissez ce terminal ouvert. Vous devriez voir des logs indiquant que Zookeeper est démarré.

#### Étape 2 : Démarrer le broker Kafka

Ouvrez un **second terminal PowerShell** :

```powershell
cd C:\kafka
.\bin\windows\kafka-server-start.bat .\config\server.properties
```

Laissez également ce terminal ouvert. Vous devriez voir des logs indiquant que le broker Kafka est démarré.

### Option B : Kafka en mode KRaft (versions 3.3+)

Pour les versions récentes de Kafka qui supportent KRaft (sans Zookeeper) :

> ⚠️ **IMPORTANT** : Le formatage du stockage est **OBLIGATOIRE** avant de démarrer Kafka en mode KRaft. Si vous voyez l'erreur "No `meta.properties` found", vous devez d'abord formater le répertoire.

#### Étape 1 : Formater le stockage (OBLIGATOIRE - première fois seulement)

Avant de démarrer Kafka en mode KRaft, vous devez formater le répertoire de stockage.

**Génération d'un UUID pour le Cluster ID** :

⚠️ **IMPORTANT** : La méthode la plus simple et fiable est d'utiliser la commande intégrée de Kafka qui génère automatiquement un UUID compatible.

**Méthode 1 - Utiliser la commande Kafka (RECOMMANDÉE)** :

Kafka fournit une commande pour générer un UUID compatible :

```powershell
cd C:\kafka
.\bin\windows\kafka-storage.bat random-uuid
```

Cette commande génère directement un UUID compatible avec Kafka (exemple : `4LBwTZK_QhCTbsmqDPw4lw`).

**Méthode 2 - PowerShell (alternative)** :

Si vous préférez générer un UUID manuellement, assurez-vous qu'il fait exactement 32 caractères hexadécimaux :

```powershell
([guid]::NewGuid()).ToString().Replace('-', '')
```

Vérifiez que le résultat fait bien 32 caractères (pas 34, pas 30). Si ce n'est pas le cas, utilisez la Méthode 1.

**Méthode 3 - Python** (si Python est installé) :

```powershell
python -c "import uuid; print(str(uuid.uuid4()).replace('-', ''))"
```

Vérifiez que le résultat fait exactement 32 caractères.

**Formater le répertoire** :

Une fois que vous avez un UUID (généré avec `kafka-storage.bat random-uuid` ou manuellement), exécutez cette commande :

⚠️ **IMPORTANT** : Attention aux espaces dans la commande ! Utilisez un espace entre chaque option.

```powershell
cd C:\kafka
.\bin\windows\kafka-storage.bat format -t VOTRE-UUID -c .\config\kraft\server.properties
```

**Exemple concret** avec un UUID généré par Kafka :
```powershell
cd C:\kafka
.\bin\windows\kafka-storage.bat format -t 4LBwTZK_QhCTbsmqDPw4lw -c .\config\kraft\server.properties
```

**Exemple avec un UUID manuel** (32 caractères hexadécimaux) :
```powershell
cd C:\kafka
.\bin\windows\kafka-storage.bat format -t a1b2c3d4e5f67890abcdef1234567890 -c .\config\kraft\server.properties
```

> 💡 **Conseil** : Utilisez toujours des **espaces** entre les options :
> - ✅ Correct : `-t UUID -c config`
> - ❌ Incorrect : `-tUUID-c config` (sans espaces)

> ⚠️ **Rappel** : L'UUID doit être composé de 32 caractères hexadécimaux **sans tirets** (exemple : `370e4e9e9f854ab4b509342b7682c91a` au lieu de `370e4e9e-9f85-4ab4-b509-342b7682c91a`)

**Si la commande réussit**, vous verrez quelque chose comme :
```
Formatting /tmp/kraft-combined-logs with metadata.version 3.5-IV2
```

> **Note** : Cette étape n'est nécessaire qu'**une seule fois**. Si vous l'avez déjà faite et que vous voyez encore l'erreur, vérifiez que le répertoire de logs dans la configuration KRaft correspond bien à celui que vous avez formaté.

#### Étape 2 : Démarrer Kafka en mode KRaft

Une fois le stockage formaté, vous pouvez démarrer Kafka :

```powershell
cd C:\kafka
.\bin\windows\kafka-server-start.bat .\config\kraft\server.properties
```

Laissez ce terminal ouvert. Vous devriez voir des logs indiquant que Kafka démarre et fonctionne.

---

### Étape 3 : Créer le topic

⚠️ **IMPORTANT** : Assurez-vous que Kafka est **démarré et en cours d'exécution** avant de créer le topic !

Si vous voyez l'erreur :
```
Connection to node -1 (localhost/127.0.0.1:9092) could not be established. 
Broker may not be available.
```

Cela signifie que Kafka n'est pas démarré. Retournez à l'étape 2 et démarrez Kafka d'abord.

---

Une fois Kafka démarré (avec Zookeeper ou en KRaft), ouvrez un **nouveau terminal PowerShell** :

```powershell
cd C:\kafka
```

Créez le topic `taxi_positions` :

```powershell
.\bin\windows\kafka-topics.bat --create --topic taxi_positions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

**Si la commande réussit**, vous devriez voir :
```
Created topic taxi_positions.
```

**Vérification** : Pour vérifier que le topic a été créé :

```powershell
.\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
```

Vous devriez voir `taxi_positions` dans la liste.

---

## 5️⃣ Lancement du Producer

⚠️ **IMPORTANT - Vérifications avant de lancer le producer :**

1. ✅ **Kafka est démarré** (Zookeeper + Broker, ou KRaft seul)
2. ✅ **Le topic `taxi_positions` existe** (vérifiez avec la commande `--list`)
3. ✅ **L'environnement virtuel est activé** et les dépendances sont installées

Si vous voyez l'erreur `ModuleNotFoundError: No module named 'kafka'`, cela signifie que vous n'avez pas installé les dépendances. 

**Solution** :
```powershell
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

Ouvrez un **nouveau terminal PowerShell** :

```powershell
cd C:\Users\Quent\OneDrive\Bureau\kafka-uber
venv\Scripts\Activate.ps1
python producer/producer.py
```

### Ce que vous devriez voir :

```
============================================================
🚕 PRODUCER KAFKA - Taxi Position Tracker
============================================================
[INFO] Connexion à Kafka sur localhost:9092
[INFO] Topic : taxi_positions
[INFO] Taxi ID : 1
[INFO] Position initiale : lat=48.8566, lon=2.3522
------------------------------------------------------------
[INFO] Producer créé avec succès. Démarrage de l'envoi des positions...
[INFO] Appuyez sur Ctrl+C pour arrêter.

[PRODUCER] Position envoyée : id=1, lat=48.856600, lon=2.352200
[PRODUCER] Position envoyée : id=1, lat=48.856845, lon=2.352312
[PRODUCER] Position envoyée : id=1, lat=48.857123, lon=2.352456
...
```

Le producer envoie maintenant des positions toutes les secondes. **Laissez ce terminal ouvert**.

---

## 6️⃣ Lancement du Consumer Streamlit

Ouvrez un **nouveau terminal PowerShell** (le producer continue de tourner dans l'autre terminal) :

```powershell
cd C:\Users\Quent\OneDrive\Bureau\kafka-uber
venv\Scripts\Activate.ps1
streamlit run consumer/streamlit_consumer.py
```

### Ce qui va se passer :

1. Streamlit va démarrer et vous verrez quelque chose comme :
   ```
   You can now view your Streamlit app in your browser.
   
   Local URL: http://localhost:8501
   Network URL: http://192.168.x.x:8501
   ```

2. **Votre navigateur s'ouvrira automatiquement** sur l'application Streamlit.

3. Vous verrez :
   - 🗺️ **Une carte interactive** centrée sur Paris (coordonnées initiales)
   - 📍 **Un marqueur rouge** représentant le taxi
   - 📊 **Les coordonnées** (ID, Latitude, Longitude) sous la carte

4. **Au fur et à mesure** que le producer envoie de nouvelles positions :
   - Le marqueur sur la carte se déplace
   - Les coordonnées se mettent à jour
   - Un compteur affiche le nombre de messages reçus

5. La page se **rafraîchit automatiquement** toutes les secondes pour afficher la dernière position.

### Panneau latéral

Dans la barre latérale de Streamlit, vous trouverez :
- Instructions d'utilisation
- Statistiques (nombre de messages reçus)
- Bouton pour rafraîchir manuellement
- Bouton pour réinitialiser le consumer

---

## 7️⃣ Test complet

### Vérification que tout fonctionne

1. ✅ **Kafka est démarré** (Zookeeper + Broker, ou KRaft seul)
2. ✅ **Le topic `taxi_positions` existe**
3. ✅ **Le producer envoie des positions** (vous voyez les logs dans son terminal)
4. ✅ **L'application Streamlit est ouverte** dans votre navigateur
5. ✅ **Le marqueur bouge** sur la carte au fur et à mesure

### Résultat attendu

- La carte montre Paris avec un marqueur de taxi
- Le marqueur se déplace progressivement (petits mouvements aléatoires)
- Les coordonnées sous la carte changent à chaque nouveau message
- Vous voyez des messages de confirmation dans Streamlit

---

## 8️⃣ Arrêt propre

### Arrêter le producer

Dans le terminal du producer, appuyez sur :
```
Ctrl+C
```

Vous verrez :
```
[INFO] Arrêt demandé par l'utilisateur (Ctrl+C)
[INFO] Fermeture du producer...
[INFO] Producer fermé proprement.
[INFO] Au revoir ! 👋
```

### Arrêter Streamlit

Dans le terminal de Streamlit, appuyez sur :
```
Ctrl+C
```

Ou fermez simplement l'onglet du navigateur.

### Arrêter Kafka

Dans le terminal du broker Kafka, appuyez sur :
```
Ctrl+C
```

Si vous utilisez Zookeeper, arrêtez-le également dans son terminal avec `Ctrl+C`.

---

## 🐛 Dépannage

### ❌ Erreur 1 : "ModuleNotFoundError: No module named 'kafka'"

**Symptômes** :
```
Traceback (most recent call last):
  File "producer/producer.py", line 9, in <module>
    from kafka import KafkaProducer
ModuleNotFoundError: No module named 'kafka'
```

**Cause** : Les dépendances Python n'ont pas été installées dans l'environnement virtuel.

**Solution** :
1. **Activez l'environnement virtuel** :
   ```powershell
   venv\Scripts\Activate.ps1
   ```
   Vous devez voir `(venv)` au début de la ligne de commande.

2. **Installez les dépendances** :
   ```powershell
   pip install -r requirements.txt
   ```

3. **Vérifiez l'installation** :
   ```powershell
   pip list | findstr kafka
   ```
   Vous devriez voir `kafka-python` dans la liste.

4. **Relancez le script** :
   ```powershell
   python producer/producer.py
   ```

---

### ❌ Erreur 2 : "Connection to node -1 (localhost/127.0.0.1:9092) could not be established"

**Symptômes** :
```
WARN [AdminClient clientId=adminclient-1] Connection to node -1 
(localhost/127.0.0.1:9092) could not be established. 
Broker may not be available.
```

**Cause** : Kafka n'est pas démarré ou n'écoute pas sur le port 9092.

**Solution** :

1. **Vérifiez que Kafka est démarré** :
   - Vous devez avoir un terminal avec Zookeeper en cours d'exécution (si nécessaire)
   - Vous devez avoir un terminal avec le broker Kafka en cours d'exécution

2. **Démarrez Kafka si nécessaire** :
   
   **Option A - Avec Zookeeper** :
   ```powershell
   # Terminal 1 - Zookeeper
   cd C:\kafka
   .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
   
   # Terminal 2 - Broker Kafka
   cd C:\kafka
   .\bin\windows\kafka-server-start.bat .\config\server.properties
   ```
   
   **Option B - Mode KRaft (sans Zookeeper)** :
   
   ⚠️ **Si vous n'avez jamais utilisé KRaft auparavant**, formatez d'abord le stockage :
   ```powershell
   # 1. Générer un UUID compatible (RECOMMANDÉ)
   cd C:\kafka
   .\bin\windows\kafka-storage.bat random-uuid
   # Copiez l'UUID généré (exemple : 4LBwTZK_QhCTbsmqDPw4lw)
   
   # 2. Formater le stockage (remplacez VOTRE-UUID par l'UUID généré)
   .\bin\windows\kafka-storage.bat format -t VOTRE-UUID -c .\config\kraft\server.properties
   # ⚠️ Attention : utilisez des espaces entre -t, -c et leurs valeurs
   
   # 3. Démarrer Kafka
   .\bin\windows\kafka-server-start.bat .\config\kraft\server.properties
   ```
   
   **Si vous avez déjà formaté précédemment** :
   ```powershell
   cd C:\kafka
   .\bin\windows\kafka-server-start.bat .\config\kraft\server.properties
   ```

3. **Attendez quelques secondes** que Kafka démarre complètement (vous verrez des logs dans les terminaux).

4. **Vérifiez que Kafka écoute sur le port 9092** :
   ```powershell
   netstat -ano | findstr :9092
   ```
   Vous devriez voir une ligne avec `LISTENING`.

5. **Testez la connexion** :
   ```powershell
   cd C:\kafka
   .\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
   ```
   Si cette commande fonctionne, Kafka est bien démarré.

6. **Créez le topic** si nécessaire :
   ```powershell
   .\bin\windows\kafka-topics.bat --create --topic taxi_positions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   ```

---

### ❌ Erreur 3 : "No `meta.properties` found in /tmp/kraft-combined-logs"

**Symptômes** :
```
ERROR Exiting Kafka due to fatal exception
org.apache.kafka.common.KafkaException: No `meta.properties` found in /tmp/kraft-combined-logs 
(have you run `kafka-storage.sh` to format the directory?)
```

**Cause** : Vous essayez de démarrer Kafka en mode KRaft sans avoir formaté le répertoire de stockage au préalable.

**Solution** :

1. **Générez un UUID compatible** :
   
   **Option A - Commande Kafka (RECOMMANDÉE)** :
   ```powershell
   cd C:\kafka
   .\bin\windows\kafka-storage.bat random-uuid
   ```
   Copiez l'UUID généré (exemple : `4LBwTZK_QhCTbsmqDPw4lw`)
   
   **Option B - PowerShell** :
   ```powershell
   ([guid]::NewGuid()).ToString().Replace('-', '')
   ```
   Vérifiez que le résultat fait **exactement 32 caractères** (pas 34, pas 30). Copiez l'UUID généré.

2. **Formatez le répertoire de stockage** :
   
   ⚠️ **IMPORTANT** : Utilisez des **espaces** entre chaque option dans la commande.
   
   ```powershell
   cd C:\kafka
   .\bin\windows\kafka-storage.bat format -t VOTRE-UUID -c .\config\kraft\server.properties
   ```
   
   **Exemple avec UUID généré par Kafka** :
   ```powershell
   .\bin\windows\kafka-storage.bat format -t 4LBwTZK_QhCTbsmqDPw4lw -c .\config\kraft\server.properties
   ```
   
   **Exemple avec UUID manuel** (32 caractères) :
   ```powershell
   .\bin\windows\kafka-storage.bat format -t a1b2c3d4e5f67890abcdef1234567890 -c .\config\kraft\server.properties
   ```
   
   > ⚠️ **Erreurs courantes** :
   > - Si vous voyez "does not appear to be a valid UUID" : Votre UUID n'est pas au bon format ou a une mauvaise longueur
   > - Si vous voyez "unrecognized arguments" : Vérifiez qu'il y a des espaces entre `-t`, `-c` et leurs valeurs
   > - L'UUID doit faire exactement 32 caractères (pas 34, pas 30)

3. **Vérifiez que le formatage a réussi** :
   Vous devriez voir un message de succès comme :
   ```
   Formatting /tmp/kraft-combined-logs with metadata.version 3.5-IV2
   ```

4. **Maintenant vous pouvez démarrer Kafka** :
   ```powershell
   .\bin\windows\kafka-server-start.bat .\config\kraft\server.properties
   ```

> **Note** : Le formatage n'est nécessaire qu'**une seule fois**. Si vous avez déjà formaté et que vous voyez encore l'erreur, vérifiez :
> - Que vous utilisez le même UUID que lors du formatage
> - Que le répertoire de logs dans la configuration KRaft correspond au répertoire formaté
> - Si vous avez changé le répertoire de logs dans la config, vous devrez reformater

---

### ❌ Erreur 4 : "Cluster ID string does not appear to be a valid UUID"

**Symptômes** :
```
Cluster ID string 370e4e9-9f85-4ab4-b509-342b7682c91a does not appear to be a valid UUID: 
Input string with prefix `370e4e9-9f85-4ab4-b509-3` is too long to be decoded as a base64 UUID
```

**Cause** : Vous avez utilisé un UUID avec des tirets, mais Kafka KRaft nécessite un UUID **sans tirets** (32 caractères hexadécimaux continus).

**Solution** :

1. **Générez un UUID SANS tirets** :
   ```powershell
   ([guid]::NewGuid()).ToString().Replace('-', '')
   ```
   Vous obtiendrez quelque chose comme : `370e4e9e9f854ab4b509342b7682c91a` (32 caractères, sans tirets)

2. **Utilisez cet UUID sans tirets pour formater** :
   ```powershell
   cd C:\kafka
   .\bin\windows\kafka-storage.bat format -t 370e4e9e9f854ab4b509342b7682c91a -c .\config\kraft\server.properties
   ```

> 💡 **Astuce** : Si vous avez déjà un UUID avec tirets, supprimez simplement les tirets manuellement :
> - Avant : `370e4e9e-9f85-4ab4-b509-342b7682c91a`
> - Après : `370e4e9e9f854ab4b509342b7682c91a`

---

### ❌ Erreur 5 : "unrecognized arguments" lors du formatage

**Symptômes** :
```
kafka-storage: error: unrecognized arguments: '.\config\kraft\server.properties'
```

**Cause** : Il manque des espaces dans la commande entre les options et leurs valeurs. La commande a été écrite sans espaces entre `-t`, `-c` et leurs valeurs.

**Solution** :

Vérifiez que vous avez bien des **espaces** entre chaque option et sa valeur :

**❌ Incorrect** (sans espaces) :
```powershell
.\bin\windows\kafka-storage.bat format -t5aee5a02458b4617bf9e35d9312e65af-c .\config\kraft\server.properties
```

**✅ Correct** (avec espaces) :
```powershell
.\bin\windows\kafka-storage.bat format -t 5aee5a02458b4617bf9e35d9312e65af -c .\config\kraft\server.properties
```

Notez les espaces :
- `-t` (espace) `UUID`
- `-c` (espace) `.\config\kraft\server.properties`

**Commande complète correcte** :
```powershell
cd C:\kafka
.\bin\windows\kafka-storage.bat format -t VOTRE-UUID -c .\config\kraft\server.properties
```

---

### ❌ Erreur : "Impossible de créer le producer Kafka"

**Cause** : Kafka n'est pas démarré ou n'écoute pas sur `localhost:9092`.

**Solution** :
1. Suivez la solution de l'erreur 2 ci-dessus
2. Vérifiez les logs dans les terminaux Kafka pour des erreurs
3. Testez la connexion :
   ```powershell
   cd C:\kafka
   .\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
   ```

### Erreur : "Topic 'taxi_positions' does not exist"

**Cause** : Le topic n'a pas été créé.

**Solution** : Créez le topic (voir section 4, étape 3).

### ❌ Erreur 6 : Erreur de compilation numpy lors de l'installation

**Symptômes** :
```
ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc'], ['clang'], ['clang-cl'], ['pgcc']]
error: metadata-generation-failed
× Encountered error while generating package metadata.
```

**Cause** : NumPy essaie de se compiler depuis les sources car il ne trouve pas de wheel précompilé pour votre système. Cela nécessite un compilateur C++ (Visual Studio Build Tools).

**Solution** :

**Méthode 1 - Mettre à jour pip et réessayer (RECOMMANDÉ)** :

1. **Mettez à jour pip** :
   ```powershell
   python -m pip install --upgrade pip
   ```

2. **Réessayez l'installation** :
   ```powershell
   pip install -r requirements.txt
   ```

   La nouvelle version de pip devrait télécharger des wheels précompilés au lieu de compiler.

**Méthode 2 - Installer numpy séparément avec une version précompilée** :

Si la méthode 1 ne fonctionne pas :

1. **Installez numpy avec une version qui a un wheel précompilé** :
   ```powershell
   pip install numpy
   ```

2. **Ensuite, installez le reste** :
   ```powershell
   pip install -r requirements.txt
   ```

**Méthode 3 - Installer Visual Studio Build Tools (si les méthodes précédentes échouent)** :

Cette méthode est plus lourde mais garantit que tout fonctionne :

1. Téléchargez et installez [Visual Studio Build Tools](https://visualstudio.microsoft.com/fr/visual-cpp-build-tools/)
2. Sélectionnez la charge de travail **"Développement Desktop en C++"** lors de l'installation
3. Après l'installation, redémarrez PowerShell et réessayez :
   ```powershell
   pip install -r requirements.txt
   ```

> 💡 **Conseil** : Dans 99% des cas, la Méthode 1 (mettre à jour pip) résout le problème.

### Erreur : "Java is not recognized"

**Cause** : Java n'est pas installé ou pas dans le PATH.

**Solution** :
1. Installez Java
2. Ajoutez Java au PATH système
3. Redémarrez PowerShell

### Le marqueur ne bouge pas sur la carte

**Causes possibles** :
1. Le producer n'envoie pas de messages (vérifiez son terminal)
2. Le consumer ne reçoit pas les messages (vérifiez les erreurs dans Streamlit)
3. La page Streamlit n'a pas été rafraîchie

**Solution** :
1. Vérifiez les logs du producer
2. Regardez la console Streamlit pour des erreurs
3. Cliquez sur "Rafraîchir manuellement" dans la sidebar
4. Vérifiez que Kafka reçoit bien les messages :
   ```powershell
   cd C:\kafka
   .\bin\windows\kafka-console-consumer.bat --topic taxi_positions --from-beginning --bootstrap-server localhost:9092
   ```

### Port 9092 déjà utilisé

**Cause** : Un autre processus utilise le port 9092.

**Solution** :
1. Trouvez le processus : `netstat -ano | findstr :9092`
2. Arrêtez le processus ou changez le port dans `config/server.properties`

---

## 📝 Notes supplémentaires

### Modifier la configuration

Si vous souhaitez changer les paramètres (port Kafka, coordonnées initiales, etc.), modifiez directement les constantes dans :
- `producer/producer.py` (lignes de configuration en haut)
- `consumer/streamlit_consumer.py` (lignes de configuration en haut)

### Ajouter plusieurs taxis

Pour simuler plusieurs taxis, modifiez `TAXI_ID` dans `producer/producer.py` et lancez plusieurs instances du producer avec des IDs différents.

### Consulter les messages Kafka directement

Pour voir les messages dans le topic sans passer par Streamlit :

```powershell
cd C:\kafka
.\bin\windows\kafka-console-consumer.bat --topic taxi_positions --from-beginning --bootstrap-server localhost:9092
```

---

## ✅ Checklist finale

Avant de considérer que tout est configuré :

- [ ] Python 3 installé et accessible
- [ ] Java installé et accessible
- [ ] Kafka téléchargé et extrait
- [ ] Environnement virtuel Python créé et activé
- [ ] Dépendances Python installées (`pip install -r requirements.txt`)
- [ ] Zookeeper démarré (si nécessaire)
- [ ] Broker Kafka démarré
- [ ] Topic `taxi_positions` créé
- [ ] Producer lancé et envoie des messages
- [ ] Consumer Streamlit lancé et affiche la carte

---

**🎉 Félicitations ! Vous avez maintenant un système de suivi de taxi fonctionnel avec Kafka !**

Pour toute question ou problème, référez-vous aux sections de dépannage ci-dessus.

