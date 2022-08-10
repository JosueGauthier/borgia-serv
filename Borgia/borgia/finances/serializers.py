from rest_framework import serializers


class SelfLydiaCreateAPISerializer(serializers.Serializer):
    """

    """

    amount = serializers.CharField(
        write_only=True,
    )

    phone_number = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):

        amount = attrs.get('amount')
        phone_number = attrs.get('phone_number')

        attrs['product'] = [amount, phone_number]
        return attrs
