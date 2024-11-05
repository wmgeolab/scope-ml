# app/dependencies.py
from fastapi import Depends, Request
from .config import Settings
from .types import AutoscalerState
from .kubernetes import KubeCommand
from .vllm import VLLMManager


def get_settings() -> Settings:
    return Settings()


def get_state(request: Request) -> AutoscalerState:
    return request.app.state.state


def get_kube(settings: Settings = Depends(get_settings)) -> KubeCommand:
    return KubeCommand(settings)


def get_vllm_manager(
    settings: Settings = Depends(get_settings),
    state: AutoscalerState = Depends(get_state),
    kube: KubeCommand = Depends(get_kube),
) -> VLLMManager:
    return VLLMManager(settings, state, kube)
