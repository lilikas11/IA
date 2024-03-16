import math
from consts import Direction, Tiles, MAX_LEN_ROPE
import heapq


def find_closest_enemy(state):
    if "digdug" in state:
        digdug_pos = state["digdug"]
        enemies_above_y3 = []
        enemies_below_y3 = []

        # Dividir inimigos em dois grupos com base na posição y
        for enemy in state.get("enemies", []):
            if enemy["pos"][1] >= 3:
                enemies_above_y3.append(enemy)
            else:
                enemies_below_y3.append(enemy)

        # Primeiro tentar encontrar inimigo acima de y = 3
        closest_enemy = get_prioritized_enemy(digdug_pos, enemies_above_y3, "Pooka")

        # Se não houver inimigo acima de y = 3, procurar abaixo
        if not closest_enemy:
            closest_enemy = get_prioritized_enemy(digdug_pos, enemies_below_y3, "Pooka")

        return closest_enemy

    return None

def get_prioritized_enemy(digdug_pos, enemies, priority_type):
    closest_enemy = None
    closest_distance = float('inf')
    backup_enemy = None
    backup_distance = float('inf')

    for enemy in enemies:
        distance = math.dist(digdug_pos, enemy["pos"])
        if enemy["name"] == priority_type and distance < closest_distance:
            closest_distance = distance
            closest_enemy = enemy
        elif distance < backup_distance:
            backup_distance = distance
            backup_enemy = enemy

    return closest_enemy if closest_enemy is not None else backup_enemy



def is_valid_position(state, position, rocks):
    rocks = state['rocks']
    x, y = position
    if ((state['digdug'][1]>=3) and not (0 <= x < 48 and 3 <= y < 24)):
        closest_enemy = find_closest_enemy(state)
        if closest_enemy['pos'][1]>=3:
            return False
        
    if not (0 <= x < 48 and 0 <= y < 24):
        return False  # The position is out of bounds

    # Check if the position is not where a rock is or directly under a rock
    for rock_dict in rocks:
        # Convert the position list to a tuple for comparison
        rock_pos = tuple(rock_dict['pos'])
        rock_pos_bellow = (rock_pos[0], rock_pos[1] + 1)
        if (position == rock_pos or position == rock_pos_bellow):
            return False

    return True


