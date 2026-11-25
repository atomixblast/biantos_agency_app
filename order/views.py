from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.views.decorators.http import require_POST
from django.db import transaction
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

    order_articles = ArticleOrder.objects.filter(order=order).select_related('article')
    articles_details = [
        {
            'article': line.article,
            'qty': line.qty,
            'discount': line.discount,
            'unit_price': line.unit_price,
            'subtotal': line.subtotal,
            'discount_amount': line.discount_amount,
            'total': line.total,
        }
        for line in order_articles
    ]

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


# --------------------------------------------------------------------------- #
# Lignes de commande
# --------------------------------------------------------------------------- #

def _articles_payload():
    """Catalogue des articles pour le formulaire de commande (JS)."""
    return [
        {
            'id': article.id,
            'name': article.name,
            'ref': article.ref,
            'sale_price': article.sale_price,
            'photo': article.photo.url if article.photo else None,
        }
        for article in Article.objects.all()
    ]


def _existing_lines_payload(order):
    """Lignes d'une commande existante, avec leur prix figé."""
    return [
        {
            'id': line.article.id,
            'designation': line.article.name,
            'pu': float(line.unit_price),
            'qty': line.qty,
            'discount': float(line.discount),
            'ref': line.article.ref,
            'photo': line.article.photo.url if line.article.photo else None,
        }
        for line in ArticleOrder.objects.filter(order=order).select_related('article')
    ]


def _parse_lines(json_repr, frozen_prices=None):
    """Transforme le JSON envoyé par le formulaire en lignes de commande.

    Le prix n'est jamais pris chez le client : c'est le prix figé de la ligne
    si l'article était déjà dans la commande (``frozen_prices``), sinon le prix
    de vente actuel de l'article. La remise est par article, en %.
    Lève ``Article.DoesNotExist`` ou ``ValueError``.
    """
    frozen_prices = frozen_prices or {}
    data = json.loads(json_repr) if isinstance(json_repr, str) else json_repr
    lines = []
    for item in data or []:
        article = Article.objects.get(id=item.get('id'))
        qty = int(item.get('qty', 0))
        discount = float(item.get('discount', 0) or 0)
        if qty < 0 or not 0 <= discount <= 100:
            raise ValueError(f"Quantité ou remise invalide pour « {article.name} »")
        lines.append({
            'article': article,
            'qty': qty,
            'discount': discount,
            'unit_price': frozen_prices.get(article.id, article.sale_price),
        })
    return lines


def _compute_totals(order, lines):
    """Calcule le total et le montant des remises de la commande.

    1. remise par article (en %) sur chaque ligne ;
    2. remise sur la commande, sur ce qui reste : en % ou en montant FCFA
       selon ``order.global_discount_type``.
    Lève ``ValueError`` si la remise sur la commande dépasse le montant restant.
    """
    gross = sum(l['qty'] * l['unit_price'] for l in lines)
    lines_discount = sum(l['qty'] * l['unit_price'] * l['discount'] / 100 for l in lines)
    net = gross - lines_discount
    value = order.global_discount or 0
    if order.global_discount_type == Order.DISCOUNT_AMOUNT:
        if value > net + 0.005:
            raise ValueError(
                f"La remise sur la commande ({value:,.0f} FCFA) dépasse le total des articles ({net:,.0f} FCFA)".replace(',', ' ')
            )
        global_amount = value
    else:
        global_amount = net * value / 100
    order.global_discount_amount = round(global_amount, 2)
    order.total = round(net - global_amount, 2)
    order.discount = round(lines_discount + global_amount, 2)


def _save_lines(order, lines):
    """Enregistre la commande (totaux déjà calculés) et remplace ses lignes."""
    with transaction.atomic():
        order.save()
        ArticleOrder.objects.filter(order=order).delete()
        ArticleOrder.objects.bulk_create([ArticleOrder(order=order, **l) for l in lines])


