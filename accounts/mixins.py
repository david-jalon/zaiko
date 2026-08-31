from django.contrib.auth.mixins import UserPassesTestMixin

class OperatorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        es_operador = self.request.user.groups.filter(name="Operador").exists()
        return es_operador or self.request.user.is_superuser