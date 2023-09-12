from rest_framework import serializers
from chat.models import ChatRoom, RoomMessage


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = (
            'id',
            'created_at'
        )

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['last_message_on'] = None
    #     data['last_message'] = None
    #     if hasattr(instance, 'last_message_on') and hasattr(instance, 'last_message'):
    #         data['last_message_on'] = instance.last_message_on
    #         data['last_message'] = decrypt_message(instance.last_message)
    #     else:
    #         last_message = RoomMessage.objects.filter(room_id=instance.id).order_by('-created_at').first()
    #         if last_message:
    #             data['last_message'] = decrypt_message(last_message.message)
    #             data['last_message_on'] = last_message.created_at
    #     if self.context['request'].user.user_type == UserType.user_one.value[0]:
    #         data['other_user'] = CustomUserShortSerializer(instance.user_two, context=self.context).data
    #         if hasattr(instance, 'unread_messages'):
    #             data['unread_messages'] = instance.unread_messages
    #         else:
    #             data['unread_messages'] = RoomMessage.objects.filter(room_id=instance.id,
    #                                                                  created_at__gt=instance.user_one_last_online).count()
    #     else:
    #         data['other_user'] = CustomUserShortSerializer(instance.user_one, context=self.context).data
    #         if hasattr(instance, 'unread_messages'):
    #             data['unread_messages'] = instance.unread_messages
    #         else:
    #             data['unread_messages'] = RoomMessage.objects.filter(room_id=instance.id,
    #                                                                  created_at__gt=instance.user_two_last_online).count()
    #     return data


class RoomMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMessage
        fields = (
            'id',
            'created_at',
            'sent_by_id',
            'message',
            'deleted',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.deleted:
            data['message'] = ''
        else:
            data['message'] = decrypt_message(instance.message)
        return data
