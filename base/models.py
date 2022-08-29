
from django.contrib.auth.models import User
from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=200)
    header_image = models.ImageField(blank=True, null=True, upload_to='images/')
    description = models.TextField(blank=True, null=True)  

    def __str__(self) -> str:
        return self.name
    def get_bref_discription(self):
        return self.description[0:100]

    class Meta:
        ordering = ['name']


class Room(models.Model):
    name = models.CharField(max_length=200)
    avatar = models.ImageField(blank=True, null=True, upload_to='images/')
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='host2room')
    participants = models.ManyToManyField(User, related_name='user2room')
    topic = models.ManyToManyField(Topic, related_name='topic2room')
    description = models.TextField(blank=True, null=True) 
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.name)
    def get_bref_discription(self):
        return self.description[0:100]



class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self) -> str:
        return self.body[0:50]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    email_is_verified= models.BooleanField(default=False)
    avatar = models.ImageField(blank=True, null=True, upload_to='images/')
    bio = models.TextField(blank=True, null=True)


