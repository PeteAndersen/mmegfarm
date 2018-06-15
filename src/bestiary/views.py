from django.contrib.auth.mixins import AccessMixin
from django.views.generic import FormView

from .forms import UploadFileForm


class AdminRequiredMixin(AccessMixin):
    """Verify that the current user is an administrator"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class UploadCreatureDataView(AdminRequiredMixin, FormView):
    form_class = UploadFileForm
    template_name = 'bestiary/upload_monster_data.html'

    def form_valid(self, form):
        results = form.parse_creatures()
        return self.render_to_response(self.get_context_data(results=results))
