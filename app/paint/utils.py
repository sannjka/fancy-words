
def get_figure_tag(coordinates):
    return '... figure tag...'


def figure2ndarray(r):
    im = np.zeros((r.shape[0], *self.max_values))
    ids = np.concatenate([[i] * r.shape[1] for i in range(r.shape[0])])
    rt = r[...,::-1].reshape(-1, r.shape[2]).T
    im[ids, rt[0], rt[1]] = 1
    #im[ids, *r[...,::-1].reshape(-1, r.shape[2]).T] = 1
    return im
