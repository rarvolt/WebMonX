from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Watch, Value
from .serializers import WatchSerializer, ValueSerializer


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def watch_list(request):
    if request.method == 'GET':
        watches = request.user.watches.all()
        serializer = WatchSerializer(watches, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = WatchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def watch_detail(request, pk):
    try:
        watch = Watch.objects.get(pk=pk)
    except Watch.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.user != watch.owner:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        serializer = WatchSerializer(watch)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = WatchSerializer(watch, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        watch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def watch_value_latest(request, pk):
    try:
        watch = Watch.objects.get(pk=pk)
    except Watch.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.user != watch.owner:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    value = watch.values.latest('created')

    serializer = ValueSerializer(value)

    return Response(serializer.data)


@api_view(['GET'])
def watch_value_list(request, pk):
    try:
        watch = Watch.objects.get(pk=pk)
    except Watch.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    values = watch.values.all()
    serializer = ValueSerializer(values, many=True)

    return Response(serializer.data)


# def user_list(request):
#     return None
#
#
# def user_detail(request):
#     return None
#
#
# @api_view(['GET'])
# def user_detail_watches(request, pk):
#     user = User.objects.get(pk=pk)
#
#     serializer = WatchSerializer(user.watches, many=True)
#
#     return Response(serializer.data)

