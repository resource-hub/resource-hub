from django.db import models

from .base import BaseModel


class Message(BaseModel):
    sender = models.ForeignKey(
        'Actor',
        on_delete=models.PROTECT,
        related_name='messages_sent',
    )
    recipient = models.ForeignKey(
        'Actor',
        on_delete=models.PROTECT,
        related_name='messages_recieved',
    )
    text = models.TextField()


class ContractMessage(Message):
    contract = models.ForeignKey(
        'Contract',
        on_delete=models.CASCADE,
        related_name='messages',
    )
