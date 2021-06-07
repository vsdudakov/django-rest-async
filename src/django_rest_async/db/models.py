from asgiref.sync import sync_to_async

from django.db.models import Model, QuerySet

from django_rest_async.db.queryset import AsyncManyRelatedQuerySet, AsyncQuerySet
from django_rest_async.db.signals import async_post_delete, async_post_save, async_pre_delete, async_pre_save


class AsyncModel(Model):

    objects = QuerySet.as_manager()
    async_objects = AsyncQuerySet.as_manager()

    @sync_to_async(thread_sensitive=True)
    def _save(self, *args, **kwargs):
        return self.save(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def _delete(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def _refresh_from_db(self, *args, **kwargs):
        return self.refresh_from_db(*args, **kwargs)

    async def async_save(self, *args, **kwargs):
        cls = origin = self.__class__
        meta = cls._meta
        update_fields = kwargs.get("update_fields", None)
        using = kwargs.get("using", None)
        if not meta.auto_created:
            await async_pre_save.async_send(
                sender=origin,
                instance=self,
                raw=False,
                using=using,
                update_fields=update_fields,
            )
        result = await self._save(*args, **kwargs)
        if not meta.auto_created:
            await async_post_save.async_send(
                sender=origin,
                instance=self,
                created=None,  # TODO
                update_fields=update_fields,
                raw=False,
                using=using,
            )
        return result

    async def async_delete(self, *args, **kwargs):
        origin = self.__class__
        using = kwargs.get("using", None)
        await async_pre_delete.async_send(
            sender=origin,
            instance=self,
            using=using,
        )
        result = await self._delete(*args, **kwargs)
        await async_post_delete.async_send(
            sender=origin,
            instance=self,
            using=using,
        )
        return result

    async def async_refresh_from_db(self, *args, **kwargs):
        return await self._refresh_from_db(*args, **kwargs)

    def __getattribute__(self, field):
        if not field.startswith("async_"):
            return super().__getattribute__(field)
        field_name = field.replace("async_", "")
        opts = self._meta
        m2m_fields = [f.name for f in opts.many_to_many]
        rel_fields = [f.name for f in opts.get_fields() if f.__class__.__name__ in ("ForeignKey", "OneToOneField")]
        if field_name in m2m_fields:
            value = super().__getattribute__(field_name)
            return AsyncManyRelatedQuerySet(value)
        if field_name in rel_fields:
            return sync_to_async(super().__getattribute__, thread_sensitive=True)(field_name)
        return super().__getattribute__(field)

    class Meta:
        abstract = True
