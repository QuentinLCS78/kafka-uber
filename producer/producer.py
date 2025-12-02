"""
Producer Kafka pour envoyer les positions GPS d'un taxi.
Simule un taxi qui se déplace à Paris en suivant des itinéraires réalistes entre des POI.
"""

import json
import time
import random
import sys

# Vérification de l'importation du module kafka
try:
    from kafka import KafkaProducer
    from kafka.errors import KafkaError
except ImportError as e:
    print("=" * 60)
    print("❌ ERREUR : Module 'kafka' non trouvé")
    print("=" * 60)
    print("\n💡 Solution : Installez les dépendances Python avec :")
    print("   1. Activez l'environnement virtuel :")
    print("      venv\\Scripts\\Activate.ps1")
    print("\n   2. Installez les dépendances :")
    print("      pip install -r requirements.txt")
    print("\n   3. Ou installez directement :")
    print("      pip install kafka-python")
    print("\n" + "=" * 60)
    sys.exit(1)

# Configuration Kafka
BOOTSTRAP_SERVERS = ["localhost:9092"]
TOPIC = "taxi_positions"

# Configuration du taxi
TAXI_ID = 1

# Liste de Points of Interest (POI) à Paris
# Format: (latitude, longitude, nom_du_lieu)
POI_LIST = [
    (48.8566, 2.3522, "Notre-Dame de Paris"),
    (48.8584, 2.2945, "Tour Eiffel"),
    (48.8606, 2.3376, "Louvre"),
    (48.8738, 2.2950, "Arc de Triomphe"),
    (48.8867, 2.3431, "Sacré-Cœur"),
]

# Configuration du déplacement
INTERPOLATION_POINTS = 100  # Nombre de points intermédiaires entre départ et arrivée
SPEED_FACTOR = 1.0  # Facteur de vitesse (1.0 = 1 point par seconde)


def create_producer():
    """Crée et retourne un producer Kafka."""
    try:
        print(f"[INFO] Tentative de connexion à Kafka sur {BOOTSTRAP_SERVERS[0]}...")
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: str(k).encode('utf-8') if k else None
        )
        
        # Test de connexion : essayer de lister les topics
        print(f"[INFO] Test de connexion en cours...")
        time.sleep(0.5)  # Petite pause pour la connexion
        
        return producer
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERREUR : Impossible de créer le producer Kafka")
        print("=" * 60)
        print(f"\n🔍 Détails de l'erreur : {e}")
        print("\n💡 Solutions possibles :")
        print("\n   1. Vérifiez que Kafka est démarré :")
        print("      - Zookeeper doit être lancé (si nécessaire)")
        print("      - Le broker Kafka doit être lancé sur localhost:9092")
        print("\n   2. Pour démarrer Kafka (dans un terminal séparé) :")
        print("      cd C:\\kafka")
        print("      .\\bin\\windows\\zookeeper-server-start.bat .\\config\\zookeeper.properties")
        print("      (puis dans un autre terminal)")
        print("      .\\bin\\windows\\kafka-server-start.bat .\\config\\server.properties")
        print("\n   3. Vérifiez que le port 9092 est disponible :")
        print("      netstat -ano | findstr :9092")
        print("\n   4. Créez le topic après avoir démarré Kafka :")
        print("      .\\bin\\windows\\kafka-topics.bat --create --topic taxi_positions")
        print("      --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1")
        print("\n" + "=" * 60)
        return None


def calculate_route(start_lat, start_lon, end_lat, end_lon, num_points):
    """
    Calcule un itinéraire avec interpolation linéaire entre deux points.
    
    Args:
        start_lat: Latitude de départ
        start_lon: Longitude de départ
        end_lat: Latitude d'arrivée
        end_lon: Longitude d'arrivée
        num_points: Nombre de points intermédiaires
    
    Returns:
        Liste de tuples (lat, lon) représentant le chemin
    """
    route = []
    
    # Calcul des différences
    lat_diff = end_lat - start_lat
    lon_diff = end_lon - start_lon
    
    # Génération des points intermédiaires
    for i in range(num_points + 1):  # +1 pour inclure le point d'arrivée
        # Interpolation linéaire
        ratio = i / num_points
        lat = start_lat + (lat_diff * ratio)
        lon = start_lon + (lon_diff * ratio)
        route.append((lat, lon))
    
    return route


