import numpy as np
import render

def fwd(d):
    return render.ship_forward(render.quat_look_along(d))

print('(0,0,-1):', np.round(fwd((0,0,-1)), 4))
print('(1,0,0):',  np.round(fwd((1,0,0)), 4))
print('(0,0,1):',  np.round(fwd((0,0,1)), 4))
print('(1,1,1):',  np.round(fwd((1,1,1)), 4))
print('(0,1,0):',  np.round(fwd((0,1,0)), 4))
print('no NaN for (0,1,0):', not np.any(np.isnan(render.quat_look_along((0,1,0)))))
