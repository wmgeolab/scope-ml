# app/dependencies.py
from fastapi import Depends, Request

from .config import Settings
from .kubernetes import KubeCommand
from .manager import ServiceManager
from .types import AutoscalerState


def get_settings() -> Settings:
    return Settings()


def get_state(request: Request) -> AutoscalerState:
    return request.app.state.state


def get_kube(settings: Settings = Depends(get_settings)) -> KubeCommand:
    return KubeCommand(settings)


def get_service_manager(
    settings: Settings = Depends(get_settings),
    state: AutoscalerState = Depends(get_state),
    kube: KubeCommand = Depends(get_kube),
) -> ServiceManager:
    return ServiceManager(settings, state, kube)
