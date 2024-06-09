from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.permissions import IsRelated
from utils import get_logger

from .models import Inbox, Message
from .serializers import InboxSerializer, MessageSerializer

log = get_logger(__name__)


class MessagePagination(LimitOffsetPagination):
    page_size = 10
    limit_query_param = "limit"
    offset_query_param = "offset"
    max_page_size = 100


class InboxViewSet(ListCreateAPIView, viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsRelated]
    serializer_class = InboxSerializer
    lookup_url_kwarg = "inbox_id"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context

    def get_queryset(self):
        queryset = None
        if query := self.request.query_params.get("q", None):
            queryset = Inbox.objects.filter(
                Q(user_1__personal_information__full_name__icontains=query)
                | Q(user_2__personal_information__full_name__icontains=query)
            )
        queryset = Inbox.objects.filter(
            Q(user_1=self.request.user) | Q(user_2=self.request.user)
        ).exclude(Q(last_message=None) | Q(last_message=""))
        return queryset

    def create(self, request, *args, **kwargs):
        if (
            request.data.get("user_1") != self.request.user.resident_id
            and request.data.get("user_2") != self.request.user.resident_id
        ):
            return Response(
                "You do not have permission to create this inbox", status=400
            )
        if inbox := Inbox.objects.filter(
            Q(user_1=request.data.get("user_1"), user_2=request.data.get("user_2"))
            | Q(
                user_1=request.data.get("user_2"),
                user_2=request.data.get("user_1"),
            )
        ).first():
            return Response(
                InboxSerializer(instance=inbox, context={"user": request.user}).data,
                status=200,
            )
        return super().create(request, *args, **kwargs)


class MessageViewSet(ListCreateAPIView, viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    lookup_url_kwarg = "message_id"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        queryset = Message.objects.filter(
            Q(inbox__user_1=self.request.user) | Q(inbox__user_2=self.request.user),
            inbox_id=self.kwargs["inbox_id"],
        ).all()
        return queryset.order_by("-created_date")

    def perform_create(self, serializer):
        serializer.save(inbox_id=self.kwargs["inbox_id"], sender=self.request.user)

    def list(self, request, *args, **kwargs):
        inbox = get_object_or_404(Inbox, id=self.kwargs["inbox_id"])
        if inbox.user_1 != self.request.user and inbox.user_2 != self.request.user:
            return Response(
                "You do not have permission to get messages from this inbox", status=400
            )
        response = super().list(request, *args, **kwargs)
        if response.data:
            response.data["inbox"] = InboxSerializer(
                instance=inbox,
                context={"user": request.user},
            ).data
        log.info("Get messagse successfully")
        return response
