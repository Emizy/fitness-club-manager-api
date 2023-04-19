from rest_framework import serializers

from apps.core.models import User, MemberShip, FitnessClub, CheckIn


class MemberShipSerializer(serializers.ModelSerializer):
    """
    This handle data serialization of membership model
    """

    class Meta:
        model = MemberShip
        fields = ["id", "state", "amount_of_credit", "start_date", "end_date"]


class UserSerializer(serializers.ModelSerializer):
    """
    This handle data serialization of user model
    """
    membership = MemberShipSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "email", "phone_number", "membership"]


class FitnessClubSerializer(serializers.ModelSerializer):
    """
    This handle data serialization of fitness club model
    """

    class Meta:
        model = FitnessClub
        fields = ["id", "name", "description", ]


class CheckInSerializer(serializers.ModelSerializer):
    """
    This handle data serialization for user checkin model
    """
    membership = MemberShipSerializer(read_only=True)
    club = FitnessClubSerializer(read_only=True)

    class Meta:
        model = CheckIn
        fields = ["id", "membership", "club", "created_at"]


class UserFormSerializer(serializers.Serializer):
    """
    this class handles user create and update functionality
    """
    name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(max_length=255, required=True)
    phone_number = serializers.CharField(max_length=20, required=False)

    def create(self, validated_data):
        """
        Method handles creating of a user account on the system
        """
        instance = User.objects.create(**validated_data)
        _, _ = MemberShip.objects.get_or_create(user=instance)
        return instance

    def update(self, instance, validated_data):
        """
        Method handles update of user information
        """
        _ = User.objects.filter(id=instance.id).update(**validated_data)
        return instance


class FitnessClubFormSerializer(serializers.Serializer):
    """
        this class handles creating and updating of fitness clubs on the system
    """
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)

    def create(self, validated_data):
        """
           Method handles creating of a new fitness club
        """
        instance = FitnessClub.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        """
            Method handles updating of already existing fitness club
        """
        _ = FitnessClub.objects.filter(id=instance.id).update(**validated_data)
        return instance


class CheckInFormSerializer(serializers.Serializer):
    """
        this class handles method that allows users to checkin to one or more fitness clubs
    """
    user = serializers.IntegerField(required=True)
    club = serializers.IntegerField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
