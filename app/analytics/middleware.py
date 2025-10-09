import uuid
from datetime import timedelta
from django.utils import timezone
from app.shop.models import Visit

class VisitMiddleware:
    COOKIE_NAME = "visitor_id"
    SESSION_TIMEOUT = timedelta(minutes=30)
    COOKIE_AGE = 60 * 60 * 24 * 365  

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path.startswith(("/admin", "/static", "/media")):
            return response

        ip = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        visitor_id = request.COOKIES.get(self.COOKIE_NAME)

        if not visitor_id:
            visitor_id = str(uuid.uuid4())
            response.set_cookie(
                self.COOKIE_NAME,
                visitor_id,
                max_age=self.COOKIE_AGE,
                httponly=True,
                samesite="Lax",
            )

        last_visit = (
            Visit.objects.filter(visitor_id=visitor_id)
            .order_by("-started_at")
            .first()
        )

        now = timezone.now()
        create_new = False

        if not last_visit:
            create_new = True
        else:
            delta = now - last_visit.started_at
            if delta > self.SESSION_TIMEOUT:
                create_new = True

        if create_new:
            Visit.objects.create(
                visitor_id=visitor_id,
                ip=ip,
                user_agent=user_agent,
            )

        return response