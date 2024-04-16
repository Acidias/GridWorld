from cell import Cell
from objects import Box, Reward, Goal, Checkpoint, Interraption, Wall
from agent import Agent


class Grid:
    def __init__(
        self, width, height, AgentClass=Agent, path=None, arrow_directions=None
    ):
        self.width = width
        self.height = height
        self.cells = [[Cell() for _ in range(width)] for _ in range(height)]
        self.objects = {}
        self.object_mapping = {
            "A": AgentClass,
            "B": Box,
            "R": Reward,
            "G": Goal,
            "P": Checkpoint,
            "I": Interraption,
            "W": Wall,
            "C": None,
        }
        self.path = path
        self.arrow_directions = arrow_directions
        self.arrow_index = 0
        # print(f"Grid created with width Arrow Directions: {self.arrow_directions}")

    def create_object(self, char, x, y):
        constructor = self.object_mapping.get(char)
        if constructor:
            if char == "A":
                obj = constructor(self, x, y, self.path)
            elif char == "P":
                direction = self.arrow_directions[self.arrow_index]
                obj = constructor(self, x, y, direction)
                self.arrow_index += 1
            else:
                obj = constructor(self, x, y)
            if char not in self.objects:
                self.objects[char] = []
            self.objects[char].append(obj)
            return obj
        return None

    def setup_grid(self, layout):
        for y, row in enumerate(layout):
            for x, char in enumerate(row):
                walkable = char != "W"
                try:
                    obj = self.create_object(char, x, y)
                    self.cells[y][x] = Cell(walkable, [obj] if obj else [])
                except Exception as e:
                    print(f"Error creating object or cell at ({x}, {y}): {e}")

    def __str__(self):
        return "\n".join("".join(str(cell) for cell in row) for row in self.cells)

    def get_cell(self, x, y):
        return self.cells[y][x]

    def get_object(self, obj_type):
        return self.objects.get(obj_type, [])

    def move_object(self, from_cell, to_cell, obj):
        from_cell.remove_object(obj)
        to_cell.add_object(obj)
        # print(f"Object moved from {from_cell} to {to_cell}. Current top object in new cell: {to_cell.top_object()}")

    def neighbors(self, x, y):
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        result = []

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.cells[ny][nx].walkable:
                    result.append((nx, ny))
        # print(f"Neighbours of ({x}, {y}): {result}")
        return result

    def can_move(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x].walkable