def manhattan_distance(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


def get_next_move_key(current_pos, next_pos, mapa, digdug_dir):
    # Se chegar aqui então VAI cavar
    # Calculate the difference between the current and next positions
    dx = next_pos[0] - current_pos[0]
    dy = next_pos[1] - current_pos[1]

    # Map the difference to a movement key
    key = ''
    dir = digdug_dir
    if dx == 1 and dy == 0:
        key = 'd'  # Move right
        dir = Direction.EAST
    elif dx == -1 and dy == 0:
        key = 'a'  # Move left
        dir = Direction.WEST
    elif dx == 0 and dy == 1:
        key = 's'  # Move down
        dir = Direction.SOUTH
    elif dx == 0 and dy == -1:
        key = 'w'  # Move up
        dir = Direction.NORTH


    mapa.map[next_pos[0]][next_pos[1]] = 0
    return key, dir  # If there's no movement or an invalid move, return an empty string


def calculate_goal(state, mapa, closest_enemy):
    # first Passage title (vert-align-left, hor-align-up) in the closest_enemy_pos:
    enemy_x, enemy_y = closest_enemy['pos']

    map_x, map_y = mapa._size

    passage = [(enemy_x, enemy_y)]
    passage_direction = None
    distance_from_enemie = 8

    # checkar os tiles acima, abaixo, esquerda e direita do inimigo
    # if tile == passage append to passage
    # else break


    # só ve se tem uma passagem vertical se nao tiver uma horizontal
    for dy in range(-1, -enemy_y, -1):
        if len(passage) > distance_from_enemie:
            break
        x, y = enemy_x, enemy_y + dy

        if mapa.get_tile([x, y]) == Tiles.PASSAGE:
            passage_direction = 'Vertical'
            passage.append((x, y))
        else:
            break

    for dy in range(1, map_y-enemy_y):
        if len(passage) > distance_from_enemie:
            break
        x, y = enemy_x, enemy_y + dy

        if mapa.get_tile([x, y]) == Tiles.PASSAGE:
            passage_direction = 'Vertical'
            passage.append((x, y))
        else:
            break

    if len(passage) == 1:

        for dx in range(-1, -enemy_x, -1):
            if len(passage) > distance_from_enemie:
                break
            x, y = enemy_x + dx, enemy_y

            if mapa.get_tile([x, y]) == Tiles.PASSAGE:
                passage_direction = 'Horizontal'
                passage.append((x, y))
            else:
                break

        for dx in range(1, map_x-enemy_x):
            if len(passage) > distance_from_enemie:
                break
            x, y = enemy_x + dx, enemy_y

            if mapa.get_tile([x, y]) == Tiles.PASSAGE:
                passage_direction = 'Horizontal'
                passage.append((x, y))
            else:
                break
            
    # ver qual dos tiles das pontas em passage está mais perto do digdug e definir como goal
    digdug_pos = state["digdug"]
    min_distance = float('inf')
    closest_option = None

    options = []
    if passage_direction == 'Vertical':
        min_y_pair = min(passage, key=lambda pair: pair[1])
        options.append(min_y_pair)
        max_y_pair = max(passage, key=lambda pair: pair[1])
        options.append(max_y_pair)
    elif passage_direction == 'Horizontal':
        min_x_pair = min(passage, key=lambda pair: pair[0])
        options.append(min_x_pair)
        max_x_pair = max(passage, key=lambda pair: pair[0])
        options.append(max_x_pair)
    else:
        return closest_enemy['pos'],closest_enemy['pos'], None
        
    for tile in options:
        distance = manhattan_distance(digdug_pos, tile)
        if distance < min_distance:
            min_distance = distance
            closest_option = tile
    
    if (closest_enemy['name'] == 'Fygar' and passage_direction == 'Horizontal'):
        # se o fygar estiver numa passagem horizontal o goal é 2 tiles para cima do velho goal (caso 2 tiles a cima passe o range do mapa, o goal é 2 tiles a baixo do velho goal)
        if (closest_option[1] - 1 >= 3):
            options.append((closest_option[0], closest_option[1] - 1))
        if (closest_option[1] + 1 <= map_y-1):
            options.append((closest_option[0], closest_option[1] + 1))

        for tile in options:
            distance = manhattan_distance(digdug_pos, tile)
            if distance < min_distance:
                min_distance = distance
                closest_option = tile

    return closest_option, passage_direction, passage

def get_direction(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2

    dx = x2 - x1
    dy = y2 - y1

    if dy == 0:
        # Movimento maior na horizontal
        if dx > 0:
            return Direction.EAST
        else:
            return Direction.WEST
    else:
        # Movimento maior na vertical
        if dy > 0:
            return Direction.SOUTH
        else:
            return Direction.NORTH


def canShootNow(state, mapa, digdug_dir):
    enemies = state['enemies']
    digdug_pos = state['digdug']
    # lista de posições válidas para atirar em todas as direções até de 3 a 4 tiles de distância
    # 1 tile de distancia entra no safe zone
    # 2 tiles só vale a pena disparar se ele tiver virado para ele (feito no safe zone)
    # 3 tiles dispara sempre
    # 4 tiles só dispara se for uma pooka
    shoot_positions = []

    # Para a direção Oeste
    for dx in range(-2, -4, -1):  # 2 a 4 tiles
        x, y = digdug_pos[0] + dx, digdug_pos[1]

        if x < 1 or y < 1:
            break

        if mapa.get_tile([x, y]) == Tiles.PASSAGE:
            shoot_positions.append((x, y))
        else:
            break

    # Para a direção Leste
    for dx in range(1, 4):
        x, y = digdug_pos[0] + dx, digdug_pos[1]

        if x > mapa._size[0]-1 or y > mapa._size[1]-1:
            break

        if mapa.get_tile([x, y]) == Tiles.PASSAGE:
            shoot_positions.append((x, y))
        else:
            break

    # Para a direção Norte
    for dy in range(-1, -4, -1):
        x, y = digdug_pos[0], digdug_pos[1] + dy

        if x < 1 or y < 1:
            break

        if mapa.get_tile([x, y]) == Tiles.PASSAGE:
            shoot_positions.append((x, y))
        else:
            break

    # Para a direção Sul
    for dy in range(1, 4):
        x, y = digdug_pos[0], digdug_pos[1] + dy
        # ver se x,y não passa do size do mapa
        if x > mapa._size[0]-1 or y > mapa._size[1]-1:
            break

        if mapa.get_tile([x, y]) == Tiles.PASSAGE:
            shoot_positions.append((x, y))
        else:
            break
            

    # Verifica se há algum inimigo em uma posição de tiro válida
    for enemy in enemies:
        
        dx = int(enemy['pos'][0]) - int(digdug_pos[0])
        dy = int(enemy['pos'][1]) - int(digdug_pos[1])
        # if enemy['name'] == 'Fygar' and abs(dx) == 1 and abs(dy) <= 3:
        #     # se estas posições não forem tiles também são posições de tiro
        #     for dx in range(-1, 2):
        #         for dy in range(-3, 4):
        #             x, y = digdug_pos[0] + dx, digdug_pos[1] + dy
        #             if x < 0 or y < 0 or x > mapa._size[0]-1 or y > mapa._size[1]-1:
        #                 continue
        #             if mapa.get_tile([x, y]) == Tiles.PASSAGE:
        #                 shoot_positions.append((x, y))
        #             else:
        #                 break
            

        enemy_pos = tuple(enemy['pos'])
        if enemy_pos in shoot_positions:
            # ver se ele não está virado para outro lado
            dir_shoot = get_direction(digdug_pos, enemy_pos)
            print("dir_shoot", dir_shoot)
            print("digdug_dir", digdug_dir)
            if digdug_dir != dir_shoot:
                return False, None, None
            return True, enemy, 'A'  # Encontrou um inimigo em uma posição válida para atirar

    return False, None, None  # Não encontrou inimigos em posições válidas para atirar


def tile_passage(state, mapa, digdug_pos, enemy_pos, dx):
    rocks = state['rocks']

    if dx>=0:
        for dx in range(0, dx +1 ):
            x, y = enemy_pos[0] - dx, enemy_pos[1]
            if mapa.get_tile([x, y]) == Tiles.STONE:
                return False
    else:
        for dx in range(0, dx -1, -1):
            x, y = enemy_pos[0] - dx, enemy_pos[1]
            if mapa.get_tile([x, y]) == Tiles.STONE:
                return False
            
    return True
        
                   
def safe_pos_enemy(state, mapa, digdug_pos, didug_dir):
    enemies = state['enemies']
    rocks = state['rocks']
    # se estiver mos a fazer uma posição futura temos de atualizar para a dir que ele vai ficar
        
        
    for enemy in enemies:
        enemy_pos = tuple(enemy['pos'])
        dx = int(enemy_pos[0]) - int(digdug_pos[0])
        dy = int(enemy_pos[1]) - int(digdug_pos[1])

        if ( enemy['name'] == 'Fygar' and (
            (abs(dx) == 1 and dy == 0) or
            (abs(dy)==1 and dx==0) or
            (abs(dx)<=4 and dy == 0 and tile_passage(state, mapa, digdug_pos, enemy_pos, dx))
        )
            ): # cara triste como eu :'
            return False
        
        if ( enemy['name'] == 'Pooka' and (
            ((abs(dx) == 1 and dy == 0) or (abs(dy) == 1 and dx == 0) or (dy == 0 and dx == 0))
            #(((dx==2 and dy==0) or (dy == 2 and dy == 0)) and didug_dir != shoot_dir)
            #(('traverse' in enemy) and (abs(dx) + abs(dy) <= 5))
            )
            ):
            return False

    return True


def best_escape_direction(state, mapa, enemy):
    start = tuple(state['digdug'])
    rocks = state['rocks']
    best_score = float('inf')
    best_neighbor = None

     # Verificar a possibilidade de ficar parado
    if is_valid_position(state, start, rocks) and safe_pos_enemy(state, mapa, start, None):
        if enemy['name'] == 'Fygar':
            best_score = 2
        else:
            best_score = 1  # Implemente essa função conforme necessário
        best_neighbor = start
        
    offset = {
        Direction.NORTH: (0, -1),
        Direction.SOUTH: (0, 1),
        Direction.EAST: (1, 0),
        Direction.WEST: (-1, 0),
    }

    for direction in Direction:
        print("direction no best direction", direction)
        dx, dy = offset[direction]
        neighbor = (start[0] + dx, start[1] + dy)

        if not is_valid_position(state, neighbor, rocks):
            print('position not valid:', neighbor)
            continue

        if not safe_pos_enemy(state, mapa, neighbor, direction):
            print('position not safe enemy:', neighbor)
            continue

        # o custo começa como 1
        cost = 1
        
        # se for um tile o cost é + 2
        # isto porque se não fica preso nos fygars
        if enemy['name']== 'Pooka' and mapa.get_tile(neighbor) == Tiles.STONE:
            cost += 2
        
        if enemy['name'] == 'Fygar':
            # andar na horizontal é mais caro
            if direction == Direction.EAST or direction == Direction.WEST:
                cost += 3
                        
        # se for uma pooka o custo de andar na direção contraria é maior
        if enemy['name'] == 'Pooka':
            if direction == Direction.EAST and enemy['dir'] == Direction.EAST:
                cost += 1
            if direction == Direction.WEST and enemy['dir'] == Direction.WEST:
                cost += 1
            if direction == Direction.NORTH and enemy['dir'] == Direction.NORTH:
                cost += 1
            if direction == Direction.SOUTH and enemy['dir'] == Direction.SOUTH:
                cost += 1

        # Aqui você pode implementar outras lógicas para calcular o 'score' de fuga
        # Por exemplo, distância até inimigos, obstáculos, etc.

        if cost < best_score:
            best_score = cost
            best_neighbor = neighbor
    print("best_neighbor", best_neighbor)
    return best_neighbor


def safe_zone(state, mapa, digdug_pos, didug_dir):
    # check if didug is in a safe zone 1 tile away from all enemies
    # não está na safe zone a 1 tile (a não ser que o enimigo seja um fygar e o tile seja uma stone)
    # nao esta na safe zone a 2 tiles se estiver virado na direção contraria que tem de disparar (a não ser que os blocos no meio sejam tiles)
    # não está na safe zone a 3 blocos na horizontal de um fygar
    # não tá safe perto de uma ghosted pooka
    enemies = state['enemies']
    rocks = state['rocks']
    # se estiver mos a fazer uma posição futura temos de atualizar para a dir que ele vai ficar

    
    for enemy in enemies:
        enemy_pos = tuple(enemy['pos'])
        dx = int(enemy_pos[0]) - int(digdug_pos[0])
        dy = int(enemy_pos[1]) - int(digdug_pos[1])

        shoot_dir = get_direction(digdug_pos, enemy_pos)
        

        # if fygar
        # e se os tiles entre o digdug e o fygar forem todos passagem
        if ( enemy['name'] == 'Fygar' and (
            (abs(dx) == 1 and dy == 0) or
            (abs(dy)==1 and dx==0) or
            (abs(dx)<=4 and dy == 0 and tile_passage(state, mapa, digdug_pos, enemy_pos, dx)))
            ):
            # as soluções são feitas com base na posição do digdug
            digdug_pos = state['digdug']
            # para fugir do fygar vamos é na vertical
            best_direction = best_escape_direction(state, mapa, enemy)
            if best_direction: 
                key, dir = get_next_move_key(digdug_pos, best_direction, mapa, didug_dir)
                return False, key, dir

            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            if (shoot_dir != Direction.SOUTH and is_valid_position(state, (digdug_pos[0], digdug_pos[1] + 1), rocks)):
                mapa.map[digdug_pos[0]][ digdug_pos[1] + 1]
                return False, 's', Direction.SOUTH
            if (shoot_dir != Direction.NORTH and is_valid_position(state, (digdug_pos[0], digdug_pos[1] - 1), rocks)):
                mapa.map[digdug_pos[0]][ digdug_pos[1] - 1] = 0
                return False, 'w', Direction.NORTH

        # if Pooka e se o fygar na vertical
        # TODO: AINDA NÂO CONSEGUI TESTAR
        if ( enemy['name'] == 'Pooka' and (
            ((abs(dx) == 1 and dy == 0) or (abs(dy) == 1 and dx == 0) or (dy == 0 and dx == 0))
            # or (((dx==2 and dy==0) or (dy == 2 and dy == 0)) and didug_dir != shoot_dir)
            # or (('traverse' in enemy) and (abs(dx) + abs(dy) <= 2))
            )
            ):
            print('entrei na pooka')
            digdug_pos = state['digdug']
            
            best_direction = best_escape_direction(state, mapa, enemy)
            print('best_direction', best_direction)
            if best_direction: 
                print('entrei no best direction')
                key, dir = get_next_move_key(digdug_pos, best_direction, mapa, didug_dir)
                print('key', key)
                print('dir', dir)
                return False, key, dir
            
            
            # se não houver best_direction vai para o lado contrario do inimigo
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            
            if (shoot_dir == Direction.EAST and is_valid_position(state, (digdug_pos[0] - 1, digdug_pos[1]), rocks)):
                mapa.map[digdug_pos[0] - 1][ digdug_pos[1]] = 0
                return False, 'a', Direction.WEST
            if (shoot_dir == Direction.WEST and is_valid_position(state, (digdug_pos[0] + 1, digdug_pos[1]), rocks)):
                mapa.map[digdug_pos[0] + 1][ digdug_pos[1]] = 0 

                return False, 'd', Direction.EAST
            if (shoot_dir == Direction.NORTH and is_valid_position(state, (digdug_pos[0], digdug_pos[1] + 1), rocks)):
                mapa.map[digdug_pos[0]][ digdug_pos[1] + 1] = 0
                return False, 's', Direction.SOUTH
            if (shoot_dir == Direction.SOUTH and is_valid_position(state, (digdug_pos[0], digdug_pos[1] - 1), rocks)):
                mapa.map[digdug_pos[0]][ digdug_pos[1] - 1] = 0
                return False, 'w', Direction.NORTH
            
    return True, None, didug_dir


def is_enemy_alive(saved_enemy, state):
    saved_enemy_id = saved_enemy['id']
    for enemy in state['enemies']:
        if enemy['id'] == saved_enemy_id:
            return True  # O inimigo com o ID correspondente ainda está na lista de inimigos
    return False  # Não encontrou o inimigo, ele pode estar morto


class SOLVER:
    def __init__(self, state, digdug_dir, mapa):
        self.state = state
        self.digdug_dir = digdug_dir
        self.mapa = mapa
        # se não houver goal é porque ele já chegou à passagem e está a ir contra o inimigo
        self.goal = None
        self.passage_direction = None  # achei que ia usar, nao usei
        self.passage = None  # achei que ia usar, nao usei
        self.saved_enemy = None
        self.path = None
        self.lives = None
        self.level = None
        self.notSafe = False
        # self.pooka_usando_speed = {}
        

    def run(self):
        print("-------------------------------------------------")
        if 'digdug' not in self.state or 'rocks' not in self.state:
            return '', self.digdug_dir
        
        # for aqui e meter nome das pookas vivas e se a case for igual adicionar 1 à variavel e se for diferente meter a 0
        print("digdug pos", self.state['digdug'])        
        
        if self.goal:
            print("goal", self.goal)
        if self.path:
            print("path", self.path)
        print("digdug pos", self.state['digdug'])
        for enemy in self.state['enemies']:
            print("enemy name", enemy['name'])
            print("enemy pos", enemy['pos'])
        
        
        # turns out que é preciso isto para caso ele dispare ou nao se mexa
        # em vez de ser a primeira é a antes da primeira (tamos a jogar muitooooo safe, tentando nao morrer :)
        # primeira jogada garantir que ele não vai morrer (TAMOS A JOGAR SAFE)
        print("1. O sitio em que estou é seguro? ")
        boolean_safe_zone, key, self.digdug_dir = safe_zone(
            self.state, self.mapa, self.state['digdug'], self.digdug_dir)
        if (not boolean_safe_zone):
            print("não")
            self.notSafe = True
            self.saved_enemy = None
            return key, self.digdug_dir
        else:
            if self.notSafe == True:
                self.notSafe = False

        # segunda jogada antes de tudo é se ele pode disparar
        print("2. posso disparar?")
        can_shoot_now, enemy, key = canShootNow(
            self.state, self.mapa, self.digdug_dir)
        if can_shoot_now:
            print("sim")
            return key, self.digdug_dir

        # if(closest_enemy_pos != self.saved_enemy):
        #     self.saved_enemy= closest_enemy_pos
        #     boolean_saved_enemy = False

        # se nao houver um saved_enemy ele arranja um, e calcula o goal e o path
        print("3. há saved_enemy?")
        if ((not self.saved_enemy) or (not self.lives or not self.level) or (self.lives != self.state['lives'] or self.level != self.state['level'])):
            print("não")
            self.saved_enemy = find_closest_enemy(self.state)
            # a minha estrategia aqui é considerar que todos os inimigos spwanam numa passagem por isso o goal vai ser a ponta da passagem
            if self.saved_enemy:
                self.goal, self.passage_direction, self.passage = calculate_goal(
                    self.state, self.mapa, self.saved_enemy)
            else:
                print("não encontrei um inimigo close")
                return '', self.digdug_dir
            # em seguida vou procurar uma unica vez o caminho para o goal
            # If the enemy is not in a direct line of sight or if there is an obstacle,
            # then find the path to move towards the enemy
            self.path = self.a_star_search(
                self.state, self.state["digdug"], self.goal, self.state['rocks'])
            self.lives = self.state['lives']
            self.level = self.state['level']
            print("path", self.path)
            

        # enquanto não estiver morto
        print("5. saved_enemy está vivo?")
        if self.saved_enemy and is_enemy_alive(self.saved_enemy, self.state):
            if self.saved_enemy['name'] == 'Fygar' and manhattan_distance(self.state['digdug'], self.saved_enemy['pos']) <= 3:
                self.goal = None
                
            print("sim")
            # if(goal == self.state["digdug"] or boolean_saved_enemy):
            #     boolean_saved_enemy = True
            #     goal = closest_enemy_pos

            
            # enquanto ele estiver a fazer o caminho para o goal procura se sempre se ele pode disparar e se não passa a menos de 2 tiles de qualquer um dos inimigos
            print("6. ainda não cheguei ao goal?")
            if self.goal and (tuple(self.state["digdug"]) != self.goal) and (self.path and len(self.path) > 1):
                print("não")
                next_pos = self.path[1]

                # se o didug vai para um sitio safe (isto nao é feito no search porque só o faço uma vez e os inimigos podem mudar de posição)
                boolean_safe_zone, key, self.digdug_dir = safe_zone(
                    self.state, self.mapa, next_pos, self.digdug_dir)
                print("7. o sitio para onde vou é seguro?")
                if not boolean_safe_zone:
                    print("não")
                    self.notSafe = True
                    self.saved_enemy = None
                    return key, self.digdug_dir
                else:
                    if self.notSafe == True:
                        self.notSafe = False
                # --------
                print("sim")
                self.path.pop(0)
                key, self.digdug_dir = get_next_move_key(
                    self.state["digdug"], next_pos, self.mapa, self.digdug_dir)
            
                return key, self.digdug_dir  # Return the key to move DigDug
            else:
                print("Perseguindo o inimigo")
                # se entrar aqui ele já chegou à passagem e está a ir contra o inimigo
                self.goal = None
                saved_enemy_id = self.saved_enemy['id']
                for enemy in self.state['enemies']:
                    if enemy['id'] == saved_enemy_id:
                        enemy_pos = tuple(enemy['pos'])
                
                if enemy_pos[1] < 3:
                    self.saved_enemy = None
                    return '', self.digdug_dir
                        
                if (self.saved_enemy['name'] == 'Fygar'):
                    digdug_pos = self.state['digdug']
                    
                    distance_y_minus_1 = abs(digdug_pos[0] - enemy_pos[0]) + abs(digdug_pos[1] - (enemy_pos[1] - 1))
                    distance_y_plus_1 = abs(digdug_pos[0] - enemy_pos[0]) + abs(digdug_pos[1] - (enemy_pos[1] + 1))

                    # Determinando qual posição está mais perto
                    if distance_y_minus_1 < distance_y_plus_1:
                        enemy_pos = (enemy_pos[0], enemy_pos[1] - 1)
                    else:
                        enemy_pos = (enemy_pos[0], enemy_pos[1] + 1)
                    
                self.path = self.a_star_search(
                    self.state, self.state["digdug"], enemy_pos, self.state['rocks'], perseguindo_enemy=True)
                
                if self.path and len(self.path) > 1:
                    next_pos = self.path[1]

                    # se o didug vai para um sitio safe (isto nao é feito no search porque só o faço uma vez e os inimigos podem mudar de posição)
                    print("8. o sitio para onde vou é seguro?")
                    boolean_safe_zone, key, self.digdug_dir = safe_zone(
                        self.state, self.mapa, next_pos, self.digdug_dir)
                    if not boolean_safe_zone:
                        print("não")
                        self.notSafe = True
                        self.saved_enemy = None
                        return key, self.digdug_dir
                    else:
                        if self.notSafe == True:
                            self.notSafe = False
                    # --------

                    key, self.digdug_dir = get_next_move_key(
                        self.state["digdug"], next_pos, self.mapa, self.digdug_dir)
                    return key, self.digdug_dir

            # zera tudo e faz tudo de novo

                # working here
                # If DigDug can shoot the enemy directly, then return the shoot command
                # if can_shoot_enemy(self.state["digdug"], closest_enemy_pos, enemy_dir, next_pos, self.mapa, self.state):
                #     # Here 'A' is a placeholder for the actual shoot command key you might have
                #     dir_shoot = get_direction(self.state["digdug"], closest_enemy_pos)
                #     return 'A', dir_shoot  # Assume 'A' is the key to shoot
        else:
            # inimigo morreu :)
            print("inimigo morreu")
            self.saved_enemy = None
        # If no path or enemy is found, don't move
        return '', self.digdug_dir

    def a_star_search(self, state, start, goal, rocks, perseguindo_enemy=False):
        start = tuple(start)
        goal = tuple(goal)
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: manhattan_distance(start, goal)}

        # Dictionary to map the directions to their offsets
        offset = {
            Direction.NORTH: (0, -1),
            Direction.SOUTH: (0, 1),
            Direction.EAST: (1, 0),
            Direction.WEST: (-1, 0)
        }

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1] 

            # Iterate through all possible directions
            for direction in Direction:
                dx, dy = offset[direction]
                neighbor = (current[0] + dx, current[1] + dy)

                if not is_valid_position(state, neighbor, rocks):
                    continue
                
                if (perseguindo_enemy):
                    if (not safe_pos_enemy(state, self.mapa, neighbor, direction) and manhattan_distance(neighbor, goal) > 1) :
                        print(neighbor)
                        continue

                # if not is_valid_position_enemy(state, neighbor):
                #     continue

                # # quero matar o fygar
                # if closest_enemy and closest_enemy['name'] == "Fygar":
                #     if not is_valid_fygar(neighbor, closest_enemy):
                #         continue
                
                cost = 1
                if self.mapa.get_tile(neighbor) == Tiles.STONE:
                    cost = 3
                
                
                if self.state['digdug'][0] == 1 and self.state['digdug'][1] in range(0, 3):
                    if neighbor == (self.state['digdug'][0], self.state['digdug'][1] + 1):
                        cost = 0
                    else:
                        cost = 10 
                        
                tentative_g_score = g_score[current] + cost
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + \
                        manhattan_distance(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None 
