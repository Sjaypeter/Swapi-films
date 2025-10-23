from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from django.core.cache import cache
from .models import Film, Comment
from .serializers import (
    FilmListSerializer,
    FilmDetailSerializer,
    CommentSerializer,
    CommentCreateSerializer
)
import logging

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class FilmViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Film.objects.all()
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return FilmListSerializer
        return FilmDetailSerializer

    def get_queryset(self):
        """Annotate queryset with comment count for efficiency."""
        return Film.objects.annotate(
            comment_count=Count('comments')
        ).order_by('release_date')

    def list(self, request, *args, **kwargs):
        
        #Get list of all films.
        try:
            film_count = Film.objects.count()
            if film_count == 0:
                logger.info("No films in database, syncing from SWAPI...")
                swapi_service = SwapiService()
                swapi_service.sync_films()
            
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Error listing films: {str(e)}")
            return Response(
                {"error": "Failed to retrieve films"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='comments')
    def comments(self, request, pk=None):
       
        #Get all comments for a specific film.

        try:
            film = self.get_object()
            comments = film.comments.all().order_by('created_at')
            
            page = self.paginate_queryset(comments)
            if page is not None:
                serializer = CommentSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        except Film.DoesNotExist:
            return Response(
                {"error": "Film not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving comments: {str(e)}")
            return Response(
                {"error": "Failed to retrieve comments"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='add-comment')
        def add_comment(self, request, pk=None):
            """
            Add a comment to a specific film.
            """
            try:
                film = self.get_object()
                serializer = CommentCreateSerializer(data=request.data)
                
                if serializer.is_valid():
                    # Get client IP
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0]
                    else:
                        ip = request.META.get('REMOTE_ADDR')
                    
                    comment = serializer.save(
                        film=film,
                        author_ip=ip
                    )
                    
                    response_serializer = CommentSerializer(comment)
                    return Response(
                        response_serializer.data,
                        status=status.HTTP_201_CREATED
                    )
                
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            except Film.DoesNotExist:
                return Response(
                    {"error": "Film not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                logger.error(f"Error adding comment: {str(e)}")
                return Response(
                    {"error": "Failed to add comment"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

class CommentViewSet(viewsets.ReadOnlyModelViewSet):
   
    #ViewSet for viewing comments.
    
    queryset = Comment.objects.all().order_by('created_at')
    serializer_class = CommentSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        #Filter comments by film if film_id is provided
        queryset = Comment.objects.all().order_by('created_at')
        film_id = self.request.query_params.get('film_id', None)
        
        if film_id is not None:
            queryset = queryset.filter(film_id=film_id)
        
        return queryset
   