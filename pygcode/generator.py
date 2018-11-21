class GCodeGen:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.x0 = 0
        self.y0 = 0
        self.z0 = 0
        self.safe_z = 5
        self.tool_d = 6
        self.step_file_path = "test.gcode"
        self.mill_speed = 200
        self.free_speed = 1000
        self.max_depth_per_pass = 0.1
        self.current_content = ""
        self.spindle_speed = 5000
    
    def set(self, **params):
        for k, v in params.items():
            try:
                setattr(self, k, v)
            except:
                print("param", k, " is unsupported")
                continue

    def start_step(self, filepath):
        self.step_file_path = filepath
        self.current_content = "%\r\n"
        self.g("G21G64G17")
        self.g("G90")
        self.g("G0 Z%f", (self.safe_z))
        self.g("G0 X%f Y%f Z%f", (self.x0, self.y0, self.z0))
        self.g("M3 S%f", (self.spindle_speed))
        self.g("G1 F%f", (self.mill_speed))

    def end_step(self):
        self.g("G0 Z%f", (self.safe_z))
        self.g("M5")
        self.g("M30")
        f = open(self.step_file_path, "w")
        f.write(self.current_content)
        f.close()
        self.current_content = ""

    def g(self, templ, params=None):
        if params:
            self.current_content += (templ+"\r\n") % params
        else:
            self.current_content += templ+"\r\n"

    def spiral_hole(self, x=0, y=0, z=0, d=0, depth=0):
        r = d/2.0 - self.tool_d/2.0
        self.g("G1 X%.3f Z%.3f F%.3f", (x - r, z, self.free_speed))
        self.g("G1 F%.3f", (self.mill_speed))
        cur_depth = 0.0
        cur_sign = 1
        while cur_depth <= depth:
            self.g("G3 X%.3f Y%.3f Z%.3f R%.3f", (x+cur_sign*r, y, z-cur_depth, r))
            cur_depth += self.max_depth_per_pass
            cur_sign *= -1
        self.g("G3 X%.3f Y%.3f Z%.3f R%.3f", (x+cur_sign*r, y, z-depth, r))
        cur_sign *= -1
        self.g("G3 X%.3f Y%.3f Z%.3f R%.3f", (x+cur_sign*r, y, z-depth, r))

    def plane(self, xc=30, yc=30, zc=0, xdim=10, ydim=10, overlapping=0.3):
        xdim -= self.tool_d
        ydim -= self.tool_d
        self.g("G1 X%.3f Y%.3f Z%.3f F%.3f", (xc-xdim/2.0, yc-ydim/2.0, zc, self.free_speed))
        self.g("G1 F%.3f", (self.mill_speed))
        cur_y = yc - ydim/2.0
        cur_sign = 1
        while cur_y <= yc + ydim/2.0:
            self.g("G1 X%.3f", (xc + xdim/2.0*cur_sign, ))
            cur_y += self.tool_d*(1-overlapping)
            if cur_y <= yc + ydim/2.0:
                self.g("G1 Y%.3f", (cur_y, ))
            cur_sign *= -1
        self.g("G1 X%.3f Y%.3f", (xc + xdim/2.0*cur_sign, yc + ydim/2.0, ))
        
        self.g("G1 X%.3f Y%.3f", (xc - xdim/2.0, yc - ydim/2.0, ))
        self.g("G1 X%.3f Y%.3f", (xc + xdim/2.0, yc - ydim/2.0, ))
        self.g("G1 X%.3f Y%.3f", (xc + xdim/2.0, yc + ydim/2.0, ))
        self.g("G1 X%.3f Y%.3f", (xc - xdim/2.0, yc + ydim/2.0, ))
        self.g("G1 X%.3f Y%.3f", (xc - xdim/2.0, yc - ydim/2.0, ))

    def rect_vol(self, xc=30, yc=30, zc=0, xdim=10, ydim=10, depth=1, overlapping=0.3):
        cur_depth = 0.0
        while cur_depth <= depth:
            self.plane(xc, yc, zc-cur_depth, xdim, ydim, overlapping)
            cur_depth += self.max_depth_per_pass
        self.plane(xc, yc, zc-depth, xdim, ydim, overlapping)

    def rotate(self, angle):
        self.g("G0 A%.3f", (angle))

    def move_away(self, x, y):
        self.g("G0 Z%.3f", (self.safe_z))
        self.g("G0 X%.3f Y%.3f", (x, y))
