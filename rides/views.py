from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F, Q, Prefetch
from django.utils import timezone
from datetime import timedelta
from .models import User, Ride, RideEvent
from .serializers import UserSerializer, RideSerializer, RideListSerializer, RideEventSerializer
from .permissions import IsAdminRole


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]


class RideViewSet(viewsets.ModelViewSet):
    """ViewSet for Ride model."""
    
    queryset = Ride.objects.all()
    permission_classes = [IsAdminRole]
    
    def get_serializer_class(self):
        """Use RideListSerializer for list action, RideSerializer for others."""
        if self.action == 'list':
            return RideListSerializer
        return RideSerializer
    
    def get_queryset(self):
        """
        Optimized queryset for Ride List endpoint.
        Uses select_related, prefetch_related, and annotations for performance.
        """
        queryset = Ride.objects.select_related('id_rider', 'id_driver')
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by rider email
        rider_email = self.request.query_params.get('rider_email', None)
        if rider_email:
            queryset = queryset.filter(id_rider__email=rider_email)
        
        # Distance sorting - requires lat/lng params
        ordering = self.request.query_params.get('ordering', None)
        lat = self.request.query_params.get('lat', None)
        lng = self.request.query_params.get('lng', None)
        
        if ordering and 'distance' in ordering:
            if lat is None or lng is None:
                # This will be caught in list() method
                pass
            else:
                try:
                    lat = float(lat)
                    lng = float(lng)
                    # Calculate Euclidean squared distance
                    # distance_sq = (pickup_latitude - lat)^2 + (pickup_longitude - lng)^2
                    queryset = queryset.annotate(
                        distance_sq=(
                            (F('pickup_latitude') - lat) * (F('pickup_latitude') - lat) +
                            (F('pickup_longitude') - lng) * (F('pickup_longitude') - lng)
                        )
                    )
                    if ordering == 'distance' or ordering == 'distance_sq':
                        queryset = queryset.order_by('distance_sq')
                    elif ordering == '-distance' or ordering == '-distance_sq':
                        queryset = queryset.order_by('-distance_sq')
                except (ValueError, TypeError):
                    # Invalid lat/lng - will be caught in list() method
                    pass
        
        # Prefetch filtered RideEvents (last 24 hours only)
        now = timezone.now()
        twenty_four_hours_ago = now - timedelta(hours=24)
        
        queryset = queryset.prefetch_related(
            Prefetch(
                'ride_events',
                queryset=RideEvent.objects.filter(
                    created_at__gte=twenty_four_hours_ago
                ).order_by('-created_at'),
                to_attr='todays_ride_events_prefetched'
            )
        )
        
        # Ordering by pickup_time (if not ordering by distance)
        if ordering and 'distance' not in ordering:
            if ordering == 'pickup_time':
                queryset = queryset.order_by('pickup_time')
            elif ordering == '-pickup_time':
                queryset = queryset.order_by('-pickup_time')
        elif not ordering or 'distance' not in ordering:
            # Default ordering
            queryset = queryset.order_by('-pickup_time')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override list to validate distance sorting params."""
        ordering = request.query_params.get('ordering', None)
        lat = request.query_params.get('lat', None)
        lng = request.query_params.get('lng', None)
        
        # Validate distance sorting params
        if ordering and 'distance' in ordering:
            if lat is None or lng is None:
                return Response(
                    {'error': 'lat and lng query parameters are required when ordering by distance'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                float(lat)
                float(lng)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'lat and lng must be valid floating point numbers'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return super().list(request, *args, **kwargs)


class RideEventViewSet(viewsets.ModelViewSet):
    """ViewSet for RideEvent model."""
    
    queryset = RideEvent.objects.all()
    serializer_class = RideEventSerializer
    permission_classes = [IsAdminRole]

