import sys
import os
import time
import random
import math
import numpy as np
import cv2
from handle_mouse import MouseHandler
from squares_sequence import SquaresSequence


def blank_image(height, width, layers=3, value=255):
    '''create blank image, with specified shape, layers and initial value'''
    img = np.ones((height, width, layers), dtype=np.uint8)*value
    return img
    
    
def draw_grid(img, center, color_mode, walls=True):
    '''draw pseudo 3D grid'''
    
    # ************ setup ************
    rays_color_modes = [
        (255, 30, 30),      # blue
        (30, 255, 30),      # green
        (30, 30, 255),      # red
        (255, 255, 30),     # blue-green
        (30, 255, 255),     # green-red
        (255, 30, 255),     # blue-red
        (30, 30, 30),       # black
        (180, 180, 180),    # white
        (50, 100, 150),     # some
        (150, 50, 100),     # thing
        ]
        
    color = rays_color_modes[color_mode]
    height, width = img.shape[:2]
    
    
    # ************ draw walls ************
    if walls:
        p_center = center
        p_left_up = (0, 0)
        p_right_up = (width-1, 0)
        p_left_down = (0, height-1)
        p_right_down = (width-1, height-1)
        
        # walls up down
        wall_up_color = (30, 30, 30)
        wall_up = np.array([p_left_up, p_right_up, p_center])
        wall_down = np.array([p_left_down, p_right_down, p_center])
        cv2.drawContours(img, [wall_up], 0, wall_up_color, -1)
        cv2.drawContours(img, [wall_down], 0, wall_up_color, -1)
        
        # walls left, right
        wall_down_color = (40, 40, 40)
        wall_left = np.array([p_left_up, p_left_down, p_center])
        wall_right = np.array([p_right_up, p_right_down, p_center])
        cv2.drawContours(img, [wall_left], 0, wall_down_color, -1)
        cv2.drawContours(img, [wall_right], 0, wall_down_color, -1)
    
    
    # ************ draw star lines ************
    lines_number = 10
    step_x = width/lines_number
    step_y = height/lines_number
    points_top = [(round(step_x*x), 0) for x in range(lines_number+1)]
    points_bottom = [(round(step_x*x), height-1) for x in range(lines_number+1)]
    points_left = [(0, round(step_y*x)) for x in range(lines_number+1)]
    points_right = [(width-1, round(step_y*x)) for x in range(lines_number+1)]
    points = list(set(points_top + points_bottom + points_left + points_right))
    
    for point in points:
        cv2.line(img, (point), (center), color, 1, cv2.LINE_AA)     # ANTIALIASED LINE
        
    return None
    
    
