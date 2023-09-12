# Generated by Django 4.2.5 on 2023-09-11 19:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('user_one', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_one_chats', to=settings.AUTH_USER_MODEL)),
                ('user_two', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_two_chats', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
                'unique_together': {('user_one', 'user_two')},
            },
        ),
        migrations.CreateModel(
            name='RoomMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField()),
                ('deleted', models.BooleanField(default=False)),
                ('chat_room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.chatroom')),
                ('sent_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
