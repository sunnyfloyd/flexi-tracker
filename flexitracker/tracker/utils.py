def get_work_effort(queryset):
    """
    Calculates sum of work effort from the provided collection of TimeEntry
    objects.

    Args:
        queryset ([QuerySet]): collection of TimeEntry objects

    Returns:
        [int]: sum of work effort from the passed QuerySet (in seconds)
    """
    deltas = [obj.end_time - obj.start_time for obj in queryset]
    deltas_sum = sum(deltas[1:], start=deltas[0]).total_seconds() if deltas else 0
    return int(round(deltas_sum / 60, 0))


def add_pagination_context(context):
    """
    Enriches passed context with additional pagination variables that contain range
    of entries displayed on the current page.

    Args:
        context ([dict]): view's context

    Returns:
        [dict]: context enriched with pagination related variables
    """    
    per_page = context["paginator"].per_page
    page_obj = context["page_obj"]
    context["showing_first"] = per_page * (page_obj.number - 1) + 1 if page_obj else 0
    context["showing_end"] = (
        context["showing_first"] + len(page_obj) - 1 if page_obj else 0
    )
    return context
