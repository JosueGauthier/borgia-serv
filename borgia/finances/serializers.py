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


"""
class LydiaStateAPISerializer(serializers.Serializer):
    
    
    params_dict = {
            !"currency": request.POST.get("currency"),
            !"request_id": request.POST.get("request_id"),
            !"amount": request.POST.get("amount"),
            !"signed": request.POST.get("signed"),
            !"transaction_identifier": request.POST.get("transaction_identifier"),
            !"vendor_token": request.POST.get("vendor_token"),
            !"sig": request.POST.get("sig")
        }

    
    
    currency = serializers.CharField(
        write_only=True,
    )
    
    amount = serializers.CharField(
        write_only=True,
    )

    phone_number = serializers.CharField(
        write_only=True,
    )

    request_uuid = serializers.CharField(
        write_only=True,
    )
    
    signed = serializers.CharField(
        write_only=True,
    )
    
    transaction_identifier = serializers.CharField(
        write_only=True,
    )
    
    vendor_token = serializers.CharField(
        write_only=True,
    )
    
    sig = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):

        currency = attrs.get('currency')
        amount = attrs.get('amount')
        phone_number = attrs.get('phone_number')
        request_uuid = attrs.get('request_uuid')
        signed = attrs.get('signed')
        transaction_identifier = attrs.get('transaction_identifier')
        vendor_token = attrs.get('vendor_token')
        sig = attrs.get('sig')

        attrs['state_data'] = [currency,amount,phone_number,request_uuid,signed,transaction_identifier,vendor_token,sig ]
        return attrs

 """


class LydiaStateAPISerializer(serializers.Serializer):
    """

    """

    request_uuid = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):

        request_uuid = attrs.get('request_uuid')

        attrs['state_data'] = [request_uuid]
        return attrs