def generate_squares(width, height, center, divider, number):
    '''generate squares'''
    half_width_left, half_height_top = center
    half_height_bot = height - half_height_top
    half_width_right = width - half_width_left
    
    # horizontal lines with golden division
    horizontal_points = []
    for x in range(1, number+1):
        line_step_top = round(half_height_top/(divider**x))
        line_step_bot = round(half_height_bot/(divider**x))
        top_pos = (half_height_top - line_step_top)
        bot_pos = (half_height_top + line_step_bot)
        horizontal_points.append(top_pos)
        horizontal_points.append(bot_pos)
        
    # vertical lines with golden division
    vertical_points = []
    for x in range(1, number+1):
        line_step_left = round(half_width_left/(divider**x))
        line_step_right = round(half_width_right/(divider**x))
        left_pos = (half_width_left - line_step_left)
        right_pos = (half_width_left + line_step_right)
        vertical_points.append(left_pos)
        vertical_points.append(right_pos)
        
    # math first and last points and draw square; continue by going to center
    horizontal_points = sorted(horizontal_points)
    vertical_points = sorted(vertical_points)
    diagonal_points = list(zip(vertical_points, horizontal_points))
    start_square = diagonal_points[:len(diagonal_points)//2]
    stop_square = diagonal_points[len(diagonal_points)//2:][::-1]
    square_points = list(zip(start_square, stop_square))
    return square_points
    
    
def draw_squares(img, center, sequence, color_mode):
    '''this functions is derivative from draw_grid; it draws squares only (including light square)'''
    if not sequence:
        return None
        
    # ************ draw squares ************
    rectangle_color_modes = [
        (255, 100, 100),    # blue
        (100, 255, 100),    # green
        (100, 100, 255),    # red
        (255, 255, 100),    # blue-green
        (100, 255, 255),    # green-red
        (255, 100, 255),    # blue-red
        (40, 40, 40),       # black
        (220, 220, 220),    # white
        (100, 150, 200),    # some
        (200, 100, 150),    # thing
        ]
        
    height, width = img.shape[:2]
    squares_color = rectangle_color_modes[color_mode]
    highlight_square_color = (squares_color[0]-20, squares_color[1]-80, squares_color[2]-80)
    
    depth = len(sequence) - 1
    phi = (1 + 5 ** 0.5) / 2
    square_points = generate_squares(width, height, center, phi, depth)
    main_square = [((+1, +1), (width-2, height-2))]
    squares = main_square + square_points
    squares = squares[::-1]
    
    total_squares = len(squares)
    for key, (p1, p2) in enumerate(squares):
        light_mode = sequence[key]
        if light_mode:
            # line_thickness calculated based on hyperbole_values
            line_thickness = math.ceil(7/(2 + total_squares - (key + 1)))
            img = cv2.rectangle(img, p1, p2, squares_color, line_thickness)
        else:
            img = cv2.rectangle(img, p1, p2, highlight_square_color, 1)
    return None
    
    
def update_points(img, points, center, show=True, freeze=False, gravity=0, remove_outer_only=False):
    '''update points position refer to center; draw points
    IMPORTANT THING - do not store rounded values of points positions
    store float and round before drawing
    '''
    points = sorted(points, key=lambda x: x[3][2])
    
    # extract values
    height, width = img.shape[:2]
    center_x, center_y = center
    center_x_coeff = (center_x/width)/4 + 0.75
    
    points_update = []
    for key, point in enumerate(points):
        point_pos, point_speed, point_color, point_3d = point
        point_pos_round = (round(point_pos[0]), round(point_pos[1]))
        
        # ***** calc point radius; draw point *****
        # calc radius by z-value
        point_3d_x, point_3d_y, point_3d_z = point_3d
        if show:
            radius = max(round(8*point_3d_z), 0)        # 0 vs 1
            calculated_point_color = tuple(center_x_coeff * item for item in point_color)
            cv2.circle(img, point_pos_round, radius, calculated_point_color, -1)
            cv2.circle(img, point_pos_round, radius, calculated_point_color, -1, lineType=cv2.LINE_AA)  # antialiased; it cause small parts will disappear
            
            
        # ***** calc point position (3d) *****
        # 1) calc window start
        window_start_x = center_x*(1 - point_3d_z)
        window_start_y = center_y*(1 - point_3d_z)
        
        # 2) calc window shape
        window_width = width*point_3d_z
        window_height = height*point_3d_z
        
        # 3) x, y true position; do not round values here
        point_pos_x = window_start_x + point_3d_x * window_width
        point_pos_y = window_start_y + point_3d_y * window_height
        
        
        # update position
        if not freeze:
            # point_3d_z += point_speed
            point_3d_z += point_3d_z*point_speed        # it compensate distance
            
            
        # ***** gravity stuff *****
        gravity_speed = 0.01
        
        if gravity > 0:
            point_3d_y += gravity_speed
            if point_3d_y > 1:
                point_3d_y = 1
                
                
        if gravity < 0:
            point_3d_y -= gravity_speed
            if point_3d_y < 0:
                point_3d_y = 0
                
                
        # ***** remove points *****
        cut_off_low_level = 0.003
        if remove_outer_only:
            if point_3d_z < cut_off_low_level:
                continue
                
            # remove points by screen position; it doesnt work fine
            if not (0 <= point_pos[0] <= width) or not (0 <= point_pos[1] <= height):
                continue
        else:
            # remove points by z-value
            if not (cut_off_low_level <= point_3d_z <= 1):
                continue
                
        point_3d = (point_3d_x, point_3d_y, point_3d_z)
        point_pos = (point_pos_x, point_pos_y)
        points_update.append((point_pos, point_speed, point_color, point_3d))
        
    points = points_update
    return points
    
    
def generate_points(width, height, center, number):
    '''generate points'''
    center_x, center_y = center
    
    points = []
    for x in range(number):
        # it affects points direction
        point_pos = (random.randrange(width), random.randrange(height))
        
        # 3d position
        point_3d_x = point_pos[0]/width
        point_3d_y = point_pos[1]/height
        point_3d_z = 0.003       # close to center (0 - inside center)
        point_3d = (point_3d_x, point_3d_y, point_3d_z)
        
        # ***** (update init position) calc point position (3d) *****
        # 1) calc window start
        window_start_x = center_x*(1 - point_3d_z)
        window_start_y = center_y*(1 - point_3d_z)
        
        # 2) calc window shape
        window_width = width*point_3d_z
        window_height = height*point_3d_z
        
        # 3) x, y true position; do not round values here
        point_pos_x = window_start_x + point_3d_x * window_width
        point_pos_y = window_start_y + point_3d_y * window_height
        
        # it lets to avoid first occur out of center (anywhere on the screen)
        point_pos = (point_pos_x, point_pos_y)
        
        
        # speed near to zero may cause, some points stuck inside
        point_speed = random.randrange(2, 100)/1000
        point_color = (random.randrange(80, 140),)*3        # grey
        # point_color = (random.randrange(40, 70), random.randrange(40, 70), random.randrange(200, 255),)        # red
        points.append((point_pos, point_speed, point_color, point_3d))
    return points
    
    
def generate_single_bullet(width, height, bullet_pos, variable):
    '''generate bullets'''
    # 3d position
    bullet_3d_x = bullet_pos[0]/width
    bullet_3d_y = bullet_pos[1]/height
    bullet_3d_z = 1     # on the surface
    bullet_3d = (bullet_3d_x, bullet_3d_y, bullet_3d_z)
    
    if variable:
        # variable bullets speed
        bullet_speed = -(random.randrange(5, 100)/10000)
    else:
        bullet_speed = -0.005
        
    bullet_color = (random.randrange(50), random.randrange(150, 255), random.randrange(50))
    bullet = (bullet_pos, bullet_speed, bullet_color, bullet_3d)
    return bullet
    
    
def main(height=1080, width=1920, points_number=180, fullscreen=True):
    '''interactive grid main function'''
    # ******* general setup *******
    # fullscreen=True                 # outside
    freeze = False                  # inside
    show_grid = True                # inside
    show_points = True              # inside
    show_bullets = True             # inside
    show_walls = True               # inside
    remove_outer_only = False       # inside; store points which reached z-value 1 or more
    variable_bullets_speed = False  # inside
    color_mode = 5                  # inside
    gravity = 0                     # inside
    
    
    # ******* image shape *******
    # height, width = (1080, 1920)    # outside
    center_x, center_y = (width//2, height//2)
    center = (center_x, center_y)
    
    
    # ******* bullets, points & squares setup *******
    bullets = []
    squares_seq = SquaresSequence()
    points = []
    points = generate_points(width, height, center, points_number)
    
    
    # ******* window setup *******
    window_title = 'img'
    if fullscreen:
        cv2.namedWindow(window_title, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
        cv2.namedWindow(window_title)
        
        
    # ******* mouse events *******
    handler = MouseHandler(height, width)
    cv2.setMouseCallback(window_title, handler.handle_event)
    
    
    # ******* init last time *******
    last_time = time.time()
    
    
    # ******* main loop *******
    while True:
        # which is faster - painting black or creating blank img everytime?
        img = blank_image(height, width, layers=3, value=0)
        
        # ******* map keyboard events *******
        code = cv2.waitKey(1) & 0xFF
        if code != 255:
            char = chr(code)
            
            if char == 'q':
                # break loop, close window and quit from main
                break
                
            elif char == '-':
                # set depth
                squares_seq.depth_decrease()
                
            elif char == '+':
                # set depth
                squares_seq.depth_increase()
                
            elif char == 'c':
                # remove bullets & points
                bullets = []
                points = []
                
            elif char == 'f':
                freeze = not freeze
                print('freeze: {}'.format(freeze))
                
            elif char == 'g':
                show_grid = not show_grid
                
            elif char in [str(x) for x in range(10)]:
                # change color mode
                color_mode = int(char)
                
            elif char == 'p':
                show_points = not show_points
                
            elif char == 'b':
                show_bullets = not show_bullets
                
            elif char == 'v':
                variable_bullets_speed = not variable_bullets_speed
                print('variable_bullets_speed: {}'.format(variable_bullets_speed))
                
            elif char == 'w':
                show_walls = not show_walls
                
            elif char == 's':
                # increase number of light squares
                squares_seq.mode_up()
                
            elif char == 'x':
                # increase light squares speed
                squares_seq.speed_up()
                
            elif char == 'd':
                # move pieces down; gravity turn on
                if gravity < 0:
                    gravity = 0
                else:
                    gravity = 1
                    print('gravity: down')
                
            elif char == 'u':
                # move pieces up; antigravity turn on
                if gravity > 0:
                    gravity = 0
                else:
                    gravity = -1
                    print('gravity: up')
                    
        # ******* map mopuse values *******
        center_x = handler.center_x
        center_y = handler.center_y
        cursor_x = handler.cursor_x
        cursor_y = handler.cursor_y
        center = (center_x, center_y)
        
        
        # ******* update sequence *******
        if not freeze:
            squares_seq.count()
            
            
        # ******* draw grid *******
        if show_grid:
            counter = 1
            draw_grid(img, center, color_mode, show_walls)
            sequence = squares_seq.sequence
            # print(sequence)
            draw_squares(img, center, sequence, color_mode)
            
            
        # ******* create new bullets *******
        if handler.shoot:
            bullet = generate_single_bullet(width, height, (cursor_x, cursor_y), variable_bullets_speed)
            bullets.append(bullet)
            
            
        # ******* update & draw bullets *******
        bullets = update_points(img, bullets, center, show_bullets, freeze, gravity)
        
        
        # ******* update & draw points *******
        points = update_points(img, points, center, show_points, freeze, gravity, remove_outer_only)
        new_points = generate_points(width, height, center, points_number-len(points))
        points.extend(new_points)   # keep number of points fixed
        
        
        # ******* calc time to wait *******
        # set upper limit for fps (~30); in most cases it will be much lower :|
        elapsed = time.time() - last_time
        fixed_time = 0.03333333333333333
        if elapsed < fixed_time:
            # print('wait: {}'.format(fixed_time-elapsed))
            time.sleep(fixed_time-elapsed)
        last_time = time.time()
        
        
        # ******* show image *******
        cv2.imshow(window_title, img)
        
        
    # ******* CLEANUP *******
    cv2.destroyAllWindows()
    return None
    
    
def usage():
    '''mouse and keyboard actions'''
    print('''interactive grid usage content
    \r------------------------------
    \rmouse actions:
    \r    left mouse button press               - draw bullets
    \r    mouse center hold with mouse moves    - move grid center
    \r
    \rkeyboard actions:
    \r    g     - hide/show grid
    \r    f     - freeze points & bullets
    \r    c     - remove all visible pieces
    \r    p     - hide/show points
    \r    b     - hide/show bullets
    \r    d     - gravity down
    \r    u     - gravity up
    \r    v     - variable/fixed bullets speed
    \r    w     - hide/show walls
    \r    s     - switch light square modes
    \r    x     - squares speed up
    \r    +     - increase squares depth
    \r    -     - decrease squares depth
    \r    q     - quit from grid
    \r------------------------------
    ''')
    return None
    
    
if __name__ == "__main__":
    usage()
    main(height=1080, width=1920, points_number=180, fullscreen=True)
