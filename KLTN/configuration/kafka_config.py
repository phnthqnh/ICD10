import logging
from utils.utils import Utils

logger = logging.getLogger(__name__)


class KafkaConfig:
    @staticmethod
    def get_producer_config():
        config = {
            "bootstrap.servers": Utils.get_setting("KAFKA_BOOTSTRAP_SERVERS"),
            "message.max.bytes": Utils.get_setting(
                "KAFKA_MESSAGE_MAX_BYTES", 10_000_000, int
            ),
            "max.in.flight.requests.per.connection": 1,
            "compression.type": Utils.get_setting("KAFKA_COMPRESSION_TYPE", "gzip"),
            "enable.idempotence": True,
            "linger.ms": Utils.get_setting("KAFKA_LINGER_MS", 5),
            "batch.size": Utils.get_setting("KAFKA_BATCH_SIZE", 16_384, int),
            "queue.buffering.max.messages": Utils.get_setting(
                "KAFKA_QUEUE_BUFFERING_MAX_MESSAGES", 100_000, int
            ),
            "acks": Utils.get_setting("KAFKA_ACKS", "all"),
            "retries": Utils.get_setting("KAFKA_RETRIES", 10, int),
            "retry.backoff.ms": Utils.get_setting("KAFKA_RETRY_BACKOFF_MS", 300, int),
            "socket.keepalive.enable": True,
            "message.timeout.ms": 30_000,
        }
        logger.debug(f"KAFKA PRODUCER CONFIG: {config}")
        return config

    @staticmethod
    def get_consumer_config(group_id):
        if not group_id:
            logger.error("group_id is required for Kafka consumer")
            return

        config = {
            "bootstrap.servers": Utils.get_setting("KAFKA_BOOTSTRAP_SERVERS"),
            "group.id": group_id,
            "auto.offset.reset": Utils.get_setting("KAFKA_AUTO_OFFSET_RESET"),
            "enable.auto.commit": False,
            "max.poll.interval.ms": Utils.get_setting(
                "KAFKA_MAX_POLL_INTERVAL_MS", 300_000
            ),
            "session.timeout.ms": Utils.get_setting(
                "KAFKA_SESSION_TIMEOUT_MS", 10_000, int
            ),
            "heartbeat.interval.ms": Utils.get_setting(
                "KAFKA_HEARTBEAT_INTERVAL_MS", 3_000, int
            ),
            "max.partition.fetch.bytes": Utils.get_setting(
                "KAFKA_MAX_PARTITION_FETCH_BYTES", 1_048_576, int
            ),
            "fetch.max.bytes": Utils.get_setting(
                "KAFKA_FETCH_MAX_BYTES", 50_000_000, int
            ),
            "fetch.wait.max.ms": Utils.get_setting("KAFKA_FETCH_WAIT_MAX_MS", 500, int),
            "isolation.level": "read_committed",
            "partition.assignment.strategy": "roundrobin",
        }
        logger.debug(f"KAFKA CONSUMER CONFIG: {config}")
        return config
