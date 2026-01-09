from rest_framework import serializers
from .models import User, Ride, RideEvent


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id_user', 'email', 'role', 'first_name', 'last_name', 'phone_number']
        read_only_fields = ['id_user']


class RideEventSerializer(serializers.ModelSerializer):
    """Serializer for RideEvent model."""
    
    class Meta:
        model = RideEvent
        fields = ['id_ride_event', 'id_ride', 'description', 'created_at']
        read_only_fields = ['id_ride_event', 'created_at']


class MinimalUserSerializer(serializers.ModelSerializer):
    """Minimal user serializer for nested representation."""
    
    class Meta:
        model = User
        fields = ['id_user', 'first_name', 'last_name', 'email']


class RideSerializer(serializers.ModelSerializer):
    """Serializer for Ride model (CRUD operations)."""
    
    rider = MinimalUserSerializer(source='id_rider', read_only=True)
    driver = MinimalUserSerializer(source='id_driver', read_only=True)
    
    class Meta:
        model = Ride
        fields = [
            'id_ride', 'status', 'id_rider', 'id_driver',
            'pickup_latitude', 'pickup_longitude',
            'dropoff_latitude', 'dropoff_longitude',
            'pickup_time', 'rider', 'driver'
        ]
        read_only_fields = ['id_ride']


class RideEventListSerializer(serializers.ModelSerializer):
    """Serializer for RideEvent in list view (minimal fields)."""
    
    class Meta:
        model = RideEvent
        fields = ['id_ride_event', 'description', 'created_at']


class RideListSerializer(serializers.ModelSerializer):
    """Serializer for Ride List endpoint with nested data."""
    
    rider = MinimalUserSerializer(source='id_rider', read_only=True)
    driver = MinimalUserSerializer(source='id_driver', read_only=True)
    todays_ride_events = serializers.SerializerMethodField()
    
    class Meta:
        model = Ride
        fields = [
            'id_ride', 'status', 'pickup_time',
            'pickup_latitude', 'pickup_longitude',
            'dropoff_latitude', 'dropoff_longitude',
            'rider', 'driver', 'todays_ride_events'
        ]
    
    def get_todays_ride_events(self, obj):
        """Get prefetched today's ride events."""
        # Access the prefetched queryset
        events = getattr(obj, 'todays_ride_events_prefetched', None)
        if events is None:
            # Fallback: return empty list if not prefetched
            return []
        return RideEventListSerializer(events, many=True).data

