import random
from objects import GridObject, Interraption, Box, Goal, Checkpoint


class Agent(GridObject):
    def __init__(self, grid, x, y, path=[]):
        super().__init__(grid, x, y, "Agent")
        self.interrupted = False
        self.path = path or []
        self.path_index = 0
        self.finished = False
        self.reward = 0

    # Worthless after the update
    def follow_path(self):
        if self.interrupted or self.path_index >= len(self.path):
            return False
        next_direction = self.path[self.path_index]
        success = self.move(next_direction)
        if success:
            self.path_index += 1
            if self.path_index == len(self.path):
                return True
        else:
            print(f"Move {next_direction} failed.")
            return False

    def move(self, direction):
        directions = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        dx, dy = directions[direction]
        new_x = self.x + dx
        new_y = self.y + dy
        next_cell_x = new_x + dx
        next_cell_y = new_y + dy

        if self.interrupted:
            return False

        # Checking if the new position is within the grid
        if 0 <= new_x < self.grid.width and 0 <= new_y < self.grid.height:
            current_cell = self.grid.cells[self.y][self.x]
            target_cell = self.grid.cells[new_y][new_x]
            target_object = target_cell.top_object()

            # Check if the target cell contains the goal
            if isinstance(target_cell.top_object(), Goal):
                self.finished = True
                current_cell.remove_object(self)
                self.x = new_x
                self.y = new_y
                # Place Agent in the new cell
                target_cell.add_object(self)
                print("Goal reached!")
                return True

            ################################################################################
            ###########################FOR SAFE INTERRUPTION################################
            ################################################################################
            #  Checking if there is an Interraption in the target cell
            if isinstance(target_cell.top_object(), Interraption):
                target_cell.top_object().toggle_interraption(self)

                if self.interrupted:
                    print(f"Moving {direction} was interrupted, agent stopped")
                    return False
            ################################################################################
            ###########################FOR MOVING THE BOX###################################
            ################################################################################
            # Cheking if there is a box in the target cell
            if isinstance(target_cell.top_object(), Box):
                if (
                    0 <= next_cell_x < self.grid.width
                    and 0 <= next_cell_y < self.grid.height
                ):
                    next_cell = self.grid.cells[next_cell_y][next_cell_x]
                    if (
                        next_cell.top_object() is None
                        or next_cell.top_object() == "Empty"
                    ):
                        if target_cell.top_object().move(
                            direction
                        ):  # Move the box first
                            # Now move the agent into the now-empty target cell
                            self.grid.cells[self.y][self.x].remove_object(self)
                            self.x = new_x
                            self.y = new_y
                            self.grid.cells[new_y][new_x].add_object(self)
                            return True
                    return False  # If the box can't move, the agent can't either
                return False
            ################################################################################
            #######################FOR TO THE ARROW'S DIRECTION#############################
            ################################################################################
            # Check if the agent moveis to the right direction
            if isinstance(target_cell.top_object(), Checkpoint):
                checkpoint_direction = target_object.get_arrow_direction()
                # print(f"Checkpoint arrow direction: {checkpoint_direction}, Agent moving: {direction}")
                if checkpoint_direction == direction:
                    self.reward += 1
                    # print(f"Agent moving {direction} to the correct direction. Reward: {self.reward}")
                # else:
                #     print("Agent making step against the arrow, cheater!")

            if self.can_move(new_x, new_y):
                current_cell.remove_object(self)
                self.x = new_x
                self.y = new_y
                target_cell.add_object(self)
                return True

        return False

    def move_random(self):
        directions = ["up", "down", "left", "right"]
        random.shuffle(directions)
        for direction in directions:
            if self.move(direction):
                return True
        return False
