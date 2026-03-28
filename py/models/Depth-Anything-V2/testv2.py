from transformers import pipeline
import matplotlib.pyplot as plt
from PIL import Image

pipe = pipeline(
    task="depth-estimation",
    model="depth-anything/Depth-Anything-V2-Metric-Indoor-Base-hf",
)
image = Image.open("../data/sample2.png")
depth = pipe(image)["depth"]

plt.imshow(depth)
plt.show()
