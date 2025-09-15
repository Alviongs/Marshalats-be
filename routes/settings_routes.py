from fastapi import APIRouter, Depends, status
from controllers.settings_controller import SettingsController
from models.settings_models import SystemSettingsFlatCreate, SystemSettingsFlatResponse
from models.user_models import UserRole
from utils.unified_auth import require_role_unified

router = APIRouter()

@router.get("", response_model=SystemSettingsFlatResponse)
async def get_system_settings(
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """
    Get current system settings
    
    - **Requires**: Super Admin authentication
    - **Returns**: Current system settings in flat format
    """
    return await SettingsController.get_settings(current_user)

@router.put("", response_model=SystemSettingsFlatResponse)
async def update_system_settings(
    settings_data: SystemSettingsFlatCreate,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """
    Update system settings
    
    - **Requires**: Super Admin authentication
    - **Body**: System settings data in flat format
    - **Returns**: Updated system settings
    """
    return await SettingsController.update_settings(settings_data, current_user)

@router.post("/reset", response_model=SystemSettingsFlatResponse)
async def reset_system_settings(
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """
    Reset system settings to default values
    
    - **Requires**: Super Admin authentication
    - **Returns**: Reset system settings with default values
    """
    return await SettingsController.reset_settings(current_user)

@router.get("/defaults", response_model=dict)
async def get_default_settings(
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """
    Get default system settings values
    
    - **Requires**: Super Admin authentication
    - **Returns**: Default system settings values
    """
    return SettingsController._get_default_settings()
