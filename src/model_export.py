"""
model_export.py

Utility functions to export trained machine learning models in multiple formats.

Supported model formats, usage, and typical platforms:

- Scikit-learn: 
    .pkl / .joblib / .bin
    -> Python-only serialization. Good for experiments and small projects.
       Platforms: Python environments on PC, server, or Raspberry Pi (CPU-only).

- PyTorch:
    .pt / .bin / .onnx
    -> .pt and .bin store model weights (TorchScript). 
       .onnx allows interoperability across frameworks, C++, mobile, and edge devices.
       Platforms: Python, C++ runtime, mobile apps (iOS/Android), edge devices supporting ONNX runtime.

- XGBoost:
    .bin / .json
    -> Native XGBoost formats for loading models in Python or other supported languages.
       Platforms: Python, C++, Java.

- LightGBM:
    .bin / .txt
    -> Native LightGBM formats for fast reloading and inference.
       Platforms: Python, C++, Java.

- CatBoost:
    .bin / .cbm
    -> CatBoost formats suitable for Python, C++, and Java inference engines.
       Platforms: Python, C++, Java.

- TensorFlow / Keras:
    .h5 / SavedModel / .tflite
    -> .h5 stores Keras models.
       SavedModel is TensorFlow’s standard format for serving.
       .tflite is optimized for deployment on mobile and IoT/edge devices.
       Platforms: Python, TensorFlow Serving, mobile (Android/iOS), microcontrollers (via TensorFlow Lite), Raspberry Pi.

Author: Hatix Ntsoa
"""

import os
import joblib
import torch
import onnx
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier
import tensorflow as tf

# Ensure models directory exists
os.makedirs("models", exist_ok=True)


# -------------------------------
# Scikit-learn Export
# -------------------------------
def export_sklearn_model(model, name="model"):
    """
    Export a scikit-learn model in .pkl, .joblib, and .bin formats.
    Platforms: Python on PC, server, or Raspberry Pi (CPU-only)
    """
    joblib.dump(model, f"models/{name}.pkl")
    joblib.dump(model, f"models/{name}.joblib")
    joblib.dump(model, f"models/{name}.bin")
    print(f"[INFO] Scikit-learn model exported as: {name}.pkl, {name}.joblib, {name}.bin")


# -------------------------------
# PyTorch Export
# -------------------------------
def export_pytorch_model(model, sample_input, name="model"):
    """
    Export a PyTorch model in .pt, .bin, and ONNX formats.
    Platforms: Python, C++, mobile apps (iOS/Android), edge devices supporting ONNX runtime
    sample_input: a torch.Tensor of appropriate shape for the model
    """
    # TorchScript / state_dict
    torch.save(model.state_dict(), f"models/{name}.pt")
    torch.save(model.state_dict(), f"models/{name}.bin")
    
    # Export to ONNX
    torch.onnx.export(model, sample_input, f"models/{name}.onnx",
                      export_params=True,
                      opset_version=12,
                      do_constant_folding=True)
    
    print(f"[INFO] PyTorch model exported as: {name}.pt, {name}.bin, {name}.onnx")


# -------------------------------
# XGBoost Export
# -------------------------------
def export_xgboost_model(model: xgb.Booster, name="model"):
    """
    Export an XGBoost model in .bin and .json formats.
    Platforms: Python, C++, Java
    """
    model.save_model(f"models/{name}.bin")
    model.save_model(f"models/{name}.json")
    print(f"[INFO] XGBoost model exported as: {name}.bin, {name}.json")


# -------------------------------
# LightGBM Export
# -------------------------------
def export_lightgbm_model(model: lgb.Booster, name="model"):
    """
    Export a LightGBM model in .bin and .txt formats.
    Platforms: Python, C++, Java
    """
    model.save_model(f"models/{name}.bin")
    model.save_model(f"models/{name}.txt")
    print(f"[INFO] LightGBM model exported as: {name}.bin, {name}.txt")


# -------------------------------
# CatBoost Export
# -------------------------------
def export_catboost_model(model: CatBoostClassifier, name="model"):
    """
    Export a CatBoost model in .bin and .cbm formats.
    Platforms: Python, C++, Java
    """
    model.save_model(f"models/{name}.bin")
    model.save_model(f"models/{name}.cbm")
    print(f"[INFO] CatBoost model exported as: {name}.bin, {name}.cbm")


# -------------------------------
# TensorFlow / Keras Export
# -------------------------------
def export_keras_model(model: tf.keras.Model, name="model"):
    """
    Export a Keras/TensorFlow model in .h5, SavedModel, and TFLite formats.
    Platforms: Python, TensorFlow Serving, mobile (Android/iOS), microcontrollers (TFLite), Raspberry Pi
    """
    # H5 format
    model.save(f"models/{name}.h5")
    
    # SavedModel format
    model.save(f"models/{name}_saved_model", save_format="tf")
    
    # TFLite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    with open(f"models/{name}.tflite", "wb") as f:
        f.write(tflite_model)
    
    print(f"[INFO] Keras model exported as: {name}.h5, {name}_saved_model/, {name}.tflite")


# -------------------------------
# Generic Export Function
# -------------------------------
def export_model(model, framework: str, **kwargs):
    """
    Generic function to export a model based on its framework.
    framework: "sklearn", "pytorch", "xgboost", "lightgbm", "catboost", "keras"
    kwargs: additional args like sample_input for PyTorch
    """
    framework = framework.lower()
    if framework == "sklearn":
        export_sklearn_model(model, **kwargs)
    elif framework == "pytorch":
        if "sample_input" not in kwargs:
            raise ValueError("PyTorch export requires 'sample_input' argument")
        export_pytorch_model(model, kwargs["sample_input"], **kwargs)
    elif framework == "xgboost":
        export_xgboost_model(model, **kwargs)
    elif framework == "lightgbm":
        export_lightgbm_model(model, **kwargs)
    elif framework == "catboost":
        export_catboost_model(model, **kwargs)
    elif framework == "keras":
        export_keras_model(model, **kwargs)
    else:
        raise ValueError(f"Unsupported framework: {framework}")

