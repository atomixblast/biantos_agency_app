from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, Q
from django.template.loader import render_to_string
import json
import csv
from datetime import date, datetime, timedelta

from order.forms import AddOrderForm, UpdateOrderForm
from order.models import Order, ArticleOrder, Article, Payment, Customer, SalesExecutive

# Create your views here.

@login_required
def list_orders(request):
    orders = Order.objects.all().select_related('customer', 'sales_executive').order_by('-created_at')
    return render(request, 'order/list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Vue de détail d'une commande (pour modal)"""
    order = get_object_or_404(Order, id=order_id)
    
    # Récupérer les articles de la commande
    order_articles = ArticleOrder.objects.filter(order=order).select_related('article')
    
    # Calculer les détails
    articles_details = []
    for order_article in order_articles:
        subtotal = order_article.qty * order_article.article.sale_price
        discount_amount = subtotal * (order_article.discount / 100)
        total = subtotal - discount_amount
        
        articles_details.append({
            'article': order_article.article,
            'qty': order_article.qty,
            'discount': order_article.discount,
            'unit_price': order_article.article.sale_price,
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'total': total
        })
    
    # Récupérer les paiements
    payments = order.payments.all().order_by('-payment_date', '-created_at')
    
    context = {
        'order': order,
        'articles_details': articles_details,
        'total_without_discount': order.get_total_without_discount(),
        'total_with_discount': order.get_total_with_discount(),
        'payments': payments,
        'total_paid': order.get_total_paid(),
        'remaining_amount': order.get_remaining_amount(),
        'payment_status': order.get_payment_status(),
    }
    
    return render(request, 'order/detail_modal.html', context)


def create_order(request):
    if request.method == 'POST':
        form = AddOrderForm(request.POST)
        if form.is_valid():
            # Create the order instance but don't save yet
            order = form.save(commit=False)
            
            # Parse the JSON representation of articles
            json_repr = form.cleaned_data.get('json_repr')
            
            # Calculate total from articles using DATABASE prices (security)
            total_without_discount = 0
            total_discount = 0
            
            if json_repr:
                try:
                    articles_data = json.loads(json_repr) if isinstance(json_repr, str) else json_repr
                    
                    # Calculate totals using DATABASE prices, not client prices
                    for article_data in articles_data:
                        article_id = article_data.get('id')
                        qty = int(article_data.get('qty', 0))
                        discount = float(article_data.get('discount', 0))
                        
                        # SECURITY: Get price from database, don't trust client
                        try:
                            article = Article.objects.get(id=article_id)
                            pu = article.sale_price  # Use DB price
                            
                            subtotal = qty * pu
                            discount_amount = subtotal * (discount / 100)
                            total_without_discount += subtotal
                            total_discount += discount_amount
                        except Article.DoesNotExist:
                            messages.error(request, f"Article avec l'ID {article_id} n'existe pas")
                            return render(request, 'order/add.html', {
                                'form': form,
                                'articles': list(Article.objects.all().values('id', 'name', 'ref', 'sale_price'))
                            })
                    
                    # Set the order total (after discount)
                    order.total = total_without_discount - total_discount
                    
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    messages.error(request, f"Erreur lors du traitement des articles: {str(e)}")
                    return render(request, 'order/add.html', {
                        'form': form,
                        'articles': list(Article.objects.all().values('id', 'name', 'ref', 'sale_price'))
                    })
            
            # Save the order
            order.save()
            
            # Create ArticleOrder entries
            if json_repr:
                try:
                    articles_data = json.loads(json_repr) if isinstance(json_repr, str) else json_repr
                    
                    for article_data in articles_data:
                        article_id = article_data.get('id')
                        qty = int(article_data.get('qty', 0))
                        discount = float(article_data.get('discount', 0))
                        
                        try:
                            article = Article.objects.get(id=article_id)
                            ArticleOrder.objects.create(
                                article=article,
                                order=order,
                                qty=qty,
                                discount=discount
                            )
                        except Article.DoesNotExist:
                            messages.warning(request, f"Article avec l'ID {article_id} n'existe pas")
                            
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    messages.error(request, f"Erreur lors de la création des articles: {str(e)}")
            
            messages.success(request, "Commande créée avec succès!")
            return redirect('order:list_orders')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire")
            # Pass articles even on form error
            articles = []
            for article in Article.objects.all():
                articles.append({
                    'id': article.id,
                    'name': article.name,
                    'ref': article.ref,
                    'sale_price': article.sale_price,
                    'photo': article.photo.url if article.photo else None
                })
            return render(request, 'order/add.html', {'form': form, 'articles': articles})
    else:
        form = AddOrderForm()
    
    # Fetch articles from database with photos
    articles = []
    for article in Article.objects.all():
        articles.append({
            'id': article.id,
            'name': article.name,
            'ref': article.ref,
            'sale_price': article.sale_price,
            'photo': article.photo.url if article.photo else None
        })
    
    return render(request, 'order/add.html', {'form': form, 'articles': articles})


@login_required
def update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = UpdateOrderForm(request.POST, instance=order)
        if form.is_valid():
            # Create the order instance but don't save yet
            order = form.save(commit=False)
            
            # Parse the JSON representation of articles
            json_repr = form.cleaned_data.get('json_repr')
            
            # Calculate total from articles using DATABASE prices (security)
            total_without_discount = 0
            total_discount = 0
            
            if json_repr:
                try:
                    articles_data = json.loads(json_repr) if isinstance(json_repr, str) else json_repr
                    
                    # Calculate totals using DATABASE prices, not client prices
                    for article_data in articles_data:
                        article_id = article_data.get('id')
                        qty = int(article_data.get('qty', 0))
                        discount = float(article_data.get('discount', 0))
                        
                        # SECURITY: Get price from database, don't trust client
                        try:
                            article = Article.objects.get(id=article_id)
                            pu = article.sale_price  # Use DB price
                            
                            subtotal = qty * pu
                            discount_amount = subtotal * (discount / 100)
                            total_without_discount += subtotal
                            total_discount += discount_amount
                        except Article.DoesNotExist:
                            messages.error(request, f"Article avec l'ID {article_id} n'existe pas")
                            return render(request, 'order/update.html', {
                                'form': form,
                                'order': order,
                                'articles': list(Article.objects.all().values('id', 'name', 'ref', 'sale_price')),
                                'existing_articles': []
                            })
                    
                    # Set the order total (after discount)
                    order.total = total_without_discount - total_discount
                    
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    messages.error(request, f"Erreur lors du traitement des articles: {str(e)}")
                    return render(request, 'order/update.html', {
                        'form': form,
                        'order': order,
                        'articles': list(Article.objects.all().values('id', 'name', 'ref', 'sale_price')),
                        'existing_articles': []
                    })
            
            # Save the order
            order.save()
            
            # Delete existing ArticleOrder entries and create new ones
            ArticleOrder.objects.filter(order=order).delete()
            
            if json_repr:
                try:
                    articles_data = json.loads(json_repr) if isinstance(json_repr, str) else json_repr
                    
                    for article_data in articles_data:
                        article_id = article_data.get('id')
                        qty = int(article_data.get('qty', 0))
                        discount = float(article_data.get('discount', 0))
                        
                        try:
                            article = Article.objects.get(id=article_id)
                            ArticleOrder.objects.create(
                                article=article,
                                order=order,
                                qty=qty,
                                discount=discount
                            )
                        except Article.DoesNotExist:
                            messages.warning(request, f"Article avec l'ID {article_id} n'existe pas")
                            
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    messages.error(request, f"Erreur lors de la création des articles: {str(e)}")
            
            messages.success(request, "Commande mise à jour avec succès!")
            return redirect('order:list_orders')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire")
            # Get existing articles for this order
            existing_articles = ArticleOrder.objects.filter(order=order).select_related('article')
            existing_articles_data = [
                {
                    'id': ao.article.id,
                    'designation': ao.article.name,
                    'pu': float(ao.article.sale_price),
                    'qty': ao.qty,
                    'discount': float(ao.discount),
                    'ref': ao.article.ref,
                    'photo': ao.article.photo.url if ao.article.photo else None
                }
                for ao in existing_articles
            ]
            # Pass articles even on form error with photos
            articles = []
            for article in Article.objects.all():
                articles.append({
                    'id': article.id,
                    'name': article.name,
                    'ref': article.ref,
                    'sale_price': article.sale_price,
                    'photo': article.photo.url if article.photo else None
                })
            return render(request, 'order/update.html', {
                'form': form,
                'order': order,
                'articles': articles,
                'existing_articles': existing_articles_data
            })
    else:
        form = UpdateOrderForm(instance=order)
    
    # Fetch articles from database with photos
    articles = []
    for article in Article.objects.all():
        articles.append({
            'id': article.id,
            'name': article.name,
            'ref': article.ref,
            'sale_price': article.sale_price,
            'photo': article.photo.url if article.photo else None
        })
    
    # Get existing articles for this order
    existing_articles = ArticleOrder.objects.filter(order=order).select_related('article')
    existing_articles_data = [
        {
            'id': ao.article.id,
            'designation': ao.article.name,
            'pu': float(ao.article.sale_price),
            'qty': ao.qty,
            'discount': float(ao.discount),
            'ref': ao.article.ref,
            'photo': ao.article.photo.url if ao.article.photo else None
        }
        for ao in existing_articles
    ]
    
    return render(request, 'order/update.html', {
        'form': form,
        'order': order,
        'articles': articles,
        'existing_articles': existing_articles_data
    })


@login_required
@require_POST
def change_order_status(request, order_id):
    """Vue pour changer le statut d'une commande"""
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Récupérer les données du POST
        new_status = request.POST.get('status')
        state_date = request.POST.get('state_date')
        
        # Valider le statut
        valid_statuses = ['PENDING', 'DONE', 'CANCELED']
        if new_status not in valid_statuses:
            return JsonResponse({
                'success': False,
                'message': 'Statut invalide'
            }, status=400)
        
        # Valider la date
        if not state_date:
            return JsonResponse({
                'success': False,
                'message': 'La date de changement de statut est requise'
            }, status=400)
        
        # Mettre à jour la commande
        order.state = new_status
        order.state_date = state_date
        order.save()
        
        # Retourner le statut formaté pour l'affichage
        status_display = order.get_state_display()
        
        return JsonResponse({
            'success': True,
            'message': f'Statut changé en "{status_display}" avec succès',
            'new_status': new_status,
            'status_display': status_display,
            'state_date': state_date
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=500)


@login_required
@require_POST
def add_payment(request, order_id):
    """Vue pour ajouter un paiement à une commande"""
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Récupérer les données du POST
        amount = float(request.POST.get('amount', 0))
        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method', 'CASH')
        reference = request.POST.get('reference', '')
        notes = request.POST.get('notes', '')
        
        # Validation
        if amount <= 0:
            return JsonResponse({
                'success': False,
                'message': 'Le montant doit être supérieur à zéro'
            }, status=400)
        
        if not payment_date:
            return JsonResponse({
                'success': False,
                'message': 'La date de paiement est requise'
            }, status=400)
        
        # Vérifier que le montant ne dépasse pas le reste à payer
        remaining = order.get_remaining_amount()
        if amount > remaining:
            return JsonResponse({
                'success': False,
                'message': f'Le montant ({amount} FCFA) dépasse le reste à payer ({remaining} FCFA)'
            }, status=400)
        
        # Créer le paiement
        payment = Payment.objects.create(
            order=order,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference=reference,
            notes=notes,
            created_by=request.user
        )
        
        # Mettre à jour le champ cashed de la commande
        order.cashed = order.get_total_paid()
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Paiement de {amount} FCFA ajouté avec succès',
            'payment': {
                'id': payment.id,
                'amount': payment.amount,
                'payment_date': str(payment.payment_date),
                'payment_method': payment.get_payment_method_display(),
                'reference': payment.reference,
                'notes': payment.notes
            },
            'order_stats': {
                'total': order.total,
                'total_paid': order.get_total_paid(),
                'remaining': order.get_remaining_amount()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=500)


@login_required
@require_POST
def delete_payment(request, payment_id):
    """Vue pour supprimer un paiement"""
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        order = payment.order
        amount = payment.amount
        
        # Supprimer le paiement
        payment.delete()
        
        # Mettre à jour le champ cashed de la commande
        order.cashed = order.get_total_paid()
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Paiement de {amount} FCFA supprimé avec succès',
            'order_stats': {
                'total': order.total,
                'total_paid': order.get_total_paid(),
                'remaining': order.get_remaining_amount()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=500)


@login_required
def report_orders(request):
    """Vue pour afficher le bilan des commandes avec filtres"""
    
    # Récupérer tous les ordres par défaut
    orders = Order.objects.all().select_related('customer', 'sales_executive').prefetch_related('payments', 'articles')
    
    # Filtres
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    customer_id = request.GET.get('customer')
    sales_executive_id = request.GET.get('sales_executive')
    article_ids = request.GET.getlist('articles')
    state = request.GET.get('state')
    payment_status = request.GET.get('payment_status')
    
    # Appliquer les filtres
    if start_date:
        orders = orders.filter(created_at__gte=start_date)
    
    if end_date:
        # Ajouter 1 jour pour inclure la date de fin
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() + timedelta(days=1)
        orders = orders.filter(created_at__lt=end_date_obj)
    
    if customer_id:
        orders = orders.filter(customer_id=customer_id)
    
    if sales_executive_id:
        orders = orders.filter(sales_executive_id=sales_executive_id)
    
    if article_ids:
        # Filtrer les commandes qui contiennent au moins un des articles sélectionnés
        orders = orders.filter(articles__id__in=article_ids).distinct()
    
    if state:
        orders = orders.filter(state=state)
    
    # Filtrer par statut de paiement
    if payment_status == 'PAID':
        # Commandes entièrement payées
        orders = [order for order in orders if order.is_fully_paid()]
    elif payment_status == 'PARTIAL':
        # Commandes partiellement payées
        orders = [order for order in orders if order.is_partially_paid()]
    elif payment_status == 'UNPAID':
        # Commandes non payées
        orders = [order for order in orders if not order.is_fully_paid() and not order.is_partially_paid()]
    else:
        orders = list(orders)
    
    # Calculer les statistiques
    total_orders = len(orders)
    total_amount = sum(order.total for order in orders)
    total_paid = sum(order.get_total_paid() for order in orders)
    total_remaining = sum(order.get_remaining_amount() for order in orders)
    total_discount = sum(order.discount for order in orders)
    
    # Statistiques supplémentaires
    orders_paid = sum(1 for order in orders if order.is_fully_paid())
    orders_partial = sum(1 for order in orders if order.is_partially_paid())
    orders_unpaid = sum(1 for order in orders if not order.is_fully_paid() and not order.is_partially_paid())
    
    # Statistiques par statut de commande
    orders_done = sum(1 for order in orders if order.state == 'DONE')
    orders_pending = sum(1 for order in orders if order.state == 'PENDING')
    orders_cancelled = sum(1 for order in orders if order.state == 'CANCELLED')
    
    # Récupérer les listes pour les filtres
    customers = Customer.objects.all().order_by('name')
    sales_executives = SalesExecutive.objects.all().order_by('name')
    articles = Article.objects.all().order_by('name')
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'total_discount': total_discount,
        'orders_paid': orders_paid,
        'orders_partial': orders_partial,
        'orders_unpaid': orders_unpaid,
        'orders_done': orders_done,
        'orders_pending': orders_pending,
        'orders_cancelled': orders_cancelled,
        'customers': customers,
        'sales_executives': sales_executives,
        'articles': articles,
        # Filtres appliqués (pour pré-remplir le formulaire)
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'customer': customer_id,
            'sales_executive': sales_executive_id,
            'articles': article_ids,
            'state': state,
            'payment_status': payment_status,
        }
    }
    
    return render(request, 'order/report.html', context)


