####################################################################################################
#
# Utility class for sensor moving average.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################


class movingAverage:
    def __init__(self, size):
        self.size = size
        self.buffers = [[0] * size for _ in range(4)]
        self.indices = [0, 0, 0, 0]
        self.totals = [0, 0, 0, 0]
        self.counts = [0, 0, 0, 0]

    def add(self, values):
        for i in range(4):
            # remove oldest value
            self.totals[i] -= self.buffers[i][self.indices[i]]
            # add new value
            self.buffers[i][self.indices[i]] = values[i]
            self.totals[i] += values[i]

            # advance index
            self.indices[i] = (self.indices[i] + 1) % self.size

            if self.counts[i] < self.size:
                self.counts[i] += 1

    def average(self):
        vals = (
            self.totals[i] / self.counts[i] if self.counts[i] else 0 for i in range(4)
        )
        return tuple(vals)

    def clamp(self, threshold=0.5) -> tuple[int, ...]:
        vals = (
            1 if (self.totals[i] / self.counts[i]) > threshold else 0 for i in range(4)
        )
        return tuple(vals)
