import pandas


def merge(count_frames, diff_frames=[]):
    count_frame = pandas.DataFrame()
    for frame in count_frames:
        count_frame = count_frame.merge(
            frame,
            how='outer',
            right_index=True,
            left_index=True)

    # TODO: diff_frames

    return count_frame
