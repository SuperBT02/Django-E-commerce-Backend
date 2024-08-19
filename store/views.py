from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Product, Collection, OrderItem, Review, Cart, CartItem, Customer, Order
from rest_framework import status

from .permissions import IsAdminOrReadOnly, FullDjangoModelPermissions, ViewCustomerHistoryPermission
from .serializers import ProductSerialize, CollectionSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, \
    AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, OrderSerializer, CreateOrderSerializer, \
    UpdateOrderSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions


class ProductViewSet(ModelViewSet):
    # queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerialize
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted'})
        return super().destroy(request, *args, **kwargs)


# !!!!!! GENERIC VIEWS (ALL THOSE SIMILAR VIEWS HAS BEEN TRANSFERT IN THE SAME VIEWLIST )
# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.select_related('collection').all()
#     serializer_class = ProductSerialize
#
#     def get_serializer_context(self):
#         return {'request': self.request}


# class ProductDetails(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerialize

# def get(self, request, id):
#     product = get_object_or_404(Product, pk=id)
#     serializer = ProductSerialize(product)
#     return Response(serializer.data)
#
# def put(self, request, id):
#     product = get_object_or_404(Product, pk=id)
#     serializer = ProductSerialize(product, data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data, status=status.HTTP_201_CREATED)

# def delete(self, request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     if product.orderitems.count() > 0:
#         return Response({'error:Product can not be deleted'}, status=status.HTTP_204_NO_CONTENT)
#     product.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)
class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('product')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Collection.objects.annotate(
        products_count=Count('product'))
    serializer_class = CollectionSerializer

    # @api_view(['GET', 'POST', 'DELETE'])
    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.Count() > 0:
            return Response({'error': 'Collection cant be deleted whe it containt products'})
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# !!!!!! GENERIC VIEWS (ALL THOSE SIMILAR VIEWS HAS BEEN TRANSFERT IN THE SAME VIEWLIST )
# class Collection_List(RetrieveUpdateDestroyAPIView):
# queryset = Collection.objects.annotate(products_count=Count('product')).all()
# serializer_class = CollectionSerializer


# def collection_list(request):
#     if request.method == 'GET':
#         collection = Collection.objects.annotate(products_count=Count('product')).all()
#         serializer = CollectionSerializer(collection, many=True)
#         return Response(serializer.data)
#     if request.method == 'POST':
#         collection = CollectionSerializer(data=request.data)
#         collection.is_valid(raise_exception=True)
#         collection.save()
#         return Response(collection.data, status=status.HTTP_201_CREATED)

# class Collection_Detail(RetrieveUpdateDestroyAPIView):
# queryset = Collection.objects.annotate(
#     products_count=Count('product'))
# serializer_class = CollectionSerializer
#
# # @api_view(['GET', 'POST', 'DELETE'])
# def delete(self, request, pk):
#     collection = get_object_or_404(Collection, pk=pk)
#     if collection.products.Count() > 0:
#         return Response({'error': 'Collection cant be deleted whe it containt products'})
#     collection.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)
# if request.method == 'GET':
#     serializer = CollectionSerializer(collection)
#     return Response(serializer.data)
# elif request.method == 'POST':
#     serializer = Collection(collection, data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data)
# elif request.method == 'DELETE':
class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class CartViewSet(CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        if self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects \
            .filter(cart_id=self.kwargs['cart_pk']) \
            .select_related('product')


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):

        return Response('ok')

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    # queryset = Order.objects.all()
    # serializer_class = OrderSerializer
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        customer_id = Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)
