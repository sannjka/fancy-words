import os
from flask import  url_for, current_app
import numpy as np
from PIL import Image
from app import nn_model


def get_figure_tag(x, y):
    x, y = np.array(x), np.array(y)

    xs, ys, scale, xm, ym = scale_coordinates(x, y)
    r = np.array([xs, ys]).astype(np.uint8)
    ar = figure2ndarray(r)

    # display picture for debugging
    local = os.environ.get('PAINT_LOCAL', 0)
    if local == '1':
        im = Image.fromarray(ar.astype(np.uint8) * 255)
        picture_path = os.path.join(current_app.root_path,
                                    'static',
                                    'temp.png')
        im.save(picture_path)

    prediction = nn_model.predict(ar[None, ...], verbose=0)
    figure_index = np.argmax(prediction[0])

    coordinates = prediction[1].reshape(4, 2)
    xscaled, yscaled = coordinates[:, 0], coordinates[:, 1]
    if figure_index == 3:
        xback, yback = scale_back_coordinates_ellipse(
            xscaled, yscaled, scale, xm, ym
        )
    else:
        xback, yback = scale_back_coordinates(xscaled, yscaled, scale, xm, ym)
    coordinates = np.array([xback, yback]).T

    # we want to put start point of the figure to start point of x, y
    move_to_start_point(coordinates, figure_index, x, y)

    if figure_index == 0:
        figure_tag = get_bezier_tag(coordinates)
    elif figure_index == 1:
        figure_tag = get_triangle_tag(coordinates)
    elif figure_index == 2:
        figure_tag = get_rectangle_tag(coordinates)
    elif figure_index == 3:
        figure_tag = get_ellipse_tag(coordinates)
    elif figure_index == 4:
        figure_tag = get_straight_tag(coordinates)

    return figure_tag

def get_bezier_tag(c):
    """
    q - second and third points get difference with the first one
    Q - all values are absolute
    """
    output = f'''
          <g class="deletable">
            <path class="deletable line"
                d="M {c[0, 0]} {c[0, 1]}
                Q {c[1, 0]} {c[1, 1]}
                {c[2, 0]} {c[2, 1]}"
                fill="none"
                stroke="red"
                stroke-width="5"
                />
            <path
                d="M {c[0, 0]} {c[0, 1]}
                Q {c[1, 0]} {c[1, 1]}
                {c[2, 0]} {c[2, 1]}"
                fill="none"
                stroke="green"
                stroke-width="20"
                stroke-opacity="0"/>
          </g>
    '''
    return output

def get_triangle_tag(c):
    output = f'''
          <g class="deletable">
            <path class="deletable line"
                d="M {c[0, 0]} {c[0, 1]}
                L {c[1, 0]} {c[1, 1]}
                L {c[2, 0]} {c[2, 1]} Z"
                fill="none"
                stroke="red"
                stroke-width="5"
                />
            <path
                d="M {c[0, 0]} {c[0, 1]}
                L {c[1, 0]} {c[1, 1]}
                L {c[2, 0]} {c[2, 1]} Z"
                fill="none"
                stroke="green"
                stroke-width="20"
                stroke-opacity="0"/>
          </g>
    '''
    return output

def get_rectangle_tag(c):
    output = f'''
          <g class="deletable">
            <path class="deletable line"
                d="M {c[0, 0]} {c[0, 1]}
                L {c[1, 0]} {c[1, 1]}
                L {c[2, 0]} {c[2, 1]}
                L {c[3, 0]} {c[3, 1]} Z"
                fill="none"
                stroke="red"
                stroke-width="5"
                />
            <path
                d="M {c[0, 0]} {c[0, 1]}
                L {c[1, 0]} {c[1, 1]}
                L {c[2, 0]} {c[2, 1]}
                L {c[3, 0]} {c[3, 1]} Z"
                fill="none"
                stroke="green"
                stroke-width="20"
                stroke-opacity="0"/>
          </g>
    '''
    return output

