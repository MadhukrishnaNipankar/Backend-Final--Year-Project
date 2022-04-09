from rest_framework import serializers

class VideoDataSerializer(serializers.Serializer):
    sno = serializers.IntegerField() 
    video_title = serializers.CharField(max_length=1000)
    video_desc = serializers.CharField(max_length=5000)
    video_keywords = serializers.CharField(max_length=4000,default="")
    video_likes = serializers.IntegerField(default=0)
    video_views = serializers.IntegerField(default=0)
    video_report_count = serializers.IntegerField(default=0)
    video_thumbnail = serializers.ImageField()
    video_file = serializers.FileField()
    notes_file = serializers.FileField()
    timestamp = serializers.DateTimeField()


class MessageSerializer(serializers.Serializer):
    sno = serializers.IntegerField()
    value = serializers.CharField(max_length=4000)
    timestamp = serializers.DateTimeField()
    username = serializers.CharField(default="",max_length=1000)
    room = serializers.CharField(default="",max_length=1000)