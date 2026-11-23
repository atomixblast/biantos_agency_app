from django.shortcuts import render, redirect

from target.forms import TargetForm
from target.models import Target

# Create your views here.


def list_targets(request):
    targets = Target.objects.all()
    return render(request, 'target/target_list.html', {'targets': targets})


def create_target(request):
    # Logic to add a new target
    if request.method == 'POST':
        form = TargetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('target:list_targets')
    else:
        form = TargetForm()
    return render(request, 'target/create_target.html', {'form': form, 'action': 'create'})



def update_target(request, target_id):
    target = Target.objects.get(id=target_id)
    # Logic to update the target
    if request.method == 'POST':
        form = TargetForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            return redirect('target:list_targets')
    else:
        form = TargetForm(instance=target)
    return render(request, 'target/create_target.html', {'form': form, 'action': 'update', 'target': target})