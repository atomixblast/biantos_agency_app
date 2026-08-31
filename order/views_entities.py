from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from order.models import Article, Customer, SalesExecutive, Order
from order.forms_entities import ArticleForm, CustomerForm, SalesExecutiveForm


# ==================== ARTICLES ====================

@login_required
def list_articles(request):
    """Liste des articles"""
    search = request.GET.get('search', '')
    articles = Article.objects.all().order_by('-created_at')
    
    if search:
        articles = articles.filter(
            Q(name__icontains=search) | Q(ref__icontains=search)
        )
    
    context = {
        'articles': articles,
        'search': search,
    }
    return render(request, 'order/entities/articles/list.html', context)


@login_required
def create_article(request):
    """Créer un article"""
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save()
            messages.success(request, f'Article "{article.name}" créé avec succès !')
            return redirect('order:list_articles')
    else:
        form = ArticleForm()
    
    context = {'form': form, 'action': 'create'}
    return render(request, 'order/entities/articles/form.html', context)


@login_required
def update_article(request, article_id):
    """Modifier un article"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()
            messages.success(request, f'Article "{article.name}" modifié avec succès !')
            return redirect('order:list_articles')
    else:
        form = ArticleForm(instance=article)
    
    context = {'form': form, 'article': article, 'action': 'update'}
    return render(request, 'order/entities/articles/form.html', context)


@login_required
def detail_article(request, article_id):
    """Détails d'un article"""
    article = get_object_or_404(Article, id=article_id)
    
    # Récupérer les commandes contenant cet article
    orders = Order.objects.filter(articles=article).select_related('customer', 'sales_executive').order_by('-created_at')
    
    context = {
        'article': article,
        'orders': orders,
    }
    return render(request, 'order/entities/articles/detail.html', context)


@login_required
def delete_article(request, article_id):
    """Supprimer un article"""
    article = get_object_or_404(Article, id=article_id)
    
    # Vérifier si l'article est utilisé dans des commandes
    orders_count = Order.objects.filter(articles=article).count()
    
    if orders_count > 0:
        messages.error(request, f'Impossible de supprimer "{article.name}". Il est utilisé dans {orders_count} commande(s).')
    else:
        article_name = article.name
        article.delete()
        messages.success(request, f'Article "{article_name}" supprimé avec succès !')
    
    return redirect('order:list_articles')


# ==================== CLIENTS ====================

@login_required
def list_customers(request):
    """Liste des clients"""
    search = request.GET.get('search', '')
    customers = Customer.objects.all().annotate(
        orders_count=Count('order')
    ).order_by('-created_at')
    
    if search:
        customers = customers.filter(
            Q(name__icontains=search) | Q(tel__icontains=search)
        )
    
    context = {
        'customers': customers,
        'search': search,
    }
    return render(request, 'order/entities/customers/list.html', context)


@login_required
def create_customer(request):
    """Créer un client"""
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Client "{customer.name}" créé avec succès !')
            return redirect('order:list_customers')
    else:
        form = CustomerForm()
    
    context = {'form': form, 'action': 'create'}
    return render(request, 'order/entities/customers/form.html', context)


@login_required
def update_customer(request, customer_id):
    """Modifier un client"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Client "{customer.name}" modifié avec succès !')
            return redirect('order:list_customers')
    else:
        form = CustomerForm(instance=customer)
    
    context = {'form': form, 'customer': customer, 'action': 'update'}
    return render(request, 'order/entities/customers/form.html', context)


@login_required
def detail_customer(request, customer_id):
    """Détails d'un client"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Récupérer les commandes du client
    orders = customer.order_set.all().select_related('sales_executive').order_by('-created_at')
    
    # Statistiques
    total_orders = orders.count()
    total_amount = sum(order.total for order in orders)
    
    context = {
        'customer': customer,
        'orders': orders,
        'total_orders': total_orders,
        'total_amount': total_amount,
    }
    return render(request, 'order/entities/customers/detail.html', context)


@login_required
def delete_customer(request, customer_id):
    """Supprimer un client"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Vérifier si le client a des commandes
    orders_count = customer.order_set.count()
    
    if orders_count > 0:
        messages.error(request, f'Impossible de supprimer "{customer.name}". Il a {orders_count} commande(s).')
    else:
        customer_name = customer.name
        customer.delete()
        messages.success(request, f'Client "{customer_name}" supprimé avec succès !')
    
    return redirect('order:list_customers')


# ==================== APPORTEURS D'AFFAIRES ====================

@login_required
def list_sales_executives(request):
    """Liste des apporteurs d'affaires"""
    search = request.GET.get('search', '')
    sales_executives = SalesExecutive.objects.all().annotate(
        orders_count=Count('order')
    ).order_by('-created_at')
    
    if search:
        sales_executives = sales_executives.filter(
            Q(name__icontains=search) | Q(tel__icontains=search)
        )
    
    context = {
        'sales_executives': sales_executives,
        'search': search,
    }
    return render(request, 'order/entities/sales_executives/list.html', context)


@login_required
def create_sales_executive(request):
    """Créer un apporteur d'affaire"""
    if request.method == 'POST':
        form = SalesExecutiveForm(request.POST, request.FILES)
        if form.is_valid():
            sales_executive = form.save()
            messages.success(request, f'Apporteur "{sales_executive.name}" créé avec succès !')
            return redirect('order:list_sales_executives')
    else:
        form = SalesExecutiveForm()
    
    context = {'form': form, 'action': 'create'}
    return render(request, 'order/entities/sales_executives/form.html', context)


@login_required
def update_sales_executive(request, sales_executive_id):
    """Modifier un apporteur d'affaire"""
    sales_executive = get_object_or_404(SalesExecutive, id=sales_executive_id)
    
    if request.method == 'POST':
        form = SalesExecutiveForm(request.POST, request.FILES, instance=sales_executive)
        if form.is_valid():
            sales_executive = form.save()
            messages.success(request, f'Apporteur "{sales_executive.name}" modifié avec succès !')
            return redirect('order:list_sales_executives')
    else:
        form = SalesExecutiveForm(instance=sales_executive)
    
    context = {'form': form, 'sales_executive': sales_executive, 'action': 'update'}
    return render(request, 'order/entities/sales_executives/form.html', context)


@login_required
def detail_sales_executive(request, sales_executive_id):
    """Détails d'un apporteur d'affaire"""
    sales_executive = get_object_or_404(SalesExecutive, id=sales_executive_id)
    
    # Récupérer les commandes de l'apporteur
    orders = sales_executive.order_set.all().select_related('customer').order_by('-created_at')
    
    # Statistiques
    total_orders = orders.count()
    total_amount = sum(order.total for order in orders)
    
    context = {
        'sales_executive': sales_executive,
        'orders': orders,
        'total_orders': total_orders,
        'total_amount': total_amount,
    }
    return render(request, 'order/entities/sales_executives/detail.html', context)


@login_required
def delete_sales_executive(request, sales_executive_id):
    """Supprimer un apporteur d'affaire"""
    sales_executive = get_object_or_404(SalesExecutive, id=sales_executive_id)
    
    # Vérifier si l'apporteur a des commandes
    orders_count = sales_executive.order_set.count()
    
    if orders_count > 0:
        messages.error(request, f'Impossible de supprimer "{sales_executive.name}". Il a {orders_count} commande(s).')
    else:
        sales_executive_name = sales_executive.name
        sales_executive.delete()
        messages.success(request, f'Apporteur "{sales_executive_name}" supprimé avec succès !')
    
    return redirect('order:list_sales_executives')
