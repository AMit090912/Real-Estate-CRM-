def current_role(request):
    return {"current_role": request.session.get("role", "Admin")}
