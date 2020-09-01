
class SquaresSequence():
    '''class for creating sequence for light and normal squares'''
    def __init__(self):
        self.depth_limit = 12
        self.depth = 12
        self.counter = 0
        self.speed = 10
        self.mode = 1
        self.sequence = []
        self.mode_up(False)

    def depth_increase(self):
        '''depth up'''
        self.depth += 1
        if self.depth > self.depth_limit:
            self.depth = self.depth_limit
        self.mode_up(up=False)
        return None

    def depth_decrease(self):
        '''depth down'''
        self.depth -= 1
        if self.depth < 0:
            self.depth = 0
        self.mode_up(up=False)
        return None

    def count(self):
        '''counter up'''
        self.counter += 1
        if self.counter > self.speed:
            self.counter = 0
            self.sequence = self.sequence[-1:] + self.sequence[:-1]
        return None

    def speed_up(self):
        self.speed -= 1
        if self.speed < 1:
            self.speed = 20
        print('squares speed: {}'.format(self.speed))
        return None

    def mode_up(self, up=True):
        '''mode_up with number of light squares in all range depth; mode is shrinked to depth'''
        if up:
            self.mode += 1
        else:
            self.mode = min(self.mode, self.depth)

        if self.mode > self.depth:
            self.mode = 0

        number_of_ones = min(self.mode, self.depth)
        self.sequence = [1]*number_of_ones + [0 for x in range(max(self.depth - self.mode, 0))]
        print('light squares: {}/{}'.format(number_of_ones, self.depth))
        return None

    def mode_up__(self, up=True):
        '''mode_up with fixed number of light squares; it keeps mode independent of depth
        not in use for now
        '''
        if up:
            self.mode += 1

        if self.mode > 5:
            self.mode = 0

        if self.mode == 0:
            self.sequence = [0 for x in range(self.depth)]

        if self.mode in (1, 2, 3, 4):
            self.sequence = [1]*min(self.mode, self.depth) + [0 for x in range(max(self.depth - self.mode, 0))]

        if self.mode == 5:
            self.sequence = [1 for x in range(self.depth)]
        return None


if __name__ == "__main__":
    pass
