from flask import  url_for
import numpy as np
from app import nn_model


def get_figure_tag(x, y):
    x, y = np.array(x), np.array(y)
    xs, ys, scale, xm, ym = scale_coordinates(x, y)
    r = np.array([xs, ys]).T
    ar = figure2ndarray(r)
    output = nn_model.predict(ar[None, ...], verbose=0)
    #print(output)

    return '<g class="deletable">'


def figure2ndarray(r):
    im = np.zeros((30, 30))
    rt = r[::-1].T.astype(int)
    im[rt[0], rt[1]] = 1
    return im

def scale_coordinates(x, y):
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    x_len = x_max - x_min
    y_len = y_max - y_min
    scale = max(x_len, y_len) / 25
    # чтобы фигура с запасом помещалась в поле 30 x 30
    x_scaled = x / scale
    y_scaled = y / scale
    x_scaled_med = (x_scaled.max() + x_scaled.min()) / 2
    y_scaled_med = (y_scaled.max() + y_scaled.min()) / 2
    x_centered = x_scaled - x_scaled_med + 15
    y_centered = y_scaled - y_scaled_med + 15
    return x_centered, y_centered, scale, x_scaled_med, y_scaled_med

def scale_back_coordinates(
        x_centered, y_centered, scale, x_scaled_med, y_scaled_med
    ):
    x = (x_centered - 15 + x_scaled_med) * scale
    y = (y_centered - 15 + y_scaled_med) * scale
    return x, y


