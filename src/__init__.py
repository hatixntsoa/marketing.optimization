"""
model_export package

Provides a unified interface to export trained machine learning models
to multiple formats across frameworks:
- scikit-learn
- PyTorch
- XGBoost
- LightGBM
- CatBoost
- TensorFlow/Keras

Usage:
    from model_export import export_model

    # Example:
    export_model(model, framework="sklearn", name="my_model")
"""

from .model_export import export_model

# Optional: define __all__ for clarity
__all__ = ["export_model"]