@login_required
def export_report_excel(request):
    """Exporte le bilan des commandes en CSV (compatible Excel)"""
    
    # Récupérer les mêmes filtres que la vue report_orders
    orders = Order.objects.all().select_related('customer', 'sales_executive').prefetch_related('payments', 'articles')
    
    # Appliquer les filtres
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    customer_id = request.GET.get('customer')
    sales_executive_id = request.GET.get('sales_executive')
    article_ids = request.GET.getlist('articles')
    state = request.GET.get('state')
    payment_status = request.GET.get('payment_status')
    
    if start_date:
        orders = orders.filter(created_at__gte=start_date)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() + timedelta(days=1)
        orders = orders.filter(created_at__lt=end_date_obj)
    
    if customer_id:
        orders = orders.filter(customer_id=customer_id)
    
    if sales_executive_id:
        orders = orders.filter(sales_executive_id=sales_executive_id)
    
    if article_ids:
        orders = orders.filter(articles__id__in=article_ids).distinct()
    
    if state:
        orders = orders.filter(state=state)
    
    # Filtrer par statut de paiement
    if payment_status == 'PAID':
        orders = [order for order in orders if order.is_fully_paid()]
    elif payment_status == 'PARTIAL':
        orders = [order for order in orders if order.is_partially_paid()]
    elif payment_status == 'UNPAID':
        orders = [order for order in orders if not order.is_fully_paid() and not order.is_partially_paid()]
    else:
        orders = list(orders)
    
    # Calculer les statistiques
    total_orders = len(orders)
    total_amount = sum(order.total for order in orders)
    total_paid = sum(order.get_total_paid() for order in orders)
    total_remaining = sum(order.get_remaining_amount() for order in orders)
    total_discount = sum(order.discount for order in orders)
    
    # Créer la réponse CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    filename = f"bilan_commandes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Ajouter le BOM UTF-8 pour Excel
    response.write('\ufeff')
    
    writer = csv.writer(response, delimiter=';')
    
    # Titre
    writer.writerow(['BILAN DES COMMANDES'])
    writer.writerow([f"Exporté le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"])
    writer.writerow([])
    
    # Statistiques globales
    writer.writerow(['STATISTIQUES GLOBALES'])
    writer.writerow(['Total des commandes', total_orders])
    writer.writerow(['Montant total', f"{total_amount:,.2f} FCFA".replace(',', ' ')])
    writer.writerow(['Total encaissé', f"{total_paid:,.2f} FCFA".replace(',', ' ')])
    writer.writerow(['Reste à encaisser', f"{total_remaining:,.2f} FCFA".replace(',', ' ')])
    writer.writerow(['Total des remises', f"{total_discount:,.2f} FCFA".replace(',', ' ')])
    writer.writerow([])
    
    # En-têtes du tableau
    writer.writerow([
        'Commande',
        'Client',
        'Apporteur d\'affaire',
        'Total (FCFA)',
        'Encaissé (FCFA)',
        'Reste (FCFA)',
        'Statut Commande',
        'Statut Paiement',
        'Date'
    ])
    
    # Données
    for order in orders:
        # Statut commande
        if order.state == 'DONE':
            status_cmd = 'Fait'
        elif order.state == 'PENDING':
            status_cmd = 'En cours'
        else:
            status_cmd = 'Annulé'
        
        # Statut paiement
        if order.is_fully_paid():
            status_pay = 'Payé'
        elif order.is_partially_paid():
            status_pay = 'Partiel'
        else:
            status_pay = 'Non payé'
        
        writer.writerow([
            order.name,
            order.customer.name if order.customer else '-',
            order.sales_executive.name if order.sales_executive else '-',
            f"{order.total:,.2f}".replace(',', ' '),
            f"{order.get_total_paid():,.2f}".replace(',', ' '),
            f"{order.get_remaining_amount():,.2f}".replace(',', ' '),
            status_cmd,
            status_pay,
            order.created_at.strftime('%d/%m/%Y')
        ])
    
    return response


