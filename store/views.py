from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Order, OrderItem, Product, CartItem, WishlistItem
from .serializers import CategorySerializer, OrderSerializer, ProductSerializer, CartItemSerializer, WishlistItemSerializer
from .permissions import IsStoreManager
from django.db import transaction
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsStoreManager()]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsStoreManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        cat = self.request.query_params.get("category")
        if cat:
            qs = qs.filter(category__slug=cat)
        popular = self.request.query_params.get("popular")
        if popular == "most":
            qs = qs.order_by("-total_sold")
        elif popular == "least":
            qs = qs.order_by("total_sold")
        return qs
    
class CartViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    @action(detail=False, methods=["get"])
    def list_items(self, request):
        items = CartItem.objects.filter(user=request.user)
        return Response(CartItemSerializer(items, many=True).data)

    @action(detail=False, methods=["post"])
    def add(self, request):
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = Product.objects.get(pk=serializer.validated_data["product_id"])
        obj, created = CartItem.objects.get_or_create(user=request.user, product=product, defaults={"quantity": serializer.validated_data.get("quantity",1)})
        if not created:
            obj.quantity += serializer.validated_data.get("quantity",1)
            obj.save()
        return Response(CartItemSerializer(obj).data, status=201)

    @action(detail=False, methods=["post"])
    def remove(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", None)

        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cart_item = CartItem.objects.get(user=request.user, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)

        if quantity:
            # Reduce quantity by given amount
            if cart_item.quantity <= int(quantity):
                # Remove item if quantity to remove is >= current quantity
                cart_item.delete()
                return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)
            else:
                cart_item.quantity -= int(quantity)
                cart_item.save()
                return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)
        else:
            # Remove item completely
            cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)

class WishlistViewSet(viewsets.GenericViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if product exists
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if wishlist item exists
        wishlist_item = WishlistItem.objects.filter(user=request.user, product=product).first()

        if wishlist_item:
            # Remove from wishlist
            wishlist_item.delete()
            return Response({"message": "Removed from wishlist"}, status=status.HTTP_200_OK)
        else:
            # Add to wishlist
            wishlist_item = WishlistItem.objects.create(user=request.user, product=product)
            serializer = WishlistItemSerializer(wishlist_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_list(self, request):
        items = self.get_queryset()
        serializer = WishlistItemSerializer(items, many=True)
        return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user

    # Quick empty-cart check before transaction
    if not CartItem.objects.filter(user=user).exists():
        return Response({"detail": "Cart is empty"}, status=400)

    try:
        with transaction.atomic():
            # Lock cart items *inside* the transaction
            items = CartItem.objects.select_for_update().filter(user=user).select_related("product")

            # Validate stock first to avoid partial commits
            for item in items:
                if item.product.stock < item.quantity:
                    raise ValueError(f"Insufficient stock for {item.product.name}")

            # If validation passes, process the order
            total = Decimal("0.00")
            order = Order.objects.create(user=user)

            for item in items:
                p = item.product
                p.stock -= item.quantity
                p.total_sold += item.quantity
                p.save()

                OrderItem.objects.create(
                    order=order,
                    product=p,
                    quantity=item.quantity,
                    price_at_purchase=p.price
                )

                total += p.price * item.quantity

            order.total_amount = total
            order.save()
            items.delete()

    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    return Response(OrderSerializer(order).data, status=201)

class SalesReport(APIView):
    permission_classes = [IsAuthenticated, IsStoreManager]

    def get(self, request):
        qs = Product.objects.filter(total_sold__gt=0)
        category = request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)
        sort = request.query_params.get("sort")  
        if sort == "most_sold":
            qs = qs.order_by("-total_sold")
        elif sort == "least_sold":
            qs = qs.order_by("total_sold")
        data = [{"product": p.name, "sold": p.total_sold, "stock": p.stock, "category": p.category.name if p.category else None} for p in qs]
        return Response(data)

class LowStockAlertView(APIView):
    permission_classes = [IsAuthenticated]  # must be logged in

    def get(self, request):
        # Allow only store managers
        if request.user.role != 'manager':
            return Response(
                {"detail": "You do not have permission to view this."},
                status=status.HTTP_403_FORBIDDEN
            )

        threshold = 10  # Hardcoded low stock limit
        low_stock_products = Product.objects.filter(stock__lte=threshold)

        data = [
            {"name": p.name, "stock": p.stock}
            for p in low_stock_products
        ]
        return Response({"low_stock_products": data})

