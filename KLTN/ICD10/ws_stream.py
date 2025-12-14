import asyncio
from channels.layers import get_channel_layer

async def stream_to_ws(session_id, text):
    channel_layer = get_channel_layer()

    CHUNK = 1
    for i in range(0, len(text), CHUNK):
        await channel_layer.group_send(
            f"chat_session_{session_id}",
            {
                "type": "ai_stream_event",
                "chunk": text[i:i+CHUNK],
                "done": False
            }
        )
        await asyncio.sleep(0.02)

    # Gửi done cuối
    await channel_layer.group_send(
        f"chat_session_{session_id}",
        {
            "type": "ai_stream_event",
            "chunk": "",
            "done": True
        }
    )
