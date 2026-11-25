from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from order.models import SalesExecutive
from target import services
from target.forms import TargetForm
from target.models import Target


@login_required
def list_targets(request):
    today = date.today()

    targets = Target.objects.select_related('article', 'sales_executive')
    scope = request.GET.get('sales_executive', '')
    if scope == 'agency':
        targets = targets.filter(sales_executive__isnull=True)
    elif scope.isdigit():
        targets = targets.filter(sales_executive_id=int(scope))
    else:
        scope = ''

    tab = request.GET.get('tab', services.TAB_CURRENT)
    if tab not in services.TABS:
        tab = services.TAB_CURRENT

    progress = [services.build_progress(t, today) for t in targets]
    by_tab = {key: [p for p in progress if p.tab == key] for key in services.TABS}

    context = {
        'today': today,
        'tab': tab,
        'tab_counts': {key: len(items) for key, items in by_tab.items()},
        'groups': services.group_by_period(by_tab[tab], tab),
        'kpis': services.compute_kpis(by_tab[services.TAB_CURRENT]),
        'sales_executives': SalesExecutive.objects.order_by('name'),
        'scope': scope,
        'has_targets': bool(progress),
    }
    return render(request, 'target/target_list.html', context)


@login_required
def create_target(request):
    if request.method == 'POST':
        form = TargetForm(request.POST)
        if form.is_valid():
            target = form.save()
            messages.success(request, f'Objectif « {target.name} » créé avec succès.')
            return redirect('target:list_targets')
    else:
        form = TargetForm()
    return render(request, 'target/create_target.html', {'form': form, 'action': 'create'})


@login_required
def update_target(request, target_id):
    target = get_object_or_404(Target, id=target_id)
    if request.method == 'POST':
        form = TargetForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, f'Objectif « {target.name} » mis à jour.')
            return redirect('target:list_targets')
    else:
        form = TargetForm(instance=target)
    return render(request, 'target/create_target.html', {'form': form, 'action': 'update', 'target': target})


@login_required
@require_POST
def delete_target(request, target_id):
    target = get_object_or_404(Target, id=target_id)
    name = target.name
    target.delete()
    messages.success(request, f'Objectif « {name} » supprimé.')
    return redirect('target:list_targets')
