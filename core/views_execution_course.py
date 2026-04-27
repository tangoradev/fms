from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import PlanificationCourse, ExecutionCourse
from .forms import ExecutionCourseForm
from django.urls import reverse
from django.db import transaction

@login_required
def execution_course_create(request, planification_id):
    planification = get_object_or_404(PlanificationCourse, pk=planification_id)
    # Seul le chauffeur affecté peut saisir l'exécution
    if planification.utilisateur != request.user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à saisir l'exécution de cette course.")
    # Un seul enregistrement d'exécution par planification
    if ExecutionCourse.objects.filter(id_planification=planification).exists():
        return redirect(reverse('planification_course_detail', args=[planification_id]))
    if request.method == 'POST':
        form = ExecutionCourseForm(request.POST, planification=planification)
        if form.is_valid():
            with transaction.atomic():
                execution = form.save(commit=False)
                execution.id_planification = planification
                execution.save()

                # Mettre à jour le kilométrage du véhicule si progression
                vehicule = planification.vehicule
                if execution.kilometrage_fin > vehicule.kilometrage:
                    vehicule.kilometrage = execution.kilometrage_fin
                    vehicule.save(update_fields=['kilometrage'])

                # Clôturer la planification et la demande associée
                planification.statut = 'terminée'
                planification.save(update_fields=['statut'])

                if planification.demande:
                    planification.demande.statut = 'terminée'
                    planification.demande.save(update_fields=['statut'])

            return redirect(reverse('planification_course_detail', args=[planification_id]))
    else:
        form = ExecutionCourseForm(planification=planification)
    retour_url = reverse('planification_course_detail', args=[planification_id])
    return render(request, 'core/planification/execution_course_form.html', {'form': form, 'retour_url': retour_url, 'planification': planification})
