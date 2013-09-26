
import random
import copy

from pymazegen.grid import Grid, DV, N, S, E, W


def choose_newest(c):
    return c


def choose_oldest(c):
    return 0


def choose_random(c):
    return random.randint(0, c)


def choose_orientation(w, h):
    if w < h:
        return True
    elif h < w:
        return False
    else:
        return True if random.randint(0, 1) == 0 else False


def with_rarity(common_func, uncommon_func, percent_rarity):
    r = random.randint(1, 100)
    if (r <= percent_rarity):
        return uncommon_func
    else:
        return common_func


def pop_random(sequence):
    tmp = list(sequence)
    while len(tmp) > 0:
        i = random.randint(0, len(tmp) - 1)
        v = tmp[i]
        yield v
        del tmp[i]


class Generator(object):

    def generate(self, side_length, seed=None):
        random.seed(seed)
        # Setup environment
        self.length = side_length
        self.grid = Grid(side_length)
        self.maze_steps = []

        # Ask child to generate maze
        self._generate()

        return self.grid

    def _generate(self):
        raise RuntimeError("Unimplemented method")

    def save(self, local_dict):
        grid = copy.deepcopy(self.grid)
        local_dict = copy.deepcopy(local_dict)
        for key, item in local_dict.items():
            setattr(grid, key, item)
        self.maze_steps.append(grid)


class RecursiveGenerator(Generator):

    def _generate(self):
        # x = random.randint(0, self.width - 1)
        # y = random.randint(0, self.height - 1)
        self.carve_passages_from(0, 0)

    def carve_passages_from(self, x, y):
        self.maze_steps.append(copy.deepcopy(self.grid))
        for nx, ny, d in pop_random(self.grid.getNeighbors(x, y)):
            if self.grid.get(nx, ny) != 0:
                continue

            self.grid.carve_passage(nx, ny, d)
            self.carve_passages_from(nx, ny)


class GrowingTreeGenerator(Generator):

    def __init__(self, strategy):
        super(GrowingTreeGenerator, self).__init__()
        choosing_strategies = {
            'newest': choose_newest,
            'oldest': choose_oldest,
            'random': choose_random,
            'newest75-random25': lambda c: with_rarity(choose_newest, choose_random, 25)(c),
            'newest75-oldest25': lambda c: with_rarity(choose_newest, choose_oldest, 25)(c),
            'newest50-random50': lambda c: with_rarity(choose_newest, choose_random, 50)(c),
            'newest50-oldest50': lambda c: with_rarity(choose_newest, choose_oldest, 50)(c),
            'newest25-random75': lambda c: with_rarity(choose_newest, choose_random, 75)(c),
            'newest25-oldest75': lambda c: with_rarity(choose_newest, choose_oldest, 75)(c),
            'oldest75-random25': lambda c: with_rarity(choose_oldest, choose_random, 25)(c),
            'oldest50-random50': lambda c: with_rarity(choose_oldest, choose_random, 50)(c),
            'oldest25-random75': lambda c: with_rarity(choose_oldest, choose_random, 75)(c),
        }
        self.choose_func = choosing_strategies.get(strategy)
        if not self.choose_func:
            raise RuntimeError("Invalid strategy: %s" % strategy)

    def _generate(self):
        # x = random.randint(0, self.width - 1)
        # y = random.randint(0, self.height - 1)
        self.cells = [ (0, 0) ]
        while len(self.cells) > 0:
            self.grow_tree()

    def grow_tree(self):
        self.maze_steps.append(copy.deepcopy(self.grid))
        found_unvisited = False
        i = self.choose_index()
        x, y = self.cells[i]

        for nx, ny, d in pop_random(self.grid.getNeighbors(x, y)):
            if self.grid.get(nx, ny) != 0:
                continue

            self.grid.carve_passage(nx, ny, d)
            self.cells.append((nx, ny))
            found_unvisited = True
            break

        if not found_unvisited:
            del self.cells[i]

    def choose_index(self):
        return self.choose_func(len(self.cells) - 1)


class RecursiveDivision(Generator):

    def __init__(self, smallest_chamber):
        super(RecursiveDivision, self).__init__()
        self.smallest_chamber = smallest_chamber

    def _generate(self):
        # for y in range(self.length):
        #     self.grid[0][y] |= W
        #     self.grid[self.length-1][y] |= E

        # for x in range(self.length):
        #     self.grid[x][0] |= S
        #     self.grid[x][self.length-1] |= N

        self.subdivide_chamber(0, 0, self.length, self.length)

    def subdivide_chamber(self, x, y, w, h, horizontal=True):
        sc = self.smallest_chamber
        if w <= sc or h <= sc: return

        # Where is the wall?
        wx = x + ( 0 if horizontal else random.randint(0, w - 1 - sc) )
        wy = y + ( random.randint(0, h - 1 - sc) if horizontal else 0 )

        # Where is the passage?
        px = wx + ( random.randint(0, w-1) if horizontal else 0 )
        py = wy + ( 0 if horizontal else random.randint(0, h-1))

        # select which direction to add a wall
        d = N if horizontal else E

        # select which value to increment when drawing line
        dx = DV[d][1]
        dy = DV[d][0]

        # How long? Required for rectangular chambers
        length = w if horizontal else h

        debug_info = {
            'x': x, 'y': y, 'w': w, 'h': h,
            'wx': wx, 'wy': wy, 'px': px, 'py': py,
            'd': d, 'dx': dx, 'dy': dy, 'length': length,
            'horizontal': horizontal,
        }
        # print 'debug: ', debug_info

        ix = wx
        iy = wy
        for i in range(length):
            if not (ix == px and iy == py):
                self.grid.add_wall(ix, iy, d)
            # print 'i(%d, %d)' % (ix, iy)
            ix += dx
            iy += dy

        self.save(debug_info)

        # Calculate top/ left chamber
        nx, ny = x, y
        nw, nh = (w, wy - y + 1) if horizontal else (wx - x + 1, h)
        self.subdivide_chamber(nx, ny, nw, nh, choose_orientation(nw, nh))

        # Calculate bottom/ right chamber
        nx, ny = (x, wy + 1) if horizontal else (wx + 1, y)
        nw, nh = (w, h - (wy - y + 1)) if horizontal else (w - (wx - x + 1), h)
        self.subdivide_chamber(nx, ny, nw, nh,  choose_orientation(nw, nh))