from functools import wraps
from django.shortcuts import redirect


def operator_required(funcion):
    @wraps(funcion)
    def comprobar(request, *args, **kwargs):
        es_operador = request.user.groups.filter(name="Operador").exists()
        if es_operador or request.user.is_superuser:
            return funcion(request, *args, **kwargs)
        return redirect("login")
    return comprobar