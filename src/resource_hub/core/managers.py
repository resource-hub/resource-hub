from django.db.models import Manager
from django.db.models.query import QuerySet

from model_utils.managers import InheritanceManagerMixin, InheritanceQuerySet


class SoftDeletableQuerySetMixin:
    """
    QuerySet for SoftDeletableModel. Instead of removing instance sets
    its ``is_removed`` field to True.
    """

    def soft_delete(self):
        """
        Soft delete objects from queryset (set their ``is_removed``
        field to True)
        """
        self.update(is_deleted=True)


class CombinedQuerySet(SoftDeletableQuerySetMixin, InheritanceQuerySet):
    pass


class CombinedManagerMixin(InheritanceManagerMixin):
    """
    Manager that limits the queryset by default to show only not removed
    instances of model.
    """
    _queryset_class = CombinedQuerySet

    def get_queryset(self):
        """
        Return queryset limited to not removed entries.
        """
        kwargs = {'model': self.model, 'using': self._db}
        if hasattr(self, '_hints'):
            kwargs['hints'] = self._hints

        return self._queryset_class(**kwargs).filter(is_deleted=False)


class CombinedManager(CombinedManagerMixin, Manager):
    pass
