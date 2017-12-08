import pandas

from app.cluster import cluster

class DataFrameMerge():
    def __init__(self, count_frames, diff_frames=[], clustering=False):
        self.count_frame = pandas.DataFrame()
        for frame in count_frames:
            self.count_frame = self.count_frame.merge(
                frame,
                how='outer',
                right_index=True,
                left_index=True)
        if clustering:
            self.count_frame = cluster(self.count_frame)

        # TODO: diff_frames
