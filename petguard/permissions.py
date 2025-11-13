from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    """Retorna True se o usuário for superusuário (admin)."""
    return user.is_authenticated and user.is_superuser


def is_operador(user):
    """Retorna True se o usuário estiver no grupo 'Operador'."""
    return user.is_authenticated and user.groups.filter(name='Operador').exists()


def is_veterinario(user):
    """Retorna True se o usuário estiver no grupo 'Veterinario'."""
    return user.is_authenticated and user.groups.filter(name='Veterinario').exists()

admin_required = user_passes_test(is_admin, login_url='login')
operador_required = user_passes_test(
    lambda u: is_admin(u) or is_operador(u), login_url='login'
)
veterinario_required = user_passes_test(
    lambda u: is_admin(u) or is_veterinario(u), login_url='login'
)
