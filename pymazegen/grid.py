
N = 1
S = 2
E = 4
W = 8

DV = { E: (1, 0), W: (-1, 0), N: (0, 1), S: (0, -1) }
D = [ N, S, E, W]
OPPOSITES = { E: W, W: E, N: S, S: N}

class Grid(object):

    def __init__(self, side):
        self._grid = [ [ 0 for j in range(side) ] for i in range(side) ]
        self._length = side

    def getNeighbor(self, x, y, d):
        return x + DV[d][0], y + DV[d][1]

    def getNeighbors(self, x, y):
        neighbors = []
        for d in D:
            nx, ny = self.getNeighbor(x, y, d)
            if (nx < 0 or nx >= self.length
                or ny < 0 or ny >= self.length):
                continue
            neighbors.append( ( nx, ny, d ) )

        return neighbors

    def add_wall(self, x, y, d):
        nx, ny = self.getNeighbor(x, y, d)
        # print "p(%d, %d), n(%d, %d)" % (x, y, nx, ny)
        self[x][y] |= d
        self[nx][ny] |= OPPOSITES[d]

    # Enable array access
    def __len__(self):
        return self.length

    def __getitem__(self, i):
        return self._grid[i]

    def __setitem__(self, i, v):
        self._grid[i] = v

    def __delitem__(self, i):
        del self._grid[i]

    def __iter__(self):
        return iter(self._grid)

    def __reversed__(self):
        return reversed(self._grid)

    def __str__(self):
        return self._stringify_grid()

    def __repr__(self):
        return self._stringify_grid()

    def _stringify_grid(self):
        string = 'E -->\nS' + ' '*2 + '-' * ( self._length*2  + 1) + '\n'
        for y in reversed(range(self._length)):
            if y == self._length:
                string += '| '
            elif y == self._length-1:
                string += 'v '
            else:
                string += '  '

            string += '|'
            for x in range(self._length):
                cell = self[x][y]
                string += '%2X' % cell

            string += '|'
            string += '\n'
        string += ' ' + '-' * ( self._length*2  + 1) + '\n'
        return string