@login_required
def generate_invoice(request, order_id):
    """Génère une facture/reçu pour une commande"""
    order = get_object_or_404(Order, id=order_id)
    
    # Récupérer les articles de la commande
    articles_details = []
    article_orders = ArticleOrder.objects.filter(order=order).select_related('article')
    
    for item in article_orders:
        # Calculer les valeurs
        unit_price = item.article.sale_price
        subtotal = unit_price * item.qty
        discount_amount = subtotal * (item.discount / 100) if item.discount > 0 else 0
        total = subtotal - discount_amount
        
        articles_details.append({
            'article': item.article,
            'qty': item.qty,
            'discount': item.discount,
            'unit_price': unit_price,
            'discount_amount': discount_amount,
            'total': total,
        })
    
    # Récupérer les paiements
    payments = Payment.objects.filter(order=order).order_by('-payment_date')
    
    # Calculer les totaux
    total_paid = order.get_total_paid()
    remaining_amount = order.get_remaining_amount()
    total_without_discount = sum(item['unit_price'] * item['qty'] for item in articles_details)
    
    context = {
        'order': order,
        'articles_details': articles_details,
        'payments': payments,
        'total_paid': total_paid,
        'remaining_amount': remaining_amount,
        'total_without_discount': total_without_discount,
        'generated_date': datetime.now(),
    }
    
    return render(request, 'order/invoice.html', context)


@login_required
def calendar_orders(request):
    """Vue calendrier des commandes"""
    orders = Order.objects.all().select_related('customer', 'sales_executive').order_by('-created_at')
    
    # Préparer les données pour le calendrier (format JSON)
    calendar_events = []
    for order in orders:
        # Couleur selon le statut
        if order.state == 'DONE':
            color = '#14b8a6'  # teal
        elif order.state == 'PENDING':
            color = '#f59e0b'  # orange
        else:
            color = '#ef4444'  # red
        
        # Couleur selon le paiement
        if order.is_fully_paid():
            border_color = '#10b981'  # green
        elif order.is_partially_paid():
            border_color = '#f59e0b'  # orange
        else:
            border_color = '#6b7280'  # gray
        
        calendar_events.append({
            'id': order.id,
            'title': order.name,
            'start': order.created_at.isoformat(),
            'backgroundColor': color,
            'borderColor': border_color,
            'extendedProps': {
                'customer': order.customer.name if order.customer else '-',
                'total': float(order.total),
                'state': order.get_state_display(),
                'is_paid':  1 if order.is_fully_paid() else 0,
            }
        })
    
    context = {
        'calendar_events': calendar_events,
    }
    
    return render(request, 'order/calendar.html', context)
