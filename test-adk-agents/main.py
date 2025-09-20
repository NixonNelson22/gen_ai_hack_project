import asyncio

# Import the main customer service agent
from ai_agent.agent import root_agent
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from utils import add_user_query_to_history, call_agent_async

load_dotenv()

# --- Initialize in-memory session service ---
session_service = InMemorySessionService()

# --- define initial state ---
initial_state = {
    
}


async def main_async():
    APP_NAME = "cement_quality_assistant"
    USER_ID = "test_user"

    # --- session creation ---
    new_session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )

    SESSION_ID = new_session.id

    # --- agent runner setup ---
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # --- conversation loop ---
    print("Welcome to the Cement Quality Assistant!")
    print("Type 'exit' to end the session.")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Ending session. Goodbye!")
            break

        # update interaction history
        add_user_query_to_history(
            session_service, APP_NAME, USER_ID, SESSION_ID, user_input 
        )

        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

    final_session = session_service.get_session(
        APP_NAME, USER_ID, SESSION_ID
    )

    print("Final session state:")
    for key, value in final_session.state.items():
        print(f"{key}: {value}")

def main():
    """
    Entry point for the asynchronous main function.
    """
    asyncio.run(main_async())

if __name__ == "__main__":
    main()