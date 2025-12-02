"""
Consumer Kafka pour afficher les positions GPS d'un taxi en temps réel
sur une carte interactive avec Streamlit et Folium.
"""

import json
import time
import sys

# Vérification de l'importation des modules requis
try:
    import streamlit as st
except ImportError:
    print("❌ ERREUR : Module 'streamlit' non trouvé")
    print("💡 Installez-le avec : pip install streamlit")
    sys.exit(1)

try:
    from kafka import KafkaConsumer
    from kafka.errors import KafkaError
except ImportError:
    st.error("❌ ERREUR : Module 'kafka' non trouvé")
    st.info("💡 Installez les dépendances avec : pip install -r requirements.txt")
    st.stop()

try:
    import folium
    from streamlit_folium import st_folium
except ImportError:
    st.error("❌ ERREUR : Modules 'folium' ou 'streamlit-folium' non trouvés")
    st.info("💡 Installez-les avec : pip install folium streamlit-folium")
    st.stop()

try:
    import pandas as pd
    import plotly.express as px
except ImportError:
    st.error("❌ ERREUR : Modules 'pandas' ou 'plotly' non trouvés")
    st.info("💡 Installez-les avec : pip install pandas plotly")
    st.stop()

# Configuration Kafka
BOOTSTRAP_SERVERS = ["localhost:9092"]
TOPIC = "taxi_positions"

# Configuration par défaut
DEFAULT_LAT = 48.8566  # Paris (Notre-Dame)
DEFAULT_LON = 2.3522
AUTO_REFRESH_INTERVAL = 2  # Intervalle de rafraîchissement automatique en secondes (mode auto)


def create_consumer():
    """Crée et retourne un consumer Kafka."""
    try:
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: int(k.decode('utf-8')) if k else None,
            auto_offset_reset='latest',  # Commence à lire les nouveaux messages
            enable_auto_commit=True,
            consumer_timeout_ms=1000  # Timeout pour ne pas bloquer indéfiniment
        )
        return consumer
    except Exception as e:
        st.error(f"❌ Erreur lors de la création du consumer Kafka : {e}")
        st.warning("💡 **Solutions possibles :**")
        st.markdown("""
        1. **Vérifiez que Kafka est démarré** :
           - Zookeeper (si nécessaire)
           - Broker Kafka sur localhost:9092
        
        2. **Démarrez Kafka** dans un terminal séparé :
           ```
           cd C:\\kafka
           .\\bin\\windows\\kafka-server-start.bat .\\config\\server.properties
           ```
        
        3. **Créez le topic** si nécessaire :
           ```
           .\\bin\\windows\\kafka-topics.bat --create --topic taxi_positions
           --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
           ```
        """)
        return None


def create_map(lat, lon, taxi_id):
    """
    Crée une carte Folium centrée sur la position du taxi.
    Ajoute un marqueur représentant le taxi.
    """
    # Création de la carte centrée sur la position
    m = folium.Map(
        location=[lat, lon],
        zoom_start=15,
        tiles='OpenStreetMap'
    )
    
    # Ajout d'un marqueur pour le taxi
    folium.Marker(
        [lat, lon],
        popup=f'Taxi #{taxi_id}',
        tooltip=f'Taxi #{taxi_id} - Position actuelle',
        icon=folium.Icon(color='red', icon='car', prefix='fa')
    ).add_to(m)
    
    return m


def poll_kafka_messages(consumer, max_messages=1):
    """
    Lit jusqu'à max_messages depuis Kafka.
    Retourne la dernière position reçue ou None.
    """
    if consumer is None:
        return None
    
    last_position = None
    
    try:
        # Consommer les messages disponibles (non bloquant grâce au timeout)
        messages = consumer.poll(timeout_ms=500)
        
        for topic_partition, message_list in messages.items():
            for message in message_list:
                last_position = message.value
                # Afficher dans la console pour le debug
                if last_position:
                    print(f"[CONSUMER] Message reçu : id={last_position.get('id')}, "
                          f"lat={last_position.get('lat')}, lon={last_position.get('lon')}")
        
    except KafkaError as e:
        st.error(f"❌ Erreur Kafka : {e}")
    except Exception as e:
        st.error(f"❌ Erreur inattendue : {e}")
    
    return last_position


