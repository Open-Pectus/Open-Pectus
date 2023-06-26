from fastapi import APIRouter

from openpectus.protocol.aggregator import Aggregator, _create_aggregator, _get_aggregator


def create_aggregator(router: APIRouter):
    return _create_aggregator(router)


def get_aggregator() -> Aggregator:
    return _get_aggregator()
