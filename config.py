import os

vars = {"path": "data/kicount_old_middleJuly.csv",
        "model_path": "models/",
        "img_path": "images/",
        "mins": 24 * 60,
        "minimum": 0,
        "maximum": 350,
        "opening": 9,
        "closing": 22}

if not os.path.exists(vars["model_path"]):
        print("Creating model path.")
        os.mkdir(vars["model_path"])

if not os.path.exists(vars["img_path"]):
        print("Creating image path.")
        os.mkdir(vars["img_path"])