@login_required
def create_order(request):
    form = AddOrderForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            order = form.save(commit=False)
            try:
                lines = _parse_lines(form.cleaned_data.get('json_repr'))
                _compute_totals(order, lines)
            except Article.DoesNotExist:
                messages.error(request, "Un des articles sélectionnés n'existe plus")
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                messages.error(request, str(e))
            else:
                _save_lines(order, lines)
                messages.success(request, "Commande créée avec succès!")
                return redirect('order:list_orders')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire")

    return render(request, 'order/add.html', {'form': form, 'articles': _articles_payload()})


@login_required
def update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    form = UpdateOrderForm(request.POST or None, instance=order)

    if request.method == 'POST':
        if form.is_valid():
            order = form.save(commit=False)
            # Les articles déjà présents gardent leur prix d'origine.
            frozen_prices = dict(ArticleOrder.objects.filter(order=order).values_list('article_id', 'unit_price'))
            try:
                lines = _parse_lines(form.cleaned_data.get('json_repr'), frozen_prices)
                _compute_totals(order, lines)
            except Article.DoesNotExist:
                messages.error(request, "Un des articles sélectionnés n'existe plus")
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                messages.error(request, str(e))
            else:
                _save_lines(order, lines)
                messages.success(request, "Commande mise à jour avec succès!")
                return redirect('order:list_orders')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire")

    return render(request, 'order/update.html', {
        'form': form,
        'order': order,
        'articles': _articles_payload(),
        'existing_articles': _existing_lines_payload(order),
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


def _report_filters(request):
    return {
        'start_date': request.GET.get('start_date'),
        'end_date': request.GET.get('end_date'),
        'customer': request.GET.get('customer'),
        'sales_executive': request.GET.get('sales_executive'),
        'articles': request.GET.getlist('articles'),
        'state': request.GET.get('state'),
        'payment_status': request.GET.get('payment_status'),
    }


def _filtered_orders(filters):
    """Commandes du bilan selon les filtres (liste Python, paiements préchargés)."""
    orders = Order.objects.select_related('customer', 'sales_executive').prefetch_related('payments')

    if filters['start_date']:
        orders = orders.filter(created_at__gte=filters['start_date'])
    if filters['end_date']:
        # Ajouter 1 jour pour inclure la date de fin
        end_date_obj = datetime.strptime(filters['end_date'], '%Y-%m-%d').date() + timedelta(days=1)
        orders = orders.filter(created_at__lt=end_date_obj)
    if filters['customer']:
        orders = orders.filter(customer_id=filters['customer'])
    if filters['sales_executive']:
        orders = orders.filter(sales_executive_id=filters['sales_executive'])
    if filters['articles']:
        # Commandes contenant au moins un des articles sélectionnés
        orders = orders.filter(articles__id__in=filters['articles']).distinct()
    if filters['state']:
        orders = orders.filter(state=filters['state'])

    payment_status = filters['payment_status']
    if payment_status == 'PAID':
        return [o for o in orders if o.is_fully_paid()]
    if payment_status == 'PARTIAL':
        return [o for o in orders if o.is_partially_paid()]
    if payment_status == 'UNPAID':
        return [o for o in orders if not o.is_fully_paid() and not o.is_partially_paid()]
    return list(orders)


def _pct(part, whole):
    return (part / whole * 100) if whole else 0


def _report_stats(orders):
    total_orders = len(orders)
    total_amount = sum(o.total for o in orders)
    total_paid = sum(o.get_total_paid() for o in orders)
    total_gross = sum(o.get_total_without_discount() for o in orders)
    total_global_discount = sum(o.global_discount_amount for o in orders)
    total_discount = sum(o.discount for o in orders)

    orders_paid = sum(1 for o in orders if o.is_fully_paid())
    orders_partial = sum(1 for o in orders if o.is_partially_paid())
    orders_done = sum(1 for o in orders if o.state == 'DONE')
    orders_pending = sum(1 for o in orders if o.state == 'PENDING')
    orders_cancelled = sum(1 for o in orders if o.state == 'CANCELED')

    return {
        'total_orders': total_orders,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_remaining': total_amount - total_paid,
        # Remises
        'total_gross': total_gross,
        'total_discount': total_discount,
        'total_lines_discount': total_discount - total_global_discount,
        'total_global_discount': total_global_discount,
        'discount_rate': _pct(total_discount, total_gross),
        'orders_with_discount': sum(1 for o in orders if o.discount > 0),
        # Statuts
        'orders_paid': orders_paid,
        'orders_partial': orders_partial,
        'orders_unpaid': total_orders - orders_paid - orders_partial,
        'orders_done': orders_done,
        'orders_pending': orders_pending,
        'orders_cancelled': orders_cancelled,
        'pct': {
            'paid': _pct(orders_paid, total_orders),
            'partial': _pct(orders_partial, total_orders),
            'unpaid': _pct(total_orders - orders_paid - orders_partial, total_orders),
            'done': _pct(orders_done, total_orders),
            'pending': _pct(orders_pending, total_orders),
            'cancelled': _pct(orders_cancelled, total_orders),
        },
        'payment_rate': _pct(total_paid, total_amount),
    }


@login_required
def report_orders(request):
    """Vue pour afficher le bilan des commandes avec filtres"""
    filters = _report_filters(request)
    orders = _filtered_orders(filters)

    context = {
        'orders': orders,
        **_report_stats(orders),
        # Listes pour les filtres
        'customers': Customer.objects.all().order_by('name'),
        'sales_executives': SalesExecutive.objects.all().order_by('name'),
        'articles': Article.objects.all().order_by('name'),
        'filters': filters,  # pour pré-remplir le formulaire
    }
    return render(request, 'order/report.html', context)


@login_required
def export_report_excel(request):
    """Exporte le bilan des commandes en CSV (compatible Excel)"""
    orders = _filtered_orders(_report_filters(request))
    stats = _report_stats(orders)

    def money(value):
        return f"{value:,.2f}".replace(',', ' ')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    filename = f"bilan_commandes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write('﻿')  # BOM UTF-8 pour Excel

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['BILAN DES COMMANDES'])
    writer.writerow([f"Exporté le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"])
    writer.writerow([])

    writer.writerow(['STATISTIQUES GLOBALES'])
    writer.writerow(['Total des commandes', stats['total_orders']])
    writer.writerow(['Montant avant remises', f"{money(stats['total_gross'])} FCFA"])
    writer.writerow(['Remises par article', f"{money(stats['total_lines_discount'])} FCFA"])
    writer.writerow(['Remises sur commandes', f"{money(stats['total_global_discount'])} FCFA"])
    writer.writerow(['Total des remises', f"{money(stats['total_discount'])} FCFA ({stats['discount_rate']:.1f} %)"])
    writer.writerow(['Montant total', f"{money(stats['total_amount'])} FCFA"])
    writer.writerow(['Total encaissé', f"{money(stats['total_paid'])} FCFA"])
    writer.writerow(['Reste à encaisser', f"{money(stats['total_remaining'])} FCFA"])
    writer.writerow([])

    writer.writerow([
        'Commande', 'Client', "Apporteur d'affaire",
        'Avant remises (FCFA)', 'Remises articles (FCFA)', 'Remise commande (FCFA)',
        'Total (FCFA)', 'Encaissé (FCFA)', 'Reste (FCFA)',
        'Statut Commande', 'Statut Paiement', 'Date',
    ])

    state_labels = {'DONE': 'Fait', 'PENDING': 'En cours', 'CANCELED': 'Annulé'}
    for order in orders:
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
            money(order.get_total_without_discount()),
            money(order.get_lines_discount_amount()),
            money(order.global_discount_amount),
            money(order.total),
            money(order.get_total_paid()),
            money(order.get_remaining_amount()),
            state_labels.get(order.state, order.state),
            status_pay,
            order.created_at.strftime('%d/%m/%Y'),
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
        articles_details.append({
            'article': item.article,
            'qty': item.qty,
            'discount': item.discount,
            'unit_price': item.unit_price,  # prix figé à la commande
            'discount_amount': item.discount_amount,
            'total': item.total,
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
