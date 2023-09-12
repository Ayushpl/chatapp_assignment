from django.db import models
from api.models import BaseModel, CustomUser

class ChatRoom(BaseModel):

    """
    user_one = the user who initiated the chat
    user_two = the other user who was invited to chat
    """
    user_one = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_one_chats')
    user_two = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_two_chats')

    class Meta:
        ordering = (
        '-created_at',)
        unique_together = ('user_one', 'user_two',)


class RoomMessage(BaseModel):
    modified_at = None
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sent_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    deleted = models.BooleanField(default=False)
