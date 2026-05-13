from django.shortcuts import render
from .models import FacultyMember, Instrument

_SMALL = 3      # ≤ this many members → eligible for side-by-side packing
_MAX_ROW = 4    # max combined cards in one packed row


def faculty_list(request):
    all_members = list(
        FacultyMember.objects.filter(is_active=True)
        .select_related("instrument")
        .order_by("sort_order", "name")
    )
    groups = []
    assigned = set()
    for instrument in Instrument.objects.order_by("sort_order", "name"):
        group = [m for m in all_members if m.instrument_id == instrument.pk]
        if group:
            for m in group:
                assigned.add(m.pk)
            groups.append((instrument.name, group))
    leftover = [m for m in all_members if m.pk not in assigned]
    if leftover:
        groups.append(("Other", leftover))

    # Build layout rows: full-width sections stay as-is;
    # consecutive small sections are batched into a single packed row.
    rows = []
    pending = []

    def flush():
        if pending:
            rows.append({"type": "row", "groups": list(pending)})
            del pending[:]

    for label, group in groups:
        if len(group) <= _SMALL:
            total = sum(len(g[1]) for g in pending)
            if pending and total + len(group) > _MAX_ROW:
                flush()
            pending.append((label, group))
        else:
            flush()
            rows.append({"type": "full", "label": label, "members": group})
    flush()

    return render(request, "faculty/faculty.html", {"faculty_rows": rows})
