from fastai.vision import *
from io import BytesIO
from typing import List, Dict, Union, ByteString
import requests


def load_model(path=".", file="classifier.pkl"):
    learn = load_learner(path, file=file)
    return learn


def load_image_url(url: str) -> Image:
    response = requests.get(url)
    img = open_image(BytesIO(response.content))
    return img


def load_image_bytes(raw_bytes: ByteString) -> Image:
    img = open_image(BytesIO(raw_bytes))
    return img


def classifier_predict(img, n: int = 3) -> Dict[str, Union[str, List]]:
    model = load_model('models')
    pred_class, _, outputs = model.predict(img)
    pred_probs = outputs / sum(outputs)
    pred_probs = pred_probs.tolist()
    predictions = []
    for image_class, prob in zip(model.data.classes, pred_probs):
        prob = round(prob*100, 2)
        predictions.append(
            {"class": image_class.replace(
                "_", " "), "prob": prob}
        )

    predictions.sort(key=lambda x: x["prob"], reverse=True)
    predictions = [{**i, 'prob': str(i['prob']) + '%'} for i in predictions][:n]
    return {"signal": 1, "class": str(pred_class), "predictions": predictions}


def segmentation_predict(img) -> Dict[str, Union[str, List]]:
    model = load_model('models', file="segmentation.pkl")
    pred = model.predict(img)[0]
    pred.show(figsize=(480 / 50, 360 / 50), alpha=1)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.savefig('tmp.png', dpi=100)
    import base64
    with open('tmp.png', 'rb') as img_f:
        img_stream = base64.b64encode(img_f.read()).decode()
    return {"signal": 2, "img_stream": img_stream}


def void_code():
    codes = np.array(
        ['Animal', 'Archway', 'Bicyclist', 'Bridge', 'Building', 'Car', 'CartLuggagePram', 'Child', 'Column_Pole',
         'Fence', 'LaneMkgsDriv', 'LaneMkgsNonDriv', 'Misc_Text', 'MotorcycleScooter', 'OtherMoving', 'ParkingBlock',
         'Pedestrian', 'Road', 'RoadShoulder', 'Sidewalk', 'SignSymbol', 'Sky', 'SUVPickupTruck', 'TrafficCone',
         'TrafficLight', 'Train', 'Tree', 'Truck_Bus', 'Tunnel', 'VegetationMisc', 'Void', 'Wall'
         ], dtype='<U17')
    name2id = {v: k for k, v in enumerate(codes)}
    void_code = name2id['Void']
    return void_code


def acc_camvid(input, target):
    target = target.squeeze(1)
    mask = target != void_code
    return (input.argmax(dim=1)[mask] == target[mask]).float().mean()
