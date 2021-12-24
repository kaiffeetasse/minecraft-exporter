import time
from dotenv import load_dotenv
from prometheus_client import Gauge, start_http_server
import os
import logging
from mcstatus import MinecraftServer
import minecraft_service

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

EXPORT_INTERVAL_SECONDS = int(os.environ.get("EXPORT_INTERVAL_SECONDS"))
ERROR_SLEEP_SECONDS = 60
CACHE_DIR = "cache/"
SERVER_HOST = os.environ.get("SERVER_HOST")
SERVER_PORT = os.environ.get("SERVER_PORT")


def init_cache():
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)


def export_metrics():
    players_online_count_gauge = Gauge("minecraft_players_online_count", "Players online count")
    players_online_time_gauge = Gauge("minecraft_players_online_time", "Players online time", ['player_name'])
    server_latency_gauge = Gauge("minecraft_server_latency", "Server latency")

    start_http_server(8255)

    while True:
        try:
            server_latency_gauge.set(minecraft_service.get_server_latency(server))
            players_online_count_gauge.set(minecraft_service.get_player_count(server))

            online_player_names = minecraft_service.get_online_players(server)

            for player_name in online_player_names:
                minecraft_service.add_player_minutes(player_name)

            for root, dirs, files in os.walk(CACHE_DIR):
                for file in files:
                    player_name = file
                    player_minutes = minecraft_service.read_player_minutes(player_name)

                    players_online_time_gauge.labels(player_name=player_name).set(player_minutes)

        except Exception as e:
            logger.error("Error while getting server stats:")
            logger.exception(e)

        time.sleep(ERROR_SLEEP_SECONDS)


if __name__ == '__main__':
    server = MinecraftServer.lookup(SERVER_HOST + ":" + SERVER_PORT)

    init_cache()

    export_metrics()
