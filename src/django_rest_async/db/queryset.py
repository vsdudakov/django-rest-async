from asgiref.sync import sync_to_async

from django.db import router

from django_rest_async.db.signals import async_m2m_changed


class AsyncBaseQuerySet:
    pipeline = {}

    def __init__(self, sync_manager, model):
        self.sync_manager = sync_manager
        self.key = model.__name__

    def _clean(self):
        self.pipeline[self.key] = []

    def _perform(self):
        qs = self.sync_manager.all()
        for operation in self.pipeline.get(self.key) or []:
            qs = getattr(qs, operation["fn"])(*operation["args"], **operation["kwargs"])
        self._clean()
        return qs

    def all(self, *args, **kwargs):
        if self.key not in self.pipeline:
            self._clean()

        self.pipeline[self.key].append(
            {
                "fn": "all",
                "args": args,
                "kwargs": kwargs,
            }
        )
        return self

    def filter(self, *args, **kwargs):
        if self.key not in self.pipeline:
            self._clean()

        self.pipeline[self.key].append(
            {
                "fn": "filter",
                "args": args,
                "kwargs": kwargs,
            }
        )
        return self

    def exclude(self, *args, **kwargs):
        if self.key not in self.pipeline:
            self._clean()

        self.pipeline[self.key].append(
            {
                "fn": "exclude",
                "args": args,
                "kwargs": kwargs,
            }
        )
        return self

    def select_related(self, *args, **kwargs):
        if self.key not in self.pipeline:
            self._clean()

        self.pipeline[self.key].append(
            {
                "fn": "select_related",
                "args": args,
                "kwargs": kwargs,
            }
        )
        return self

    def prefetch_related(self, *args, **kwargs):
        if self.key not in self.pipeline:
            self._clean()

        self.pipeline[self.key].append(
            {
                "fn": "prefetch_related",
                "args": args,
                "kwargs": kwargs,
            }
        )
        return self

    def order_by(self, *args, **kwargs):
        if self.key not in self.pipeline:
            self._clean()

        self.pipeline[self.key].append(
            {
                "fn": "order_by",
                "args": args,
                "kwargs": kwargs,
            }
        )
        return self

    def distinct(self, *args, **kwargs):
        if self.key not in self.pipeline:
            self._clean()

        self.pipeline[self.key].append(
            {
                "fn": "distinct",
                "args": args,
                "kwargs": kwargs,
            }
        )
        return self

    @sync_to_async(thread_sensitive=True)
    def get(self, *args, **kwargs):
        qs = self._perform()
        return qs.get(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def count(self, *args, **kwargs):
        qs = self._perform()
        return qs.count(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def update(self, *args, **kwargs):
        qs = self._perform()
        return qs.update(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def delete(self, *args, **kwargs):
        qs = self._perform()
        return qs.delete(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def exists(self, *args, **kwargs):
        qs = self._perform()
        return qs.exists(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def first(self, *args, **kwargs):
        qs = self._perform()
        return qs.first(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def last(self, *args, **kwargs):
        qs = self._perform()
        return qs.last(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def values(self, *args, **kwargs):
        qs = self._perform()
        return qs.values(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def values_list(self, *args, **kwargs):
        qs = self._perform()
        return [i for i in qs.values_list(*args, **kwargs)]

    @sync_to_async(thread_sensitive=True)
    def query(self, *args, **kwargs):
        qs = self._perform()
        return [i for i in qs]

    @sync_to_async(thread_sensitive=True)
    def pagination_query(self, order_by=None, limit=None, offset=0):
        qs = self._perform()
        total = qs.count()
        if order_by:
            qs = qs.order_by(*order_by)
        if limit:
            qs = qs[offset : offset + limit]  # noqa
        return {
            "results": [i for i in qs],
            "total": total,
            "order_by": order_by,
            "limit": limit,
            "offset": offset,
        }


class AsyncQuerySet(AsyncBaseQuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        sync_manager = model.objects
        super().__init__(sync_manager, model)

    @sync_to_async(thread_sensitive=True)
    def create(self, *args, **kwargs):
        self._clean()
        return self.sync_manager.create(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def get_or_create(self, *args, **kwargs):
        self._clean()
        return self.sync_manager.get_or_create(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def update_or_create(self, *args, **kwargs):
        self._clean()
        return self.sync_manager.update_or_create(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def bulk_create(self, *args, **kwargs):
        self._clean()
        return self.sync_manager.bulk_create(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def bulk_update(self, *args, **kwargs):
        self._clean()
        return self.sync_manager.bulk_update(*args, **kwargs)

    @classmethod
    def as_manager(cls):
        # Address the circular dependency between `Queryset` and `Manager`.
        from django.db.models.manager import Manager

        manager = Manager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager


class AsyncManyRelatedQuerySet(AsyncBaseQuerySet):
    def __init__(self, sync_manager):
        self.db = router.db_for_write(sync_manager.through, instance=sync_manager.instance)
        super().__init__(sync_manager, sync_manager.model)

    @sync_to_async(thread_sensitive=True)
    def _set(self, *args, **kwargs):
        self.sync_manager.set(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def _add(self, *args, **kwargs):
        self.sync_manager.add(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def _clear(self, *args, **kwargs):
        self.sync_manager.clear(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def _remove(self, *args, **kwargs):
        self.sync_manager.remove(*args, **kwargs)

    @sync_to_async(thread_sensitive=True)
    def _get_missing_target_ids(self, *args, **kwargs):
        return self.sync_manager._get_missing_target_ids(*args, **kwargs)

    async def set(self, *args, **kwargs):
        await self._set(*args, **kwargs)

    async def add(self, *args, **kwargs):
        objs = args
        target_ids = self.sync_manager._get_target_ids(self.sync_manager.target_field_name, objs)
        missing_target_ids = await self._get_missing_target_ids(
            self.sync_manager.source_field_name, self.sync_manager.target_field_name, self.db, target_ids
        )
        await async_m2m_changed.async_send(
            sender=self.sync_manager.through,
            action="pre_add",
            instance=self.sync_manager.instance,
            reverse=self.sync_manager.reverse,
            model=self.sync_manager.model,
            pk_set=missing_target_ids,
            using=self.db,
        )
        await self._add(*args, **kwargs)
        await async_m2m_changed.async_send(
            sender=self.sync_manager.through,
            action="post_add",
            instance=self.sync_manager.instance,
            reverse=self.sync_manager.reverse,
            model=self.sync_manager.model,
            pk_set=missing_target_ids,
            using=self.db,
        )

    async def clear(self, *args, **kwargs):
        await async_m2m_changed.async_send(
            sender=self.sync_manager.through,
            action="pre_clear",
            instance=self.sync_manager.instance,
            reverse=self.sync_manager.reverse,
            model=self.sync_manager.model,
            pk_set=None,
            using=self.db,
        )
        await self._clear(*args, **kwargs)
        await async_m2m_changed.async_send(
            sender=self.sync_manager.through,
            action="post_clear",
            instance=self.sync_manager.instance,
            reverse=self.sync_manager.reverse,
            model=self.sync_manager.model,
            pk_set=None,
            using=self.db,
        )

    async def remove(self, *args, **kwargs):
        old_ids = set()
        objs = args
        for obj in objs:
            if isinstance(obj, self.sync_manager.model):
                fk_val = self.sync_manager.target_field.get_foreign_related_value(obj)[0]
                old_ids.add(fk_val)
            else:
                old_ids.add(obj)
        await async_m2m_changed.async_send(
            sender=self.sync_manager.through,
            action="pre_remove",
            instance=self.sync_manager.instance,
            reverse=self.sync_manager.reverse,
            model=self.sync_manager.model,
            pk_set=old_ids,
            using=self.db,
        )
        await self._remove(*args, **kwargs)
        await async_m2m_changed.async_send(
            sender=self.sync_manager.through,
            action="post_remove",
            instance=self.sync_manager.instance,
            reverse=self.sync_manager.reverse,
            model=self.sync_manager.model,
            pk_set=old_ids,
            using=self.db,
        )
