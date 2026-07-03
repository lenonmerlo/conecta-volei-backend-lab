import json
from typing import Any

import pika

from app.core.config import settings

REGISTRATION_EVENTS_QUEUE = "registration_events"

def publish_message(
        queue_name: str,
        message: dict[str, Any],
) -> None:
    connection = pika.BlockingConnection(
        pika.URLParameters(settings.rabbitmq_url),
    )

    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )
    finally:
        connection.close()

def publish_registration_joined_event(
        *,
        registration_id: str,
        game_id: str,
        player_id: str,
        slot: str,
) -> None:
    publish_message(
        REGISTRATION_EVENTS_QUEUE,
        {
            "event": "registration.joined",
            "registration_id": registration_id,
            "game_id": game_id,
            "player_id": player_id,
            "slot": slot,
        },
    )