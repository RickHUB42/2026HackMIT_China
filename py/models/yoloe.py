from ultralytics import YOLOE  # pyright: ignore
from ultralytics.models.yolo.yoloe import YOLOEVPDetectPredictor

model = YOLOE("./data/yoloE/yoloe-11l-seg.pt")


def segment(image, classes):
    model.set_classes(classes)
    results = model.predict(image, conf=0.008, verbose=False)
    return results[0]


if __name__ == "__main__":
    # model = YOLOE("./data/yoloE/yoloe-v8l-seg.pt")

    from visionllm import find_food

    # img_path = "./data/sample.png"
    img_path = "./data/sample3.png"

    # foodlist = find_food(img_path)
    foodlist = ["one chicken", "potato", "cherry tomato", "one arugula", "one parsley"]

    model.set_classes(["plate"] + foodlist)
    # results = model.predict(img_path, conf=0.008)
    results = model.predict(img_path, conf=0.008)
    results[0].save("./temp.png", boxes=False)
    results[0].save("./temp2.png")
    results[0].show(boxes=False)
    input()
