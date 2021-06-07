import pytest

from .models import BasicModel, ManyToManyModel, ManyToOneModel


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_obj_save():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_obj_delete():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    pk = model.pk
    await model.async_delete()
    exists = await BasicModel.async_objects.filter(pk=pk).exists()
    assert not exists


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_exists():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    exists = await BasicModel.async_objects.filter(field__contains="test").exists()
    assert exists


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_exclude():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    exists = await BasicModel.async_objects.exclude(field__contains="test").exists()
    assert not exists


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_count():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    count = await BasicModel.async_objects.all().count()
    assert count == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_values_list():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    values_list = await BasicModel.async_objects.all().values_list("pk", flat=True)
    assert values_list[0] == model.pk


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_values():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    values = await BasicModel.async_objects.all().values("pk")
    assert values[0]["pk"] == model.pk


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_last():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    obj = await BasicModel.async_objects.all().last()
    assert obj.pk == model.pk


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_first():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    obj = await BasicModel.async_objects.all().first()
    assert obj.pk == model.pk


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_get():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    obj = await BasicModel.async_objects.filter(field="test").get()
    assert obj.pk == model.pk


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_query():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    obj = await BasicModel.async_objects.filter(field="test").query()
    assert obj[0].pk == model.pk


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_update():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    await BasicModel.async_objects.filter(field="test").update(field="test_1")
    await model.async_refresh_from_db()

    assert model.field == "test_1"


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_delete():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    await BasicModel.async_objects.filter(field="test").delete()

    exists = await BasicModel.async_objects.exclude(field__contains="test").exists()
    assert not exists


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_all():
    model = BasicModel(field="test")
    await model.async_save()
    await model.async_refresh_from_db()

    assert model.field == "test"

    objs = await BasicModel.async_objects.all().query()

    assert len(objs) == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_m2o():
    model = await BasicModel.async_objects.create(field="test")
    m2o_model = await ManyToOneModel.async_objects.create(field=model)

    rel_model = await m2o_model.async_field

    assert rel_model.pk == model.pk


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_db_m2m():
    model = await BasicModel.async_objects.create(field="test")
    m2m_model = await ManyToManyModel.async_objects.create()

    await m2m_model.async_field.add(model)
    rel_models = await m2m_model.async_field.all().query()
    assert len(rel_models) == 1
    assert rel_models[0].pk == model.pk

    await m2m_model.async_field.remove(model)
    rel_models = await m2m_model.async_field.all().query()
    assert len(rel_models) == 0
