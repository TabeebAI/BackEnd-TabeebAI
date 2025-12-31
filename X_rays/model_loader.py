import os
import torch
import torchvision.models as models
import numpy as np

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = r"C:\Users\PC User\Desktop\BackEnd-TabeebAI\X_rays\best_mura_resnet5_gpu.pth"

def load_model():
    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ Model file not found: {MODEL_PATH}")
        return None
    model = models.resnet50(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, 1)
    torch.serialization.add_safe_globals([
        np.dtype,
        np.ndarray,
        np._core.multiarray.scalar
    ])

    try:
        checkpoint = torch.load(
            MODEL_PATH,
            map_location=DEVICE,
            weights_only=False 
        )
        if "model_state" in checkpoint:
            state_dict = checkpoint["model_state"]
        elif "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            raise ValueError("No model_state found in checkpoint")
        model.load_state_dict(state_dict)
        model.to(DEVICE)
        model.eval()
        print(f"✅ Model loaded successfully from: {MODEL_PATH}")
        return model

    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return None
