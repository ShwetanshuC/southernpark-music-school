from django.shortcuts import render
from .models import FacultyMember, Instrument


def faculty_list(request):
    members = list(FacultyMember.objects.filter(is_active=True).select_related("instrument").order_by("sort_order", "name"))
    groups = []
    assigned = set()
    for instrument in Instrument.objects.order_by("sort_order", "name"):
        group = [m for m in members if m.instrument_id == instrument.pk]
        if group:
            for m in group:
                assigned.add(m.pk)
            groups.append((instrument.name, group))
    leftover = [m for m in members if m.pk not in assigned]
    if leftover:
        groups.append(("Other", leftover))
    return render(request, "faculty/faculty.html", {"faculty_groups": groups})
