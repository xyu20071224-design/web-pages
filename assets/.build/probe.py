
from PIL import Image
import numpy as np
D="/home/xinyan/桌面/html/assets/.build"
im = Image.open(f"{D}/r-v1-16.png").convert("RGB")
a = np.array(im)
print("shape",a.shape)
for y in range(16):
    row = a[y]
    s = "".join("." if row[x].sum()>150 else ("#" if row[x].sum()>20 else " ") for x in range(16))
    print(f"{y:2d} |{s}|")
# check clipping at x=0 and x=15
print("col0 max", a[:,0].max(), "col15 max", a[:,15].max())
