import json

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_run_claims_exist(client: AsyncClient):
    response = await client.get("/claims")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_run_members_exist(client: AsyncClient):
    response = await client.get("/members")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_run_payment_exists_by_service_date(client: AsyncClient):
    response = await client.get("/payment?service_date=2018-03-28")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_run_payment_by_service_date_incorrect_date_format(client: AsyncClient):
    response = await client.get("/payment?service_date=incorrect_date_str")
    assert response.status_code == 422


@pytest.mark.anyio
async def test_run_payment_does_not_exists_by_service_date(client: AsyncClient):
    response = await client.get("/payment?service_date=2022-01-01")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_run_payment_reverse_success(client: AsyncClient):
    request = {
        "claim_id": 1002832,
        "member_id": 183472,
        "service_date": "2018-03-28"
    }
    response = await client.request('DELETE', "/payment?service_date=2018-03-28", content=json.dumps(request))
    assert response.status_code == 204


@pytest.mark.anyio
async def test_run_payment_reverse_incorrect_service_date_format(client: AsyncClient):
    request = {
        "claim_id": 1002832,
        "member_id": 183472,
        "service_date": "incorrect date string"
    }
    response = await client.request('DELETE', "/payment?service_date=2018-03-28", content=json.dumps(request))
    assert response.status_code == 422


@pytest.mark.anyio
async def test_run_payment_reverse_that_dont_exist(client: AsyncClient):
    request = {
        "claim_id": 0,
        "member_id": 0,
        "service_date": "2018-03-28"
    }
    response = await client.request('DELETE', "/payment?service_date=2018-03-28", content=json.dumps(request))
    assert response.status_code == 404
