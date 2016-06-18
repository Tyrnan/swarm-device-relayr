__author__ = 'ala'

from RingBuffer import RingBuffer


class DistanceData:
    def __init__(self, nodeid, buffersize=10):
        self.nodeid = nodeid
        self.buffersize = buffersize
        self.buffer = RingBuffer(buffersize)

    def add_observation(self, observation):
        self.buffer.append(observation)

    def get_filtered_value(self):
        #TODO implement filtering
        return self.buffer.get()[-1]