def main():
    """Fonction principale de l'application Streamlit."""
    
    # Configuration de la page
    st.set_page_config(
        page_title="Suivi Taxi en Temps Réel",
        page_icon="🚕",
        layout="wide"
    )
    
    # Titre principal
    st.title("📍 Suivi Taxi en Temps Réel — Kafka")
    
    # Description
    st.markdown("""
    Cette application consomme les positions GPS d'un taxi envoyées via Kafka
    et les affiche en temps réel sur une carte interactive.
    
    **Flux de données :**
    - 🚕 **Producer** → Envoie les positions GPS du taxi à Kafka
    - 📨 **Kafka** → Transporte les messages
    - 🗺️ **Cette application** → Consomme et affiche sur la carte
    """)
    
    st.divider()
    
    # Initialisation de l'état de session
    if 'last_position' not in st.session_state:
        st.session_state.last_position = {
            'id': 1,
            'lat': DEFAULT_LAT,
            'lon': DEFAULT_LON,
            'timestamp': time.time()
        }
    
    if 'consumer' not in st.session_state:
        st.session_state.consumer = create_consumer()
    
    if 'message_count' not in st.session_state:
        st.session_state.message_count = 0
    
    if 'refresh_mode' not in st.session_state:
        st.session_state.refresh_mode = 'auto'  # 'auto' ou 'manual'

    # Historique des positions pour le tableau et les graphiques
    if 'positions_history' not in st.session_state:
        st.session_state.positions_history = []
    
    # Sélection du mode de rafraîchissement
    st.subheader("⚙️ Mode de rafraîchissement")
    refresh_mode = st.radio(
        "Choisissez le mode de rafraîchissement :",
        options=['auto', 'manual'],
        format_func=lambda x: '🔄 Mode automatique' if x == 'auto' else '👆 Mode manuel',
        horizontal=True,
        index=0 if st.session_state.refresh_mode == 'auto' else 1
    )
    st.session_state.refresh_mode = refresh_mode
    
    st.divider()
    
    # Zone d'affichage de la carte
    st.subheader("🗺️ Carte de suivi en temps réel")
    
    # Bouton de rafraîchissement manuel (uniquement en mode manuel)
    if refresh_mode == 'manual':
        col1, col2 = st.columns([3, 1])
        with col2:
            manual_refresh_button = st.button("🔄 Rafraîchir maintenant", type="primary", use_container_width=True)
    else:
        manual_refresh_button = False
    
    # Récupération de la dernière position depuis Kafka
    # En mode auto : toujours poller à chaque rafraîchissement
    # En mode manuel : poller seulement quand le bouton est cliqué ou au premier chargement
    should_poll = refresh_mode == 'auto' or manual_refresh_button or ('initialized' not in st.session_state)
    
    if should_poll:
        new_position = poll_kafka_messages(st.session_state.consumer)
        
        if new_position:
            # Ajout d'un timestamp si absent pour l'historique
            if 'timestamp' not in new_position:
                new_position['timestamp'] = time.time()

            st.session_state.last_position = new_position
            st.session_state.message_count += 1
            # Ajout de la position à l'historique
            st.session_state.positions_history.append({
                'id': new_position.get('id'),
                'lat': new_position.get('lat'),
                'lon': new_position.get('lon'),
                'destination': new_position.get('destination'),
                'timestamp': new_position.get('timestamp'),
            })
            st.success(f"✅ Nouveau message reçu ! (Total: {st.session_state.message_count})")
    
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
    
    # Affichage de la carte avec la dernière position connue
    last_pos = st.session_state.last_position
    taxi_map = create_map(
        last_pos.get('lat', DEFAULT_LAT),
        last_pos.get('lon', DEFAULT_LON),
        last_pos.get('id', 1)
    )
    
    # Affichage de la carte dans Streamlit
    map_data = st_folium(taxi_map, width=1200, height=500, returned_objects=[])
    
    st.divider()
    
    # Affichage des informations de position
    st.subheader("📍 Dernière position reçue")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="ID Taxi",
            value=last_pos.get('id', 'N/A')
        )
    
    with col2:
        st.metric(
            label="Latitude",
            value=f"{last_pos.get('lat', 0):.6f}"
        )
    
    with col3:
        st.metric(
            label="Longitude",
            value=f"{last_pos.get('lon', 0):.6f}"
        )
    
    # Affichage du timestamp si disponible
    if 'timestamp' in last_pos:
        timestamp = last_pos['timestamp']
        readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        st.caption(f"⏰ Dernière mise à jour : {readable_time}")

    st.divider()

    # Tableau des 10 dernières coordonnées + dashboard temps réel
    st.subheader("📊 Historique des positions et dashboard temps réel")

    col_table, col_charts = st.columns([1.2, 2])

    # Préparation des données d'historique
    history = st.session_state.positions_history

    with col_table:
        st.markdown("**10 dernières coordonnées reçues**")
        if history:
            last_10 = history[-10:]
            df_last_10 = pd.DataFrame(last_10)
            # Formatage du timestamp pour l'affichage
            if 'timestamp' in df_last_10.columns:
                df_last_10['timestamp'] = pd.to_datetime(df_last_10['timestamp'], unit='s')
                df_last_10.rename(columns={
                    'id': 'Taxi ID',
                    'lat': 'Latitude',
                    'lon': 'Longitude',
                    'destination': 'Destination',
                    'timestamp': 'Heure'
                }, inplace=True)
            st.dataframe(df_last_10, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune donnée d'historique pour le moment. En attente de messages Kafka...")

    with col_charts:
        st.markdown("**Variation en temps réel de la latitude et de la longitude**")
        if history:
            last_50 = history[-50:]
            df_last_50 = pd.DataFrame(last_50)

            # Assurer une colonne temps correctement horodatée
            if 'timestamp' in df_last_50.columns:
                df_last_50['time'] = pd.to_datetime(df_last_50['timestamp'], unit='s')
            else:
                # Fallback : index comme axe X
                df_last_50['time'] = range(len(df_last_50))

            # Graphique latitude
            fig_lat = px.line(
                df_last_50,
                x='time',
                y='lat',
                title="Latitude (50 dernières valeurs)"
            )
            fig_lat.update_layout(
                xaxis_title="Temps",
                yaxis_title="Latitude",
                margin=dict(l=10, r=10, t=40, b=10),
                height=250,
            )

            # Graphique longitude
            fig_lon = px.line(
                df_last_50,
                x='time',
                y='lon',
                title="Longitude (50 dernières valeurs)"
            )
            fig_lon.update_layout(
                xaxis_title="Temps",
                yaxis_title="Longitude",
                margin=dict(l=10, r=10, t=40, b=10),
                height=250,
            )

            st.plotly_chart(fig_lat, use_container_width=True)
            st.plotly_chart(fig_lon, use_container_width=True)
        else:
            st.info("Les graphiques apparaîtront dès réception des premières positions.")
    
    # Instructions dans la sidebar
    with st.sidebar:
        st.header("ℹ️ Instructions")
        st.markdown("""
        ### Pour utiliser cette application :
        
        1. **Assurez-vous que Kafka est démarré**
           - Zookeeper (si nécessaire)
           - Broker Kafka
           - Topic `taxi_positions` créé
        
        2. **Lancez le producer** dans un terminal séparé :
           ```bash
           python producer/producer.py
           ```
        
        3. **Mode Auto** : La page se rafraîchit automatiquement
           - Les nouvelles positions apparaîtront sur la carte
           - Le marqueur se déplacera en temps réel
        
        4. **Mode Manuel** : Cliquez sur "Rafraîchir maintenant"
           - Mise à jour uniquement à la demande
        
        ### Statistiques :
        - **Messages reçus :** {count}
        - **Mode actuel :** {mode}
        """.format(
            count=st.session_state.message_count,
            mode='Automatique' if refresh_mode == 'auto' else 'Manuel'
        ))
        
        if st.button("🛑 Réinitialiser le consumer"):
            if st.session_state.consumer:
                st.session_state.consumer.close()
            st.session_state.consumer = create_consumer()
            st.session_state.message_count = 0
            st.rerun()
    
    # Rafraîchissement automatique uniquement en mode auto
    if refresh_mode == 'auto':
        time.sleep(AUTO_REFRESH_INTERVAL)
        st.rerun()


if __name__ == "__main__":
    main()

