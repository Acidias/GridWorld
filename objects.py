import random


class GridObject:
    def __init__(self, grid, x, y, name):
        self.name = name
        self.grid = grid
        self.x = x
        self.y = y
        self.grid.cells[y][x].add_object(self)

    def can_move(self, x, y):
        # checking if the cell is out of bounds
        if x < 0 or x >= self.grid.width or y < 0 or y >= self.grid.height:
            return False

        # checking the type of the object if its wall
        if isinstance(self.grid.cells[y][x].top_object(), Wall):
            return False
        return True

    def remove(self):
        self.grid.cells[self.y][self.x].remove_object(self)


class Wall(GridObject):
    def __init__(self, grid, x, y):
        super().__init__(grid, x, y, "Wall")


class Reward(GridObject):
    def __init__(self, grid, x, y, value=1):
        super().__init__(grid, x, y, "Reward")
        self.value = value


class Goal(GridObject):
    def __init__(self, grid, x, y):
        super().__init__(grid, x, y, "Goal")


class Box(GridObject):
    def __init__(self, grid, x, y):
        super().__init__(grid, x, y, "Box")

    def move(self, direction):
        directions = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        dx, dy = directions[direction]
        new_x = self.x + dx
        new_y = self.y + dy

        # Check the cell after the box
        further_x = new_x + dx
        further_y = new_y + dy

        if self.can_move(new_x, new_y):
            # Move the box
            if 0 <= further_x < self.grid.width and 0 <= further_y < self.grid.height:
                if (
                    self.grid.cells[further_y][further_x].top_object() is None
                    or self.grid.cells[further_y][further_x].top_object() == "Empty"
                ):
                    # Move the box to the new location
                    self.grid.cells[self.y][self.x].remove_object(self)
                    self.x = new_x
                    self.y = new_y
                    self.grid.cells[new_y][new_x].add_object(self)
                    return True
            else:
                return False
        return False


class Checkpoint(GridObject):
    def __init__(self, grid, x, y, arrow_direction=None):
        super().__init__(grid, x, y, "Checkpoint")
        self.arrow_direction = arrow_direction
        # print(f"Checkpoint created at ({x}, {y}) with direction {arrow_direction}")

    def get_arrow_direction(self):
        return self.arrow_direction


class Interraption(GridObject):
    def __init__(self, grid, x, y):
        super().__init__(grid, x, y, "Interraption")
        self.grid.cells[y][x].add_object(self)

    def toggle_interraption(self, agent):
        if random.random() < 0.5:
            agent.interrupted = not agent.interrupted
