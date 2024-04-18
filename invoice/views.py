from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ViewSet

from .models import Invoice
from .serializers import InvoiceSerializer


class InvoiceView(ViewSet, ListAPIView, RetrieveAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        queries = self.queryset

        q = self.request.query_params.get("q")
        if q:
            queries = queries.filter(id__icontains=q)

        return queries
