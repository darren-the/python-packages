import uuid


def create_order_id():
    return uuid.uuid4().int
