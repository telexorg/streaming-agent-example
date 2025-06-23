import a2a.types as a2a_types
from uuid import uuid4 as uuid

def build_agent_message_from_line(line: str) -> a2a_types.Message:
    return a2a_types.SendStreamingMessageSuccessResponse(
        result=a2a_types.Message(
            messageId=uuid().hex,
            parts=[a2a_types.TextPart(text=line.strip())],
            role="agent",
        )
    )
