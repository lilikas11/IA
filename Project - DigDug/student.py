"""Example client."""
import asyncio
import getpass
import json
import logging
import os
from mapa import Map

#adicionados para o agente
from solver import SOLVER
from consts import Direction

# Next 4 lines are not needed for AI agents, please remove them from your code!
#import pygame
import websockets


#def agent(state):


#pygame.init()
#program_icon = pygame.image.load("data/icon2.png")
#pygame.display.set_icon(program_icon)


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        # Receive information about static game properties

        # Next 3 lines are not needed for AI agent
        #SCREEN = pygame.display.set_mode((299, 123))
        #SPRITES = pygame.image.load("data/pad.png").convert_alpha()
        #SCREEN.blit(SPRITES, (0, 0))

        #adicionado para o agente:
        digdug_dir = Direction.SOUTH
        stochastic_charger = 0
        last_key = ''
        key=''	
        state = json.loads(
            await websocket.recv()
        )  # O PRIMEIRO TEM O MAPA
        mapa = Map(size=state["size"], mapa=state["map"])
        solver = SOLVER(state, digdug_dir, mapa)
        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server
##################################################### o que é preciso fazer, é só daqui até lá abaixo
                #Notas: o state é o dicio que contém toda a informação que precisamos para o agente inteligente usar. O state é o que a função assíncrona next_frame(self) de game.py retorna.
                #a chave "digdug" contém um par da posição do DigDug, e a chave "enemies" contém uma lista de dicionários da informação de cada inimigo {"name": str(e), "id": str(e.id), "pos": e.pos, "dir": e.lastdir}
                if ('map' in state):
                    mapa = Map(size=state["size"], mapa=state["map"])
                    solver.mapa = mapa
                else:
                    solver.state = state
                    key, digdug_dir = solver.run()


                
               # if key== "A" and last_key!= 'A':
               #     stochastic_charger=0
               # stochastic_charger += 1
               # if stochastic_charger >= 16:
               #     key, digdug_dir = agent_random_move(state, digdug_dir)
               #     #print("random move: ", key)
               #     stochastic_charger=0
#
               # last_key = key
                


                await websocket.send(
                        json.dumps({"cmd": "key", "key": key})
                    )  # send key command to server - you must implement this send in the AI agent
                

################################################## o que é preciso fazer, é só daqui até lá cima

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

            # Next line is not needed for AI agent
            #pygame.display.flip()


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))