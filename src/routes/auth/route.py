from fastapi import APIRouter
from src.modules.auth import module


router = APIRouter()


router.add_api_route('/login', module.login, methods=["POST"])