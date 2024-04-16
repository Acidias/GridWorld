from objects import GridObject, Checkpoint


class Cell:
    def __init__(self, walkable=True, contained_objects=None):
        self.walkable = walkable
        self.contained_objects = contained_objects if contained_objects else []

    def add_object(self, obj):
        self.contained_objects.append(obj)

    def remove_object(self, obj):
        if obj in self.contained_objects:
            self.contained_objects.remove(obj)

    def top_object(self):
        if isinstance(self.contained_objects, list) and self.contained_objects:
            last_object = self.contained_objects[-1]
            if isinstance(last_object, GridObject):
                return last_object
        return None

    def __str__(self):
        if not self.walkable:
            return "■"
        top_obj = self.top_object()
        if top_obj:
            if isinstance(top_obj, Checkpoint):
                arrow_map = {"up": "↑", "down": "↓", "left": "←", "right": "→"}
                return arrow_map.get(top_obj.arrow_direction, "_")
            return top_obj.name[0]
        return "_"
