from flask import  url_for
import numpy as np
from app import nn_model


def get_figure_tag(x, y):
    x, y = np.array(x), np.array(y)
    xs, ys, scale, xm, ym = scale_coordinates(x, y)
    r = np.array([xs, ys]).T
    ar = figure2ndarray(r)
    prediction = nn_model.predict(ar[None, ...], verbose=0)
    #print(prediction)
    figure_index = np.argmax(prediction[0])

    coordinates = prediction[1].reshape(4, 2)

    # Here we need to scale back coordinates !!!

    if figure_index == 0:
        figure_tag = get_bezier_tag(coordinates)
    elif figure_index == 1:
        figure_tag = get_triangle_tag(coordinates)
    elif figure_index == 2:
        figure_tag = get_rectangle_tag(coordinates)
    elif figure_index == 3:
        figure_tag = get_ellipse_tag(coordinates)

    #print(figure_tag)
    #print(prediction[1].reshape(4, 2))

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
                transform="rotate({c[2, 0] / 15 * np.pi / 2}), translate(0, 0)"
                transform-origin="50% 50%"
                fill="none"
                stroke="red"
                stroke-width="5"
                />
            <ellipse
                rx="12" ry="8" cx="15" cy="15"
                transform="rotate({c[2, 0] / 15 * np.pi / 2}), translate(0, 0)"
                transform-origin="50% 50%"
                fill="none"
                stroke="green"
                stroke-width="8"
                stroke-opacity="0.5"/>
          </g>
    '''
    return output

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


