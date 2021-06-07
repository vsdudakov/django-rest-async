from django.db.models.signals import ModelSignal


class AsyncModelSignal(ModelSignal):
    async def async_send(self, sender, **named):
        if not self.receivers or self.sender_receivers_cache.get(sender) is object():
            return []

        return [
            (receiver, await receiver(signal=self, sender=sender, **named)) for receiver in self._live_receivers(sender)
        ]


async_pre_save = AsyncModelSignal(use_caching=True)
async_post_save = AsyncModelSignal(use_caching=True)

async_pre_delete = AsyncModelSignal(use_caching=True)
async_post_delete = AsyncModelSignal(use_caching=True)

async_m2m_changed = AsyncModelSignal(use_caching=True)
