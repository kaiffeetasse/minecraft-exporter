import logging
import os

from main import CACHE_DIR, EXPORT_INTERVAL_SECONDS

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def get_player_count(server):
    try:
        server_status = server.status()
        return server_status.players.online
    except Exception as e:
        logger.exception(e)
        return 0


def get_online_players(server):
    try:
        return server.query().players.names
    except Exception as e:
        logger.exception(e)
        return []


def get_server_latency(server):
    try:
        server_status = server.status()
        return server_status.latency
    except Exception as e:
        logger.exception(e)
        return 0


def create_player_file(player_name):
    player_file_path = CACHE_DIR + player_name

    logger.info("File " + player_file_path + " does not exists, creating now")

    f = open(player_file_path, "a")
    f.write(str(0))
    f.close()


def read_player_minutes(player_name):
    player_file_path = CACHE_DIR + player_name

    f = open(player_file_path, "r")
    player_minutes = f.read()
    f.close()

    return player_minutes


def add_player_minutes(player_name):
    player_file_path = CACHE_DIR + player_name

    if not os.path.isfile(player_file_path):
        create_player_file(player_name)

    player_minutes = read_player_minutes(player_name)

    logger.info("player minutes: " + player_minutes)
    logger.info("Adding " + str(EXPORT_INTERVAL_SECONDS / 60) + " minute(s) to playertime to " + player_name)

    f = open(CACHE_DIR + player_name, "w")
    f.write(str(float(player_minutes) + EXPORT_INTERVAL_SECONDS / 60))
    f.close()
