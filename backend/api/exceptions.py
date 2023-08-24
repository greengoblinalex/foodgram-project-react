from rest_framework.exceptions import PermissionDenied


class Unauthorized401(PermissionDenied):
    status_code = 401
    default_detail = "Учетные данные не были предоставлены."


class NotEnoughRights403(PermissionDenied):
    status_code = 403
    default_detail = "У вас недостаточно прав для выполнения данного действия."
