import os
import a2a.types as a2a_types
from utils.random_name_genertor import RandomNameRepository

agent_name_suffix = (
    "_" + os.getenv("APP_ENV") + "_" + RandomNameRepository.generate_suffix()
    if os.getenv("APP_ENV") == "local"
    else ""
)

def get_card(base_url):
    card = a2a_types.AgentCard(
        name=f"Streaming Agent{agent_name_suffix}",
        description="An agent that streams popular text content like the Bible, Romeo and Juliet, and The Art of War",
        url=f"{base_url}",
        provider=a2a_types.AgentProvider(
            organization="Telex",
            url="telex.im",
        ),
        version="1.0.0",
        documentationUrl=f"{base_url}/docs",
        capabilities=a2a_types.AgentCapabilities(
            streaming=True,
            pushNotifications=False,
            stateTransitionHistory=True,
        ),
        authentication=a2a_types.AgentAuthentication(schemes=["Bearer"]),
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
        skills=[
            a2a_types.AgentSkill(
                id="stream_bible",
                name="Stream bible",
                description="Streams the bible",
                tags=["bible"],
                examples=["In the beginning was the word, and the word was with God, and the word was God"],
                inputModes=["text/plain"],
                outputModes=["text/plain"],
            ),
            a2a_types.AgentSkill(
                id="stream_art_of_war",
                name="Stream Art of War",
                description="Streams the Art of War",
                tags=["art_of_war"],
                examples=["The art of war is of vital importance to the State."],
                inputModes=["text/plain"],
                outputModes=["text/plain"],
            ),
            a2a_types.AgentSkill(
                id="stream_romeo_and_juliet",
                name="Stream Romeo and Juliet",
                description="Streams Romeo and Juliet",
                tags=["romeo_and_juliet"],
                examples=["Two households, both alike in dignity, from ancient grudge break to new mutiny"],
                inputModes=["text/plain"],
                outputModes=["text/plain"],
            )
        ],
    )

    return card