def select_random_destination(current_destination_index):
    """
    Sélectionne une destination aléatoire différente de la précédente.
    
    Args:
        current_destination_index: Index de la destination actuelle (None si première fois)
    
    Returns:
        (index, lat, lon, nom): Tuple avec l'index et les coordonnées de la destination
    """
    available_indices = list(range(len(POI_LIST)))
    
    # Si on a déjà une destination, on l'exclut de la sélection
    if current_destination_index is not None:
        available_indices.remove(current_destination_index)
    
    # Sélection aléatoire parmi les destinations disponibles
    selected_index = random.choice(available_indices)
    poi = POI_LIST[selected_index]
    
    return selected_index, poi[0], poi[1], poi[2]


def send_taxi_position(producer, taxi_id, lat, lon):
    """Envoie une position de taxi au topic Kafka."""
    message = {
        "id": taxi_id,
        "lat": lat,
        "lon": lon,
        "timestamp": time.time()
    }
    
    try:
        # Envoi du message avec la clé = taxi_id pour garantir l'ordre par taxi
        future = producer.send(TOPIC, key=taxi_id, value=message)
        
        # Attendre la confirmation (optionnel, pour gérer les erreurs)
        record_metadata = future.get(timeout=10)
        
        print(f"[PRODUCER] Position envoyée : id={taxi_id}, lat={lat:.6f}, lon={lon:.6f}")
        return True
        
    except KafkaError as e:
        print(f"[ERREUR] Erreur Kafka lors de l'envoi : {e}")
        return False
    except Exception as e:
        print(f"[ERREUR] Erreur inattendue : {e}")
        return False


def main():
    """Fonction principale : boucle d'envoi des positions."""
    print("=" * 60)
    print("🚕 PRODUCER KAFKA - Taxi Position Tracker")
    print("=" * 60)
    print(f"[INFO] Connexion à Kafka sur {BOOTSTRAP_SERVERS[0]}")
    print(f"[INFO] Topic : {TOPIC}")
    print(f"[INFO] Taxi ID : {TAXI_ID}")
    print(f"[INFO] POI disponibles : {len(POI_LIST)} destinations")
    print(f"[INFO] Points d'interpolation : {INTERPOLATION_POINTS} par trajet")
    print("-" * 60)
    
    # Création du producer
    producer = create_producer()
    if producer is None:
        print("\n[ERREUR] Impossible de démarrer le producer. Arrêt du programme.")
        return
    
    print("[INFO] Producer créé avec succès. Démarrage de l'envoi des positions...")
    print("[INFO] Appuyez sur Ctrl+C pour arrêter.\n")
    
    # Position actuelle du taxi (commence au premier POI)
    current_lat, current_lon, _ = POI_LIST[0]
    current_route = []  # Liste des points du chemin actuel
    route_index = 0  # Index dans le chemin actuel
    current_destination_index = None  # Index de la destination actuelle
    
    try:
        while True:
            # Si on a terminé le chemin actuel, choisir une nouvelle destination
            if route_index >= len(current_route):
                # Sélectionner une nouvelle destination
                dest_index, dest_lat, dest_lon, dest_name = select_random_destination(
                    current_destination_index
                )
                current_destination_index = dest_index
                
                print(f"\n[INFO] 🎯 Nouvelle destination : {dest_name}")
                print(f"[INFO] Position actuelle : lat={current_lat:.6f}, lon={current_lon:.6f}")
                print(f"[INFO] Destination : lat={dest_lat:.6f}, lon={dest_lon:.6f}")
                
                # Calculer le nouveau chemin
                current_route = calculate_route(
                    current_lat, current_lon,
                    dest_lat, dest_lon,
                    INTERPOLATION_POINTS
                )
                route_index = 0
                print(f"[INFO] Itinéraire calculé : {len(current_route)} points\n")
            
            # Récupérer le prochain point du chemin
            current_lat, current_lon = current_route[route_index]
            route_index += 1
            
            # Envoi de la position
            send_taxi_position(producer, TAXI_ID, current_lat, current_lon)
            
            # Vérifier si on est arrivé à destination
            if route_index >= len(current_route):
                print(f"[INFO] ✅ Arrivé à destination : {POI_LIST[current_destination_index][2]}")
            
            # Attente d'1 seconde avant le prochain envoi
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Arrêt demandé par l'utilisateur (Ctrl+C)")
        print("[INFO] Fermeture du producer...")
        
    finally:
        # Fermeture propre du producer
        if producer:
            producer.flush()  # S'assurer que tous les messages sont envoyés
            producer.close()
            print("[INFO] Producer fermé proprement.")
        print("\n[INFO] Au revoir ! 👋")


if __name__ == "__main__":
    main()
