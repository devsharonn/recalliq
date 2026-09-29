import logging
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
import asyncio
from hindsight_client import Hindsight
from support_agent import HINDSIGHT_API_KEY

BASE_URL = "https://api.hindsight.vectorize.io"


def bank_id_for(customer):
    return f"support-v2-{customer}"


def _client():
    return Hindsight(base_url=BASE_URL, api_key=HINDSIGHT_API_KEY)


async def _ensure_bank(bank_id):
    try:
        await _client().acreate_bank(bank_id=bank_id, name=bank_id)
    except Exception:
        pass


async def _recall(bank_id, query):
    r = await _client().arecall(bank_id=bank_id, query=query)
    seen, out = set(), []
    for m in r.results:
        key = " ".join(m.text.lower().split())[:120]
        if key not in seen:
            seen.add(key)
            out.append({"text": m.text})
    return out[:6]


async def _retain(bank_id, content):
    await _client().aretain(bank_id=bank_id, content=content)


def ensure_bank(customer):
    asyncio.run(_ensure_bank(bank_id_for(customer)))


def recall(customer, query):
    return asyncio.run(_recall(bank_id_for(customer), query))


def retain(customer, content):
    asyncio.run(_retain(bank_id_for(customer), content))
