from rest_framework import serializers
from .models import Film, Comment


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'film', 'text', 'author_name', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_text(self, value):
        #Ensure comment text doesn't exceed 500 characters
        if len(value) > 500:
            raise serializers.ValidationError(
                "Comment text cannot exceed 500 characters.")
        return value


class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['text', 'author_name']

    def validate_text(self, value):
        #Ensures comment text doesn't exceed 500 characters
        if len(value) > 500:
            raise serializers.ValidationError("Comment text cannot exceed 500 characters.")
        if not value.strip():
            raise serializers.ValidationError("Comment text cannot be empty.")
        return value.strip()


class FilmListSerializer(serializers.ModelSerializer):

    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Film
        fields = ['id', 'title', 'release_date', 'comment_count']


class FilmDetailSerializer(serializers.ModelSerializer):

    comment_count = serializers.IntegerField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Film
        fields = [
            'id', 'title', 'episode_id', 'opening_crawl',
            'director', 'producer', 'release_date',
            'comment_count', 'comments'
        ]