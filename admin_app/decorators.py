from django.shortcuts import redirect


def admins_only(view_func):
    def wrap(request, *args, **kwargs):
        from main_app.models import AgenciaUsuario
        if not request.user.is_anonymous:
            agencia_usuario = AgenciaUsuario.objects.filter(usuario=request.user)
            if agencia_usuario:
                agencia_usuario = agencia_usuario.first()
                request.agencia_usuario = agencia_usuario
                return view_func(request, *args, **kwargs)
            else:
                return redirect('/login/')
        else:
            return redirect('/login/')
    return wrap