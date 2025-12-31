import torch
from rest_framework.decorators import api_view
from rest_framework.response import Response
from PIL import Image

from .model_loader import load_model, DEVICE
from .transforms import image_transform

model = load_model()

@api_view(["POST"])
def predict_mura(request):
    if model is None:
        return Response({"error": "Model not loaded. best_mura_resnet5_gpu.pth is missing or failed to load"},
                        status=500)

    if "image" not in request.FILES:
        return Response({"error": "No image provided"}, status=400)

    try:
        image = Image.open(request.FILES["image"]).convert("RGB")
        image = image_transform(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            output = model(image)
            prob = torch.sigmoid(output).item()

        return Response({
            "fracture_probability": round(prob, 3),
            "prediction": "Fracture" if prob > 0.4 else "Normal"
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)