def get_ellipse_tag(c):
    '''
    При обучении модели угол поворота масштабировался к диапазону [0..15]
    При этом значения в радианах находились в диапазоне [-pi/2..pi/2]
    '''
    output = f'''
          <g class="deletable">
            <ellipse class="deletable line"
                rx="{c[1, 0]}" ry="{c[1, 1]}" cx="{c[0, 0]}" cy="{c[0, 1]}"
                transform="rotate({c[2, 0] / 30 * 90} {c[0, 0]} {c[0, 1]})"
                fill="none"
                stroke="red"
                stroke-width="5"
                />
            <ellipse
                rx="{c[1, 0]}" ry="{c[1, 1]}" cx="{c[0, 0]}" cy="{c[0, 1]}"
                transform="rotate({c[2, 0]  / 30 * 90} {c[0, 0]} {c[0, 1]})"
                fill="none"
                stroke="green"
                stroke-width="20"
                stroke-opacity="0"/>
          </g>
    '''
    return output

def get_straight_tag(c):
    output = f'''
          <g class="deletable">
            <path class="deletable line"
                d="M {c[0, 0]} {c[0, 1]}
                L {c[1, 0]} {c[1, 1]}"
                fill="none"
                stroke="red"
                stroke-width="5"
                />
            <path
                d="M {c[0, 0]} {c[0, 1]}
                L {c[1, 0]} {c[1, 1]}"
                fill="none"
                stroke="green"
                stroke-width="20"
                stroke-opacity="0"/>
          </g>
    '''
    return output

def figure2ndarray(r):
    im = np.zeros((30, 30))
    im[r[1], r[0]] = 1
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

def scale_back_coordinates_ellipse(
        x_centered, y_centered, scale, x_scaled_med, y_scaled_med
    ):
    x, y = x_centered, y_centered
    x[0] = (x_centered[0] - 15 + x_scaled_med) * scale
    y[0] = (y_centered[0] - 15 + y_scaled_med) * scale
    x[1] = (x_centered[1]) * scale
    y[1] = (y_centered[1]) * scale
    return x, y

def move_to_start_point(coordinates, figure_index, x, y):
    if figure_index == 0: # bezier
        move_to_start_point_bezier(coordinates, x, y)
    elif figure_index == 1: # triangle
        move_to_start_point_nangle(coordinates, x, y, 3)
    elif figure_index == 2: # rectangle
        move_to_start_point_nangle(coordinates, x, y, 4)
    elif figure_index == 3: # ellipse
        move_to_start_point_ellipse(coordinates, x, y)
    elif figure_index == 4: # straight
        coordinates[0] = np.array([x[0], y[0]])
        coordinates[1] = np.array([x[-1], y[-1]])

def distance(xy, x, y):
    return np.sqrt((xy[:, 0] - x) ** 2 + (xy[:, 1] - y) ** 2)

def move_to_start_point_bezier(coordinates, x, y):
    dists = distance(coordinates[:3], x[0], y[0])
    first = 0 if dists[0] < dists[2] else 2
    last = (first == 0) * 2
    # сопоставим первую точку
    coordinates -= coordinates[first] - np.array([x[0], y[0]])
    # сопоставим последнюю точку
    coordinates[last] = np.array([x[-1], y[-1]])

def move_to_start_point_nangle(coordinates, x, y, n):
    dists = distance(coordinates[:n], x[0], y[0])
    ind = np.argmin(dists)
    coordinates -= coordinates[ind] - np.array([x[0], y[0]])

def move_to_start_point_ellipse(coordinates, x, y):
    angle = coordinates[2, 0] / 30 * np.pi / 2
    basis = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle), np.cos(angle)]])
    t = np.linspace(0, np.pi * 2, 30 * 3)[:, None]
    sin = np.sin(t)
    cos = np.cos(t)
    a_cost_ix = coordinates[1, 0] * cos * basis[0]
    b_sint_iy = coordinates[1, 1] * sin * basis[1:2]
    r = coordinates[0] + a_cost_ix + b_sint_iy
    dists = distance(r, x[0], y[0])
    ind = np.argmin(dists)

    coordinates[0] = coordinates[0] - (r[ind] - np.array([x[0], y[0]]))

