"""
ColabTurtlePlus — Canvas-based turtle graphics for Pyodide
Drop-in compatible with standard turtle / ColabTurtlePlus API.
Renders to two stacked HTML canvases:
  #turtle-canvas  — persistent drawing surface
  #turtle-cursor  — turtle sprite overlay (cleared & redrawn each move)
"""
import js
import math

# ──────────────────────────────────────────────────────────────
# Module-level state
# ──────────────────────────────────────────────────────────────
_x = 0.0
_y = 0.0
_heading   = 0.0    # degrees; 0 = East, 90 = North  (standard turtle)
_pen_down  = True
_pen_color = '#1e293b'
_fill_color= '#1e293b'
_pen_width = 2
_visible   = True
_canvas_w  = 900
_canvas_h  = 600
_fill_path = None   # None = not filling; list of (x,y) when filling

_draw_ctx  = None   # cached 2D context for drawing canvas
_cur_ctx   = None   # cached 2D context for cursor canvas


def _dc():
    global _draw_ctx
    if _draw_ctx is None:
        _draw_ctx = js.document.getElementById('turtle-canvas').getContext('2d')
    return _draw_ctx


def _cc():
    global _cur_ctx
    if _cur_ctx is None:
        _cur_ctx = js.document.getElementById('turtle-cursor').getContext('2d')
    return _cur_ctx


def _to_canvas(tx, ty):
    """Turtle coords → canvas pixel coords."""
    return _canvas_w / 2 + tx, _canvas_h / 2 - ty


def _update_cursor():
    """Redraw the turtle sprite on the cursor canvas."""
    ctx = _cc()
    ctx.clearRect(0, 0, _canvas_w, _canvas_h)
    if not _visible:
        return
    cx, cy = _to_canvas(_x, _y)
    a = math.radians(_heading)
    size = 16

    # Tip of triangle (points in heading direction)
    fx = cx + size * math.cos(a)
    fy = cy - size * math.sin(a)

    # Left & right base corners
    la = a + math.radians(145)
    ra = a - math.radians(145)
    lx = cx + size * 0.65 * math.cos(la)
    ly = cy - size * 0.65 * math.sin(la)
    rx = cx + size * 0.65 * math.cos(ra)
    ry = cy - size * 0.65 * math.sin(ra)

    ctx.beginPath()
    ctx.moveTo(fx, fy)
    ctx.lineTo(lx, ly)
    ctx.lineTo(rx, ry)
    ctx.closePath()
    ctx.fillStyle = '#22c55e'
    ctx.fill()
    ctx.strokeStyle = '#14532d'
    ctx.lineWidth = 2
    ctx.stroke()


# ──────────────────────────────────────────────────────────────
# Canvas / window setup
# ──────────────────────────────────────────────────────────────

def setup(width=900, height=600, **kwargs):
    """Set canvas size and paint white background."""
    global _canvas_w, _canvas_h, _draw_ctx, _cur_ctx
    _canvas_w, _canvas_h = width, height
    _draw_ctx = _cur_ctx = None          # reset cached contexts
    for cid in ('turtle-canvas', 'turtle-cursor'):
        el = js.document.getElementById(cid)
        el.width  = width
        el.height = height
    ctx = _dc()
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, width, height)


def showborder():
    ctx = _dc()
    ctx.strokeStyle = '#94a3b8'
    ctx.lineWidth = 2
    ctx.strokeRect(1, 1, _canvas_w - 2, _canvas_h - 2)


def bgcolor(color):
    ctx = _dc()
    ctx.fillStyle = color
    ctx.fillRect(0, 0, _canvas_w, _canvas_h)


# ──────────────────────────────────────────────────────────────
# Drawing controls
# ──────────────────────────────────────────────────────────────

def speed(s):
    pass  # all drawing is instant on canvas


def hideturtle():
    global _visible
    _visible = False
    _update_cursor()


def showturtle():
    global _visible
    _visible = True
    _update_cursor()


ht = hideturtle
st = showturtle


def penup():
    global _pen_down
    _pen_down = False


def pendown():
    global _pen_down
    _pen_down = True


pu = penup
pd = pendown
up = penup
down = pendown


def pencolor(*args):
    global _pen_color
    if len(args) == 1:
        _pen_color = args[0]
    elif len(args) == 3:
        r, g, b = args
        _pen_color = f'rgb({int(r*255)},{int(g*255)},{int(b*255)})'


def fillcolor(*args):
    global _fill_color
    if len(args) == 1:
        _fill_color = args[0]
    elif len(args) == 3:
        r, g, b = args
        _fill_color = f'rgb({int(r*255)},{int(g*255)},{int(b*255)})'


def color(*args):
    if len(args) == 1:
        pencolor(args[0])
        fillcolor(args[0])
    elif len(args) == 2:
        pencolor(args[0])
        fillcolor(args[1])


def pensize(w):
    global _pen_width
    _pen_width = w


