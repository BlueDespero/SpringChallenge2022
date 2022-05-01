# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# base_x: The corner of the map representing your base
import heapq
import sys

import numpy as np

base_x, base_y = [int(i) for i in input().split()]
heroes_per_player = int(input())  # Always 3
heroes = []

print(base_x, file=sys.stderr)
print(base_y, file=sys.stderr)


# game loop

def distance(x1, y1, x2, y2):
    return np.round(np.linalg.norm((x1 - x2, y1 - y2)))


def get_default_position():
    if base_x == 0:
        positions = [(1200, 5000), (3500, 3500), (5000, 600)]
    else:
        positions = [(12000, 8000), (14000, 6000), (17000, 4000)]
    for i in range(3):
        yield positions[i]


class Entity():
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y


class Hero(Entity):
    def __init__(self, id, x, y, def_pos=(0, 0)):
        super().__init__(id, x, y)
        self.target = (0, 0)
        self.def_x = def_pos[0]
        self.def_y = def_pos[1]

    def update(self, update_hero):
        self.x = update_hero.x
        self.y = update_hero.y


class Monster(Entity):

    def __init__(self, id, x, y, health, vx, vy, near_base):
        super().__init__(id, x, y)
        self.priority = 0
        self.hits_in = None
        self.health = health
        self.vx = vx
        self.vy = vy
        self.neat_base = near_base
        self.alive = True
        self.set_priority()

    def __lt__(self, other):
        return self.priority < other.priority

    def connects_in(self):
        counter = 0
        sim_x, sim_y = self.x, self.y
        sim_vx, sim_vy = self.vx, self.vy
        sim_near_base = self.neat_base == 1
        while distance(sim_x, sim_y, base_x, base_y) > 300:
            counter += 1
            sim_x += sim_vx
            sim_y += sim_vy
            if not sim_near_base and distance(sim_x, sim_y, base_x, base_y) <= 5000:
                sim_near_base = True
                sim_vx, sim_vy = base_x - sim_x, base_y - sim_y
                sim_vx, sim_vy = np.round((np.array([sim_vx, sim_vy]) / np.linalg.norm([sim_vx, sim_vy])) * 400)

        return counter

    def set_priority(self):
        base = self.connects_in()
        prop_priority = base - self.health / 2
        _, turns = closest_hero(self)
        prop_priority -= turns

        # print(prop_priority, file=sys.stderr)
        self.priority = prop_priority


def closest_hero(monster: Monster, ):
    closest_h = None
    closest_h_turns = 1000000

    hero: Hero

    for hero in heroes:
        counter = 1

        dist = distance(hero.x, hero.y, monster.x + monster.vx * counter, monster.y + monster.vy * counter)

        while dist >= 800 * counter:
            counter += 1
            # print(dist, file=sys.stderr)
            dist = distance(hero.x, hero.y, monster.x + monster.vx * counter, monster.y + monster.vy * counter)

        if counter < closest_h_turns:
            closest_h_turns = counter
            closest_h = hero

    return closest_h, closest_h_turns


def update_hero(update_hero: Hero):
    hero: Hero
    for hero in heroes:
        if hero.id == update_hero.id:
            hero.update(update_hero)


def_pos_gen = get_default_position()

while True:
    monsters = []
    for i in range(2):
        # health: Each player's base health
        # mana: Ignore in the first league; Spend ten mana to cast a spell
        health, mana = [int(j) for j in input().split()]
    entity_count = int(input())  # Amount of heros and monsters you can see
    for i in range(entity_count):
        # _id: Unique identifier
        # _type: 0=monster, 1=your hero, 2=opponent hero
        # x: Position of this entity
        # shield_life: Ignore for this league; Count down until shield spell fades
        # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
        # health: Remaining health of this monster
        # vx: Trajectory of this monster
        # near_base: 0=monster with no target yet, 1=monster targeting a base
        # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
        _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [int(j) for j in
                                                                                               input().split()]
        if _type == 0 and threat_for == 1:
            this_mon = Monster(_id, x, y, health, vx, vy, near_base)
            heapq.heappush(monsters, (this_mon.priority, this_mon))
        elif _type == 1:
            if len(heroes) < 3:
                heroes.append(Hero(_id, x, y, next(def_pos_gen)))
            else:
                update_hero(Hero(_id, x, y))

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    # In the first league: MOVE <x> <y> | WAIT; In later leagues: | SPELL <spellParams>;
    targets = heapq.nsmallest(min(heroes_per_player, len(monsters)), monsters)

    for i in range(heroes_per_player):
        if targets:
            target = targets.pop()[1]
            # print("%s %s %s %s  || %s %s" % (target.x, target.vx, target.y, target.vy, target.x + target.vx,
            # target.y + target.vy), file=sys.stderr)
            print("MOVE %s %s" % (target.x + target.vx, target.y + target.vy))
        else:
            print("MOVE %s %s" % (heroes[i].def_x, heroes[i].def_y))
