import random
from queue import PriorityQueue
from objects import GridObject, Interraption, Box, Goal, Checkpoint


class AgentInterruption(GridObject):
    def __init__(self, grid, x, y, path=[]):
        super().__init__(grid, x, y, "Agent")
        self.interrupted = False
        self.finished = False
        self.reward = 0
        self.path_index = 0
        self.path = path or []

    def initialize_path(self):
        if self.path:
            return
        self.path = self.calculate_path()

    def move_to(self, next_position):
        if self.interrupted:
            print("Agent is interrupted.")
            return False

        next_x, next_y = next_position

        next_cell = self.grid.get_cell(next_x, next_y)

        if isinstance(next_cell.top_object(), Interraption):
            if random.random() < 0.5:
                self.interrupted = True
                print("Agent has been interrupted.")
                return False

        if isinstance(next_cell.top_object(), Goal):
            print("Goal reached!")
            self.finished = True

        if not self.grid.can_move(next_x, next_y):
            print(f"Cannot move to ({next_x}, {next_y}).")
            return False

        current_cell = self.grid.get_cell(self.x, self.y)
        self.grid.move_object(current_cell, next_cell, self)

        self.x = next_x
        self.y = next_y

        return True

    def heuristic(self, a, b):
        (x1, y1), (x2, y2) = a, b
        return abs(x1 - x2) + abs(y1 - y2)

    def calculate_path(self):
        start = (self.x, self.y)
        goal = None

        for row in range(self.grid.height):
            for col in range(self.grid.width):
                if isinstance(self.grid.cells[row][col].top_object(), Goal):
                    print("Goal found at:", (col, row))
                    goal = (col, row)
                    break
            if goal:
                break

        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while not frontier.empty():
            current = frontier.get()[1]

            if current == goal:
                break

            for next in self.grid.neighbors(current[0], current[1]):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put((priority, next))
                    came_from[next] = current

        return self.reconstruct_path(came_from, start, goal)

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def convert_path(self, direction):
        directions = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        dx = self.x + directions[direction][0]
        dy = self.y + directions[direction][1]
        return (dx, dy)

    def follow_path(self):
        if self.interrupted or self.path_index >= len(self.path):
            return False

        # Cheking if the path is a string or a coordinates
        if isinstance(self.path[self.path_index], tuple):
            next_position = self.path[self.path_index]
        elif isinstance(self.path[self.path_index], str):
            next_position = self.convert_path(self.path[self.path_index])

        # print("Path", self.path)

        print("Next position:", next_position)
        success = self.move_to(next_position)

        if success:
            self.path_index += 1
            if self.path_index == len(self.path):
                return True
        else:
            # print(f"Move {next_position} failed.")
            return False
