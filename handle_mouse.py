import cv2


class MouseHandler():
    def __init__(self, max_height, max_width):
        self.max_height = max_height
        self.max_width = max_width
        self.center_y = max_height//2
        self.center_x = max_width//2
        self.cursor_y = max_height//2
        self.cursor_x = max_width//2
        self.move_center = False    # move center, using mouse (press and hold scroll)
        self.move_center_outside = False    # flag for allowing to move center outside window; not in use for now
        self.last_event = None
        self.shoot = False
        
    def limit_number(self, number, low_limit, high_limit):
        '''limit number, to specified bounds'''
        if number < low_limit:
            return low_limit
            
        if number > high_limit:
            return high_limit
            
        return number
        
        
    def handle_event(self, event, x, y, flags, param):
        '''
        opencv events list:
            EVENT_FLAG_ALTKEY
            EVENT_FLAG_CTRLKEY
            EVENT_FLAG_LBUTTON
            EVENT_FLAG_MBUTTON
            EVENT_FLAG_RBUTTON
            EVENT_FLAG_SHIFTKEY
            EVENT_LBUTTONDBLCLK
            EVENT_LBUTTONDOWN
            EVENT_LBUTTONUP
            EVENT_MBUTTONDBLCLK
            EVENT_MBUTTONDOWN
            EVENT_MBUTTONUP
            EVENT_MOUSEHWHEEL
            EVENT_MOUSEMOVE
            EVENT_MOUSEWHEEL
            EVENT_RBUTTONDBLCLK
            EVENT_RBUTTONDOWN
            EVENT_RBUTTONUP
        '''
        if event != 0:
            # print('event: {}'.format(event))
            pass
            
        if event == cv2.EVENT_LBUTTONDOWN:  # 1
            # shoot her; press left mouse button
            self.shoot = True
            
        if event == cv2.EVENT_LBUTTONUP:
            # left button release
            self.shoot = False
            
        if event == cv2.EVENT_MBUTTONDOWN:  # 3
            # press and hold scroll button; move center active
            self.move_center = True
            
        if event == cv2.EVENT_MBUTTONUP:    # 6
            # release scroll button; move center is inactive
            self.move_center = False
            
        if self.move_center:
            # print(x, y)
            if (0 <= x <= self.max_width) and not self.move_center_outside:
                self.center_x = x
                
            if (0 <= y <= self.max_height) and not self.move_center_outside:
                self.center_y = y
                
        # store current cursor position
        self.cursor_x = self.limit_number(x, 0, self.max_width)
        self.cursor_y = self.limit_number(y, 0, self.max_height)
        
        
if __name__ == "__main__":
    pass
