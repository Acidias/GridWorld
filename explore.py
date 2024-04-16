import random
from objects import GridObject, Interraption, Box, Goal, Wall, Checkpoint


class AgentExplore(GridObject):
    def __init__(self, grid, x, y, path=[]):
        super().__init__(grid, x, y, "Agent")
        self.interrupted = False
        self.path = path or []
        self.path_index = 0
        self.finished = False
        self.reward = 0
        self.exploit = False
        self.previous_position = (x, y)

    def get_available_directions(self):
        return self.grid.neighbors(self.x, self.y)

    def is_checkpoint(self, x, y):
        # print(f"Checking checkpoint at ({x}, {y})")
        for obj in self.grid.objects["P"]:
            if obj.x == x and obj.y == y:
                return True
        return False

    def adjacent_checkpoints(self, avail_dirs):
        avail_checkpoints = []
        for adjacent in avail_dirs:
            # print(f"Adjacent: {adjacent}")
            if self.is_checkpoint(adjacent[0], adjacent[1]):
                avail_checkpoints.append(adjacent)
        return avail_checkpoints

    def get_checkpoint_direction(self, avail_checkpoint):
        for obj in self.grid.objects["P"]:
            if obj.x == avail_checkpoint[0] and obj.y == avail_checkpoint[1]:
                return obj.get_arrow_direction()
        return None

    def choose_direction_to_checkpoint(self, checkpoint_dir):
        return checkpoint_dir

    def is_checkpoint_narrowing_against_agent(
        self, checkpoint_position, checkpoint_dir
    ):
        dx = checkpoint_position[1] - self.x
        dy = checkpoint_position[0] - self.y

        # Check if the direction of the checkpoint is showing to the agent direction
        if checkpoint_dir == "up" and dy > 0:
            return True
        elif checkpoint_dir == "down" and dy < 0:
            return True
        elif checkpoint_dir == "left" and dx > 0:
            return True
        elif checkpoint_dir == "right" and dx < 0:
            return True

        return False

    def move(self):
        current_cell = self.grid.get_cell(self.x, self.y)
        current_checkpoint = self.get_checkpoint(current_cell)
        # If starting on a checkpoint, decide on the movement based on the checkpoint direction regarding of exploit value
        if current_checkpoint:
            checkpoint_dir = current_checkpoint.get_arrow_direction()
            if self.exploit:
                self.move_opposite_direction(checkpoint_dir, self.x, self.y)
            else:
                self.move_to_right_direction(checkpoint_dir, self.x, self.y)
            return

        # Explore directions for checkpoints and move to them
        available_directions = self.grid.neighbors(self.x, self.y)
        for nx, ny in available_directions:
            cell = self.grid.get_cell(nx, ny)
            checkpoint = self.get_checkpoint(cell)
            if checkpoint:
                checkpoint_dir = checkpoint.get_arrow_direction()
                if not self.is_checkpoint_narrowing_against_agent(
                    (ny, nx), checkpoint_dir
                ):
                    self.move_to_checkpoint(nx, ny, checkpoint_dir)
                    return

    def move_to_checkpoint(self, nx, ny, checkpoint_dir):
        self.actual_move(nx, ny)
        self.reward += 1
        # print(f"Moved to checkpoint at ({nx}, {ny}) facing {checkpoint_dir}")
        # self.check_on_checkpoint(checkpoint_dir, nx, ny)

    def check_on_checkpoint(self, checkpoint_dir, nx, ny):
        if self.exploit:
            self.move_opposite_direction(checkpoint_dir, nx, ny)
        else:
            self.move_to_right_direction(checkpoint_dir, nx, ny)

    def get_checkpoint(self, cell):
        return next(
            (obj for obj in cell.contained_objects if isinstance(obj, Checkpoint)), None
        )

    def move_to_right_direction(self, checkpoint_dir, nx, ny):
        moves = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        dx, dy = moves[checkpoint_dir]
        nx, ny = self.x + dx, self.y + dy

        # Check if the new position is within grid bounds and is walkable
        if self.grid.can_move(nx, ny):
            self.actual_move(nx, ny)
            # print(f"Moved in the direction {checkpoint_dir} to ({nx}, {ny}).")
        # else:
        # print(f"Cannot move in the direction {checkpoint_dir}.")

    def move_opposite_direction(self, checkpoint_dir, nx, ny):
        opposite_dirs = {"up": "down", "down": "up", "left": "right", "right": "left"}
        opp_dir = opposite_dirs[checkpoint_dir]
        moves = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        dx, dy = moves[opp_dir]
        nx, ny = self.x + dx, self.y + dy
        if self.grid.can_move(nx, ny):
            self.actual_move(nx, ny)
        #   print(f"Moved {opp_dir} to ({nx}, {ny}) due to exploitation.")

    def actual_move(self, nx, ny):
        # Get references to the current and target cells
        current_cell = self.grid.get_cell(self.x, self.y)
        target_cell = self.grid.get_cell(nx, ny)

        # print(f"Moving from ({self.x}, {self.y}) to ({nx}, {ny}).")
        # print(f"Moving from ({current_cell}) to ({target_cell}).")
        current_cell.remove_object(self)
        self.x = nx
        self.y = ny
        target_cell.add_object(self)

    def update_position_after_move(self, nx, ny):
        self.x, self.y = nx, ny
        self.previous_position = (nx, ny)

    def exploit_move(self):
        # Move back to the previous position for exploitation
        prev_x, prev_y = self.previous_position
        current_cell = self.grid.get_cell(self.x, self.y)
        prev_cell = self.grid.get_cell(prev_x, prev_y)
        self.grid.move_object(current_cell, prev_cell, self)
        self.x, self.y = prev_x, prev_y  # Move back
        print(f"Exploited and moved back to previous position ({prev_x}, {prev_y})")

    def perform_random_move(self):
        available_directions = self.grid.neighbors(self.x, self.y)
        if available_directions:
            nx, ny = random.choice(available_directions)
            self.grid.move_object(
                self.grid.get_cell(self.x, self.y), self.grid.get_cell(nx, ny), self
            )
            self.x, self.y = nx, ny
            print(f"Randomly moved to ({nx}, {ny}).")

    def move_random(self):
        directions = ["up", "down", "left", "right"]
        random.shuffle(directions)
        for direction in directions:
            if self.move(direction):
                return True
        return False
