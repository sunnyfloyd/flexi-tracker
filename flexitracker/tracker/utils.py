def get_work_effort(queryset):
    deltas = [obj.end_time - obj.start_time for obj in queryset]
    # return round(sum(deltas[1:], start=deltas[0]).total_seconds() if deltas else 0, 1)
    return (
        round(sum(deltas[1:], start=deltas[0]).total_seconds() / 60, 1) if deltas else 0
    )


def add_pagination_context(context):
    per_page = context["paginator"].per_page
    page_obj = context["page_obj"]
    context["showing_first"] = per_page * (page_obj.number - 1) + 1
    context["showing_end"] = context["showing_first"] + len(page_obj) - 1
    return context
