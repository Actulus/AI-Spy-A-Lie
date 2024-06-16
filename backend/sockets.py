import random
import numpy as np
import socketio
import uuid
import logging
import asyncio
from q_learning_agent import QLearningAgent
from mcts_agent import MCTSAgent
from sarsa_agent import SARSAAgent
from dqn_agent import DQNAgent
from load_agents import load_agents
from liars_dice_game_logic import LiarDiceGame
import sys
import os

game_counter = 0
SAVE_INTERVAL = 10 

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load the agents
easy_agent, medium_agent, hard_agent = load_agents(
    easy_filename="q_learning_agent.pkl",
    medium_filename="dqn_agent.pkl",
    hard_filename="sarsa_agent.pkl",
)

# Initialize the models dictionary
models = {
    "tutorial": None,
    "easy": easy_agent,
    "medium": medium_agent,
    "hard": hard_agent,
}

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

socketio_server = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])

socketio_app = socketio.ASGIApp(socketio_server=socketio_server, socketio_path="/")

rooms = {}  # Dictionary to keep track of rooms and their connections
games = {}  # Dictionary to keep track of games and their states


def generate_room_name(difficulty):
    return f"{difficulty}_{uuid.uuid4()}"


@socketio_server.event
async def connect(sid, environ):
    query_params = environ.get("QUERY_STRING", "")
    if query_params:
        params = dict(qc.split("=") for qc in query_params.split("&"))
        difficulty = params.get("room", "default_room")
        room = generate_room_name(difficulty)
    else:
        room = generate_room_name("default_room")

    rooms[room] = {sid}
    games[room] = LiarDiceGame()

    await socketio_server.enter_room(sid, room)
    logger.info(f"{sid}: connected to {room}")
    await socketio_server.emit("join", {"sid": sid}, room=room)

    # Emit the initial game state to the user
    game_state = games[room].get_game_state()
    await socketio_server.emit("game_update", game_state, room=room)

    # Simulate AI connection
    asyncio.create_task(simulate_ai_connection(room))


@socketio_server.event
async def player_names(sid, data):
    room = None
    for r, sids in rooms.items():
        if sid in sids:
            room = r
            break

    if room:
        user_name = data["userName"]
        ai_name = data["aiName"]
        games[room].set_player_names(user_name, ai_name)
        logger.info(f"Player names received in {room}: {user_name}, {ai_name}")
        # Update game state with player names
        game_state = games[room].get_game_state()
        await socketio_server.emit("game_update", game_state, room=room)


@socketio_server.event
async def chat(sid, message):
    room = None
    for r, sids in rooms.items():
        if sid in sids:
            room = r
            break

    if room:
        logger.info(f"Message from {sid} in {room}: {message}")
        game = games[room]
        response_message = None
        user_message = None

        # If the message is from the user, let the AI respond
        if not sid.startswith("ai_"):
            # Handle player move
            if message.startswith("bid"):
                _, quantity, face_value = message.split()
                quantity = int(quantity)
                face_value = int(face_value)
                success = game.make_bid(
                    1, quantity, face_value
                )  # player 1 is the user

                if success:
                    user_message = f"Bid: {quantity} {face_value}s."
                    response_message = "Bid successful."
                else:
                    user_message = "Invalid bid."
                    response_message = "Invalid bid."

            elif message == "challenge":
                result = game.challenge(1)
                user_message = "Challenge!"
                response_message = result

            # Send the user message only to the user
            if user_message:
                await socketio_server.emit(
                    "chat", {"sid": sid, "message": user_message}, room=sid
                )
                if message == "challenge":
                    await asyncio.sleep(0.5)
                    await socketio_server.emit(
                        "chat", {"sid": sid, "message": response_message}, room=room
                    )

            # Send game state update to all users
            game_state = game.get_game_state()
            await socketio_server.emit("game_update", game_state, room=room)

            # Check game over condition after player move
            if game.is_game_over():
                winner = game.get_winner()
                await socketio_server.emit(
                    "game_over", {"winner": game.player_names[winner]}, room=room
                )
                increment_game_counter()
                return
            else:
                ai_sid = f"ai_{room}"
                if game.is_game_over():
                    winner = game.get_winner()
                    await socketio_server.emit(
                        "chat",
                        {"sid": ai_sid, "message": f"Game over! Player {winner} wins!"},
                        room=room,
                    )
                    increment_game_counter()
                    return
                else:
                    await asyncio.sleep(0.5)  # Adding delay before AI response
                    ai_message = generate_ai_response(game, room)
                    await socketio_server.emit(
                        "chat", {"sid": ai_sid, "message": ai_message}, room=room
                    )
                    # Send updated game state after AI move
                    game_state = game.get_game_state()
                    await socketio_server.emit("game_update", game_state, room=room)
                    if game.is_game_over():
                        winner = game.get_winner()
                        await socketio_server.emit(
                            "game_over",
                            {"winner": game.player_names[winner]},
                            room=room,
                        )
                        increment_game_counter()
                        return


@socketio_server.event
async def disconnect(sid):
    room = None
    for r, sids in rooms.items():
        if sid in sids:
            sids.remove(sid)
            room = r
            if not sids:  # If the room is empty, remove it from the dictionary
                del rooms[room]
                del games[room]
            break

    if room:
        logger.info(f"{sid}: disconnected from {room}")


