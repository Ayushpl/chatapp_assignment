
from functools import reduce
from api.models import CustomUser
from base.base_views import CustomAPIView, CustomGenericView
from base.utils import (CustomException, CustomLimitOffsetPagination,
                        paginated_success_response, success_response, error_response)
from chat.models import ChatRoom, RoomMessage
from chat.serializers import ChatRoomSerializer, RoomMessageSerializer
from strings import *


class ChatRoomView(CustomAPIView):
    def post(self, request):
        #check if other user is online
        other_user = CustomUser.objects.filter(
        id=request.data['recipient']).first()
        if other_user:
            room = ChatRoom(
                user_one=request.user,
                user_two=other_user
            )
            room.save()
            room_data = ChatRoomSerializer(room, context={'request': request}).data
            return success_response(message='Chat Room created successfully', data=room_data)
        else:
            return error_response(message='The other user is not Online',)

    



