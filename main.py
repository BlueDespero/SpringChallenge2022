# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# base_x: The corner of the map representing your base
import heapq
import itertools
import sys

import numpy as np

base_x, base_y = [int(i) for i in input().split()]
enemy_base_x, enemy_base_y = [0, 0] if base_x != 0 else [17630, 9000]

heroes_per_player = int(input())  # Always 3
heroes = []

print(base_x, file=sys.stderr)
print(base_y, file=sys.stderr)


# game loop

def distance(x1, y1, x2, y2):
    return np.round(np.linalg.norm((x1 - x2, y1 - y2)))


def get_default_position():
    if base_x == 0:
        positions = [(1469, 5600), (4254, 3900), (6200, 900)]
    else:
        positions = [(11834, 7447), (13387, 4757), (16077, 3204)]
    for i in range(3):
        yield positions[i]


class Entity:
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


def closest_hero(monster: Monster):
    closest_h = None
    closest_h_turns = 1000000

    hero: Hero

    for hero in heroes:
        counter = get_turns_distance(hero, monster)

        if counter < closest_h_turns:
            closest_h_turns = counter
            closest_h = hero

    return closest_h, closest_h_turns


def update_hero(update_hero: Hero):
    hero: Hero
    for hero in heroes:
        if hero.id == update_hero.id:
            hero.update(update_hero)


def get_turns_distance(hero: Hero, monster: Monster):
    counter = 1
    dist = distance(hero.x, hero.y, monster.x + monster.vx * counter, monster.y + monster.vy * counter)

    while dist >= 800 * counter:
        counter += 1
        dist = distance(hero.x, hero.y, monster.x + monster.vx * counter, monster.y + monster.vy * counter)

    return counter


def get_base_turns_distance(monster: Monster):
    counter = 1
    dist = distance(base_x, base_y, monster.x + monster.vx * counter, monster.y + monster.vy * counter)

    while dist >= 5000:
        counter += 1
        dist = distance(base_x, base_y, monster.x + monster.vx * counter, monster.y + monster.vy * counter)

    sim_x, sim_y = monster.x + monster.vx * counter, monster.y + monster.vy * counter
    counter += (distance(base_x, base_y, sim_x, sim_y) - 300) / 400

    return counter


def can_catch_kill(hero: Hero, monster: Monster):
    mon_time = get_base_turns_distance(monster)
    catch_time = get_turns_distance(hero, monster)
    kill_time = monster.health / 2
    return mon_time >= (catch_time + kill_time)


def should_wind_attack(hero: Hero, monster: Monster):
    if mana < 10:
        return False

    if distance(hero.x, hero.y, monster.x, monster.y) > 1280:
        return False

    if distance(base_x, base_y, monster.x + monster.vx, monster.y + monster.vy) <= 5500:
        return True

    #if not can_catch_kill(hero, monster):
    #    return True

    return False


def attack(hero: Hero, monster: Monster):
    if should_wind_attack(hero, monster):
        print("SPELL WIND %s %s" % (enemy_base_x, enemy_base_y))
    else:
        print("MOVE %s %s" % (monster.x + monster.vx, monster.y + monster.vy))


def match_heroes_targets(targets):
    all_perms = itertools.permutations(range(3))
    targets = [t[1] for t in targets]

    best_distance = 10000
    best_perm = None

    for perm in all_perms:
        distances = 0
        for i, p in enumerate(perm):
            if len(targets) > i:
                distances += get_turns_distance(heroes[p], targets[i])

        print("%s %s" % (perm, distances), file=sys.stderr)
        if best_distance > distances:
            best_distance = distances
            best_perm = perm

    for i, p in enumerate(best_perm):
        if len(targets) > best_perm.index(i):
            target = targets[best_perm.index(i)]
            attack(heroes[i], target)
        else:
            print("MOVE %s %s" % (heroes[i].def_x, heroes[i].def_y))


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

    match_heroes_targets(targets)
