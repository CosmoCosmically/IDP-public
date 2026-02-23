####################################################################################################
#
# Utility class for sensor moving average.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################


class movingAverage:
    """
    Fixed-size moving average filter for a four-channel sensor array.

    Maintains independent circular buffers and running totals for each channel.
    """
    def __init__(self, size):
        """
        Initialise moving average buffers.

        Args:
            size (int): Window size for each channel.
        """
        self.size = size
        self.buffers = [[0] * size for _ in range(4)]
        self.indices = [0, 0, 0, 0]
        self.totals = [0, 0, 0, 0]
        self.counts = [0, 0, 0, 0]

    def add(self, values):
        """
        Add a new set of readings to the moving average buffers.

        Args:
            values (tuple[int, int, int, int]): Latest sensor readings.
        """
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
        """
        Compute the current moving average for each channel.

        Returns:
            tuple[float, float, float, float]: Averaged sensor values.
        """
        vals = (
            self.totals[i] / self.counts[i] if self.counts[i] else 0 for i in range(4)
        )
        return tuple(vals)

    def clamp(self, threshold=0.5) -> tuple[int, ...]:
        """
        Convert averaged values into binary outputs using a threshold.

        Args:
            threshold (float): Cutoff value for activation.

        Returns:
            tuple[int, int, int, int]: Thresholded sensor states (0 or 1).
        """
        vals = (
            1 if (self.totals[i] / self.counts[i]) > threshold else 0 for i in range(4)
        )
        return tuple(vals)