def save_agents():
    models["easy"].save("q_learning_agent.pkl")
    models["medium"].save("dqn_agent.pkl")
    models["hard"].save("dqn_agent.pkl")
    logging.info("Agents saved.")


def increment_game_counter():
    global game_counter
    game_counter += 1
    if game_counter % SAVE_INTERVAL == 0:
        save_agents()


async def simulate_ai_connection(room):
    ai_sid = f"ai_{room}"
    rooms[room].add(ai_sid)
    logger.info(f"AI {ai_sid}: connected to {room}")
    await socketio_server.emit("join", {"sid": ai_sid}, room=room)
    await socketio_server.emit(
        "chat", {"sid": ai_sid, "message": "Hi there!"}, room=room
    )


def get_ai_model(difficulty):
    return models.get(
        difficulty, models["tutorial"]
    )  # Default to tutorial if difficulty not found


def generate_ai_response(game, room):
    difficulty = room.split('_')[0]  # Extract difficulty from room name
    model = models.get(difficulty, models['tutorial'])  # Default to tutorial if difficulty not found

    if difficulty == 'tutorial':
        return handle_tutorial_mode(game)

    if game.is_game_over():
        winner = game.get_winner()
        return f"Game over! {game.player_names[winner]} wins!"

    state = game.get_game_state()
    logging.info(f"Current game state: {state}")

    if isinstance(model, QLearningAgent):
        action = model.get_action(state)
    elif isinstance(model, DQNAgent):
        state_sequence = (
            tuple(state["dice_count"]) + 
            tuple(state["current_bid"]) + 
            tuple(state["scores"]) + 
            (state["current_player"],)
        )
        action = model.act(state_sequence)
        logging.info(f"DQNAgent raw action: {action}")
    elif isinstance(model, SARSAAgent):
        action = model.get_action(state)
        logging.info(f"SARSAAgent raw action: {action}")
    elif isinstance(model, MCTSAgent):
        action = model.select_action(state, game)
        logging.info(f"MCTSAgent raw action: {action}")
    else:
        logging.error(f"Invalid model type: {type(model)}")
        return "Invalid AI model type"

    action_type, quantity, face_value = decode_action(action)
    logging.info(f"{type(model).__name__} action: {action} (Type: {action_type}, Quantity: {quantity}, Face Value: {face_value})")

    # Validate and reselect action if invalid
    attempts = 0
    while not is_valid_action(action_type, quantity, face_value, state) and attempts < 10:
        action = model.get_valid_random_action(state)
        action_type, quantity, face_value = decode_action(action)
        logging.info(f"Reselected action: {action} (Type: {action_type}, Quantity: {quantity}, Face Value: {face_value})")
        attempts += 1

    if not is_valid_action(action_type, quantity, face_value, state):
        logging.error(f"Unable to find valid action after {attempts} attempts.")
        return "Invalid action"

    logging.info(f"Final action: {action} (Type: {action_type}, Quantity: {quantity}, Face Value: {face_value})")

    if action_type == 0:  # Bid
        valid_bid = game.make_bid(2, quantity, face_value)
        if valid_bid:
            logging.info(f"Valid bid made: {quantity} {face_value}s.")
            return f"Bid: {quantity} {face_value}s."
        else:
            logging.error(f"Invalid bid action: {action}")
            return "Invalid action"
    elif action_type == 1:  # Challenge
        result = game.challenge(2)
        if game.is_game_over():
            winner = game.get_winner()
            logging.info(f"Game over! {game.player_names[winner]} wins!")
            return f"Game over! {game.player_names[winner]} wins!"
        logging.info(f"Challenge result: {result}")
        return f"Challenge! {result}"


def decode_action(action):
    if isinstance(action, tuple):
        return action
    else:
        action_type = action // 66
        quantity = (action % 66) // 6 + 1
        face_value = action % 6 + 1
        return action_type, quantity, face_value

def is_valid_action(action_type, quantity, face_value, state):
    current_quantity, current_face_value = state["current_bid"]
    total_dice = sum(state["dice_count"])

    if action_type == 0:  # Bid
        if quantity > total_dice or quantity < 1:
            return False
        if face_value < 1 or face_value > 6:
            return False
        if quantity < current_quantity or (
            quantity == current_quantity and face_value <= current_face_value
        ):
            return False
    elif action_type == 1:  # Challenge
        if state["last_action_was_challenge"]:
            return False
    return True


def handle_tutorial_mode(game):
    if game.is_game_over():
        winner = game.get_winner()
        return f"Game over! {game.player_names[winner]} wins!"

    if game.last_action_was_challenge or game.current_bid == (1, 1):
        action = "bid"  # Force bid after challenge or for the first move
    else:
        action = random.choice(["bid", "challenge"])

    # if current bid is 10 6s, challenge
    if game.current_bid[0] == 10:
        action = "challenge"

    if action == "bid":
        quantity, face_value = game.random_bid()
        game.make_bid(2, quantity, face_value)  # player 2 is the AI
        return f"Bid: {quantity} {face_value}s."
    else:
        result = game.challenge(2)

        if game.is_game_over():
            winner = game.get_winner()
            return f"Game over! {game.player_names[winner]} wins!"

        return f"Challenge! {result}"