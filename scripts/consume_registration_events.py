import logging

import pika

from app.core.config import settings
from app.core.messaging import REGISTRATION_EVENTS_QUEUE
from app.modules.registrations.events import handle_registration_event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def consume_registration_events() -> None:
    connection = pika.BlockingConnection(
        pika.URLParameters(settings.rabbitmq_url),
    )
    channel = connection.channel()
    channel.queue_declare(queue=REGISTRATION_EVENTS_QUEUE, durable=True)

    def callback(message_channel, method, properties, body: bytes) -> None:
        try:
            handle_registration_event(body)
            message_channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            # Keep the worker alive when a single message cannot be processed.
            logger.exception("failed to process registration event")
            message_channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False,
            )

    channel.basic_consume(
        queue=REGISTRATION_EVENTS_QUEUE,
        on_message_callback=callback,
    )

    logger.info("waiting for registration events")
    channel.start_consuming()


if __name__ == "__main__":
    consume_registration_events()