width = pensize


# ──────────────────────────────────────────────────────────────
# Movement
# ──────────────────────────────────────────────────────────────

def _line_to(x2, y2):
    global _x, _y
    if _fill_path is not None:
        _fill_path.append((x2, y2))
    if _pen_down:
        ctx = _dc()
        x1c, y1c = _to_canvas(_x, _y)
        x2c, y2c = _to_canvas(x2, y2)
        ctx.beginPath()
        ctx.strokeStyle = _pen_color
        ctx.lineWidth = _pen_width
        ctx.lineCap = 'round'
        ctx.lineJoin = 'round'
        ctx.moveTo(x1c, y1c)
        ctx.lineTo(x2c, y2c)
        ctx.stroke()
    _x = x2
    _y = y2


def goto(x, y=None):
    if y is None:
        x, y = x[0], x[1]
    _line_to(float(x), float(y))
    _update_cursor()


setpos      = goto
setposition = goto


def forward(distance):
    a  = math.radians(_heading)
    nx = _x + distance * math.cos(a)
    ny = _y + distance * math.sin(a)
    _line_to(nx, ny)
    _update_cursor()


fd = forward


def backward(distance):
    forward(-distance)


bk   = backward
back = backward


def left(angle):
    global _heading
    _heading = (_heading + angle) % 360
    _update_cursor()


lt = left


def right(angle):
    global _heading
    _heading = (_heading - angle) % 360
    _update_cursor()


rt = right


def setheading(angle):
    global _heading
    _heading = float(angle) % 360
    _update_cursor()


seth = setheading


def home():
    global _heading
    _line_to(0.0, 0.0)
    _heading = 0.0
    _update_cursor()


# ──────────────────────────────────────────────────────────────
# Queries
# ──────────────────────────────────────────────────────────────

def pos():
    return (_x, _y)


def position():
    return pos()


def xcor():
    return _x


def ycor():
    return _y


def heading():
    return _heading


def distance(x, y=None):
    if y is None:
        ox, oy = x
    else:
        ox, oy = x, y
    return math.sqrt((_x - ox) ** 2 + (_y - oy) ** 2)


# ──────────────────────────────────────────────────────────────
# Shapes
# ──────────────────────────────────────────────────────────────

def circle(radius, extent=360, steps=None):
    if radius == 0:
        return
    if steps is None:
        steps = max(int(abs(extent) / 4), 12)
    step_angle = extent / steps
    step_len   = 2 * math.pi * abs(radius) * abs(extent) / 360 / steps
    for _ in range(steps):
        forward(step_len)
        if radius > 0:
            left(step_angle)
        else:
            right(step_angle)


def dot(size=None, color=None):
    sz = size if size is not None else max(_pen_width + 4, 2 * _pen_width)
    c  = color if color is not None else _pen_color
    ctx = _dc()
    cx, cy = _to_canvas(_x, _y)
    ctx.beginPath()
    ctx.arc(cx, cy, sz / 2, 0, 2 * math.pi)
    ctx.fillStyle = c
    ctx.fill()


def begin_fill():
    global _fill_path
    _fill_path = [(_x, _y)]


def end_fill():
    global _fill_path
    if not _fill_path:
        return
    ctx = _dc()
    ctx.beginPath()
    x0c, y0c = _to_canvas(_fill_path[0][0], _fill_path[0][1])
    ctx.moveTo(x0c, y0c)
    for px, py in _fill_path[1:]:
        pxc, pyc = _to_canvas(px, py)
        ctx.lineTo(pxc, pyc)
    xc, yc = _to_canvas(_x, _y)
    ctx.lineTo(xc, yc)
    ctx.closePath()
    ctx.fillStyle = _fill_color
    ctx.fill()
    _fill_path = None


def write(text, move=False, align='left', font=None):
    ctx = _dc()
    cx, cy = _to_canvas(_x, _y)
    sz = font[1] if font and len(font) >= 2 and isinstance(font[1], int) else 14
    ctx.font = f'bold {sz}px Nunito, sans-serif'
    ctx.fillStyle = _pen_color
    ctx.textBaseline = 'bottom'
    ctx.fillText(str(text), cx, cy)


# ──────────────────────────────────────────────────────────────
# Screen management
# ──────────────────────────────────────────────────────────────

def clearscreen():
    ctx = _dc()
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, _canvas_w, _canvas_h)


def reset():
    global _x, _y, _heading, _pen_down, _pen_color, _fill_color
    global _pen_width, _visible, _fill_path
    _x = _y = 0.0
    _heading   = 0.0
    _pen_down  = True
    _pen_color = '#1e293b'
    _fill_color= '#1e293b'
    _pen_width = 2
    _visible   = True
    _fill_path = None
    clearscreen()
    _update_cursor()


def done():
    pass   # no-op; present for API compatibility


def window_width():
    return _canvas_w


def window_height():
    return _canvas_h
