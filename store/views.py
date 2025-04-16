from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Book, Cart, Rating
from .forms import CustomUserCreationForm, UserProfileForm, RatingForm

def home(request):
    books = Book.objects.all()
    return render(request, 'store/home.html', {'books': books})

def search_books(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(title__icontains=query) | Book.objects.filter(author__icontains=query) | Book.objects.filter(subject__icontains=query)
    return render(request, 'store/search_results.html', {'books': books, 'query': query})

@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.stock > 0:
        cart_item, created = Cart.objects.get_or_create(user=request.user, book=book)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        book.stock -= 1
        book.save()
    return redirect('cart')

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.book.price * item.quantity for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def checkout(request):
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            item.delete()
        return redirect('home')
    return render(request, 'store/checkout.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile_form = UserProfileForm(request.POST)
            if profile_form.is_valid():
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
        profile_form = UserProfileForm()
    return render(request, 'store/register.html', {'form': form, 'profile_form': profile_form})

@login_required
def rate_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.book = book
            rating.user = request.user
            rating.save()
            return redirect('home')
    else:
        form = RatingForm()
    return render(request, 'store/rate.html', {'form': form, 'book': book})