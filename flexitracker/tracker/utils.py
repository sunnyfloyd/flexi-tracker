def get_work_effort(queryset):
    deltas = [obj.end_time - obj.start_time for obj in queryset]
    # return round(sum(deltas[1:], start=deltas[0]).total_seconds() if deltas else 0, 1)
    return (
        str(round(sum(deltas[1:], start=deltas[0]).total_seconds() / 3600, 1) if deltas else 0) + 'h'
    )
