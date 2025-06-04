from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.views.generic import RedirectView

from recipes.models import ShortLink


class ShortLinkRedirectView(RedirectView):
    """Редирект по короткой ссылке."""

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """Получение URL для редиректа."""
        short_id = kwargs.get('short_id')

        try:
            short_link = get_object_or_404(ShortLink, short_id=short_id)
            # Редирект на страницу рецепта
            return f'/recipes/{short_link.recipe.id}/'
        except ShortLink.DoesNotExist:
            raise Http404("Короткая ссылка не найдена")


# Функция-обертка для удобного использования в urls.py
def short_link_redirect(request, short_id):
    """Функция редиректа по короткой ссылке."""
    view = ShortLinkRedirectView.as_view()
    return view(request, short_id=short_id)
