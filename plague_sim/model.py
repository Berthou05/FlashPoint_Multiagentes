"""Main model for the PlaguePoint simulation."""

from mesa import Model
from mesa.space import MultiGrid

from .entities import Door, POI, Patient, RatKing, RatSwarm, Wall


class PlagueSimulationModel(Model):
    """Store the board, entities, and global game rules."""

    BOARD_WIDTH = 8
    BOARD_HEIGHT = 10

    MAX_HOUSE_DAMAGE = 24
    PATIENTS_TO_RESCUE = 7
    MAX_PATIENTS_KILLED = 4

    TOTAL_PATIENTS = 10
    TOTAL_EMPTY_POIS = 5
    ACTIVE_POIS_TARGET = 3

    DIRECTIONS = (
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
    )

    # Fixed Family-mode starting positions for this board.
    INITIAL_RAT_KING_POSITIONS = (
        (4, 2), (5, 2), (4, 3), (5, 3), (3, 4),
        (4, 4), (4, 5), (1, 6), (2, 6), (2, 7),
    )

    INITIAL_POI_POSITIONS = (
        (2, 1),
        (2, 8),
        (5, 4),
    )

    EXTERIOR_DOORS = (
        ((4, 0), (4, 1)),
        ((0, 3), (1, 3)),
        ((3, 8), (3, 9)),
        ((6, 6), (7, 6)),
    )

    INTERIOR_DOORS = (
        ((1, 5), (1, 6)),
        ((1, 7), (1, 8)),
        ((2, 4), (3, 4)),
        ((3, 6), (3, 7)),
        ((4, 8), (5, 8)),
        ((5, 5), (5, 6)),
        ((6, 3), (6, 4)),
        ((4, 2), (4, 3)),
    )

    DOCTOR_START_POSITIONS = (
        (4, 0),
        (0, 3),
        (3, 9),
        (7, 6),
    )

    def __init__(self, width=8, height=10, seed=None):
        # Mesa 3.5 accepts rng and exposes self.random for reproducible choices.
        super().__init__(rng=seed)

        if width != self.BOARD_WIDTH or height != self.BOARD_HEIGHT:
            raise ValueError("PlaguePoint currently uses a fixed 8 by 10 board.")

        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, torus=False)

        # Walls and Doors live between cells, not inside the MultiGrid.
        self.boundaries = {}

        self.house_damage = 0
        self.turn = 0
        self.game_over = False
        self.game_won = False

        self.patients_rescued = 0
        self.patients_killed = 0

        # Doctors are Mesa agents, but this list lets the model query them
        # without importing agents.py and creating a circular import.
        self.doctors = []

        self.poi_pool = []

        self._setup_house()
        self.create_poi_pool()
        self._setup_initial_entities()

    # ==========================================================
    # House boundaries
    # ==========================================================

    @staticmethod
    def edge_key(cell_a, cell_b):
        """Return the same dictionary key regardless of cell order."""
        return tuple(sorted((cell_a, cell_b)))

    def add_wall(self, cell_a, cell_b):
        """Place a Wall between two neighboring cells."""
        self.boundaries[self.edge_key(cell_a, cell_b)] = Wall()

    def add_door(self, cell_a, cell_b, is_open=False):
        """Place a Door, replacing a Wall on the same edge if needed."""
        self.boundaries[self.edge_key(cell_a, cell_b)] = Door(is_open)

    def get_boundary(self, cell_a, cell_b):
        """Return the Wall, Door, or None between two cells."""
        return self.boundaries.get(self.edge_key(cell_a, cell_b))

    def are_neighbors(self, cell_a, cell_b):
        """Return True only for orthogonally adjacent board cells."""
        if not self.is_inside_board(cell_a) or not self.is_inside_board(cell_b):
            return False

        x_distance = abs(cell_a[0] - cell_b[0])
        y_distance = abs(cell_a[1] - cell_b[1])
        return x_distance + y_distance == 1

    def can_cross(self, cell_a, cell_b):
        """Return whether an adjacent edge can currently be crossed."""
        if not self.are_neighbors(cell_a, cell_b):
            return False

        boundary = self.get_boundary(cell_a, cell_b)
        return boundary is None or boundary.is_passable

    def damage_boundary(self, cell_a, cell_b):
        """Damage one Wall or Door and return structural damage added."""
        boundary = self.get_boundary(cell_a, cell_b)

        if boundary is None:
            return 0

        damage_added = boundary.take_damage()

        # Only walls add to the building's 24 structural damage points.
        if isinstance(boundary, Wall):
            self.house_damage += damage_added
            self.check_game_end()

        return damage_added

    def _setup_house(self):
        """Create walls first, then replace selected edges with doors."""
        self._create_perimeter_walls()
        self._create_interior_walls()
        self._create_doors()

    def _create_perimeter_walls(self):
        """Surround the interior x=1..6, y=1..8 with walls."""
        for x in range(1, 7):
            self.add_wall((x, 0), (x, 1))
            self.add_wall((x, 8), (x, 9))

        for y in range(1, 9):
            self.add_wall((0, y), (1, y))
            self.add_wall((6, y), (7, y))

    def _create_interior_walls(self):
        """Create the fixed room-dividing walls from the board map."""
        wall_segments = (
            ((2, 1), (3, 1)), ((2, 2), (3, 2)),
            ((2, 3), (3, 3)), ((2, 4), (3, 4)),
            ((2, 5), (3, 5)), ((2, 6), (3, 6)),
            ((2, 7), (3, 7)), ((2, 8), (3, 8)),

            ((4, 3), (5, 3)), ((4, 4), (5, 4)),
            ((4, 5), (5, 5)), ((4, 6), (5, 6)),
            ((4, 7), (5, 7)), ((4, 8), (5, 8)),

            ((3, 2), (3, 3)), ((4, 2), (4, 3)),
            ((5, 3), (5, 4)), ((6, 3), (6, 4)),
            ((1, 5), (1, 6)), ((2, 5), (2, 6)),
            ((5, 5), (5, 6)), ((6, 5), (6, 6)),
            ((1, 7), (1, 8)), ((2, 7), (2, 8)),
            ((3, 6), (3, 7)), ((4, 6), (4, 7)),
        )

        for cell_a, cell_b in wall_segments:
            self.add_wall(cell_a, cell_b)

    def _create_doors(self):
        """Create open exterior entrances and closed interior doors."""
        for cell_a, cell_b in self.EXTERIOR_DOORS:
            self.add_door(cell_a, cell_b, is_open=True)

        for cell_a, cell_b in self.INTERIOR_DOORS:
            self.add_door(cell_a, cell_b, is_open=False)

    # ==========================================================
    # Board and cell queries
    # ==========================================================

    def is_inside_board(self, position):
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def is_interior_position(self, position):
        """Return True only for cells inside the house."""
        if not self.is_inside_board(position):
            return False

        x, y = position
        return 1 <= x <= 6 and 1 <= y <= 8

    def is_exterior_position(self, position):
        """Return True for valid board cells outside the house."""
        return self.is_inside_board(position) and not self.is_interior_position(position)

    def get_exterior_positions(self):
        """Return every legal starting cell for a Doctor."""
        return [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if self.is_exterior_position((x, y))
        ]

    def get_exit_positions(self):
        """Return the exterior cells directly connected to house entrances."""
        exits = []

        for cell_a, cell_b in self.EXTERIOR_DOORS:
            if self.is_exterior_position(cell_a):
                exits.append(cell_a)
            else:
                exits.append(cell_b)

        return exits

    def get_neighbors(self, position):
        """Return orthogonal neighbors that are still on the board."""
        x, y = position
        possible = (
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        )
        return [cell for cell in possible if self.is_inside_board(cell)]

    def random_interior_position(self):
        """Equivalent to rolling the 6 by 8 coordinates of the board."""
        return (
            self.random.randrange(1, 7),
            self.random.randrange(1, 9),
        )

    def get_cell_contents(self, position):
        return self.grid.get_cell_list_contents([position])

    def get_entities_at(self, position, entity_types):
        """Return all matching entities in one cell."""
        return [
            entity
            for entity in self.get_cell_contents(position)
            if isinstance(entity, entity_types)
        ]

    def get_infestation_at(self, position):
        infestations = self.get_entities_at(position, (RatSwarm, RatKing))
        return infestations[0] if infestations else None

    def get_poi_at(self, position):
        pois = self.get_entities_at(position, POI)
        return pois[0] if pois else None

    def get_patient_at(self, position):
        patients = self.get_entities_at(position, Patient)
        return patients[0] if patients else None

    def get_patients_at(self, position):
        return self.get_entities_at(position, Patient)

    def get_doctors_at(self, position):
        return [doctor for doctor in self.doctors if doctor.pos == position]

    # ==========================================================
    # Doctor placement and movement validation
    # ==========================================================

    def place_doctor(self, doctor, position=None):
        """Place a Doctor outside the house at the start of a game."""
        if doctor.pos is not None:
            raise ValueError("Doctor is already on the board.")

        if position is None:
            position = self.random.choice(self.get_exterior_positions())

        if not self.is_exterior_position(position):
            raise ValueError("Doctors must start outside the house.")

        self.grid.place_agent(doctor, position)

        if doctor not in self.doctors:
            self.doctors.append(doctor)

        return doctor

    def can_doctor_move(self, doctor, target):
        """Check movement geometry without spending Action Points."""
        if doctor.pos is None:
            return False
        return self.can_cross(doctor.pos, target)

    def move_doctor(self, doctor, target):
        """Move a Doctor after agents.py has validated and paid the AP cost."""
        if doctor not in self.doctors or not self.can_doctor_move(doctor, target):
            return False

        self.grid.move_agent(doctor, target)
        return True

    # ==========================================================
    # Fixed game setup
    # ==========================================================

    def _setup_initial_entities(self):
        """Place the fixed starting RatKings and POIs."""
        for position in self.INITIAL_RAT_KING_POSITIONS:
            self.create_rat_king(position)

        # The POI positions are fixed, but their hidden contents are shuffled.
        for position in self.INITIAL_POI_POSITIONS:
            has_patient = self.draw_poi_content()
            self.create_poi(position, has_patient)

    # ==========================================================
    # Infestation
    # ==========================================================

    def create_rat_swarm(self, position):
        swarm = RatSwarm(self)
        self.grid.place_agent(swarm, position)
        return swarm

    def create_rat_king(self, position):
        rat_king = RatKing(self)
        self.grid.place_agent(rat_king, position)
        self.resolve_rat_king_cell(position)
        return rat_king

    def remove_infestation(self, infestation):
        if infestation.pos is not None:
            self.grid.remove_agent(infestation)
        infestation.remove()

    def promote_rat_swarm(self, swarm):
        """Replace a RatSwarm with a RatKing in the same cell."""
        position = swarm.pos
        self.remove_infestation(swarm)
        return self.create_rat_king(position)

    def add_infestation(self, position):
        """Apply Empty -> Swarm -> King -> Outbreak."""
        infestation = self.get_infestation_at(position)

        if infestation is None:
            return self.create_rat_swarm(position)

        if isinstance(infestation, RatSwarm):
            return self.promote_rat_swarm(infestation)

        self.trigger_rat_king_outbreak(position)
        return infestation

    def spawn_round_infestation(self):
        """Advance infestation once at a random interior coordinate."""
        position = self.random_interior_position()
        return position, self.add_infestation(position)

    def trigger_rat_king_outbreak(self, position):
        """Start one four-direction outbreak from the original RatKing."""
        for direction in self.DIRECTIONS:
            if self.game_over:
                return
            self.spread_outbreak(position, direction)

    def spread_outbreak(self, position, direction):
        """Spread one outbreak wave in one direction until it resolves."""
        current = position

        while True:
            target = (
                current[0] + direction[0],
                current[1] + direction[1],
            )

            if not self.is_inside_board(target):
                return

            if not self.resolve_outbreak_boundary(current, target):
                return

            infestation = self.get_infestation_at(target)

            # An outbreak creates a RatKing directly in an empty cell.
            if infestation is None:
                self.create_rat_king(target)
                return

            # A RatSwarm is promoted to RatKing and stops this direction.
            if isinstance(infestation, RatSwarm):
                self.promote_rat_swarm(infestation)
                return

            # A RatKing carries the shockwave onward in the same direction.
            current = target

    def resolve_outbreak_boundary(self, current, target):
        """Resolve a Wall or Door hit and return whether the wave continues."""
        boundary = self.get_boundary(current, target)

        if boundary is None:
            return True

        if isinstance(boundary, Wall):
            # A wall already destroyed before this wave can be crossed.
            if boundary.is_destroyed:
                return True

            # Hitting a wall always stops this wave, even if this hit destroys it.
            self.damage_boundary(current, target)
            return False

        # A Door that was already destroyed behaves as an open passage.
        if boundary.is_destroyed:
            return True

        # An open Door is destroyed, but the shockwave passes through it.
        if boundary.is_open:
            self.damage_boundary(current, target)
            return True

        # A closed Door is destroyed and absorbs this outbreak direction.
        self.damage_boundary(current, target)
        return False

    def resolve_flashover(self):
        """Promote RatSwarms adjacent to RatKings until no chain remains."""
        king_positions = [
            entity.pos
            for entity in self.agents
            if isinstance(entity, RatKing) and entity.pos is not None
        ]

        index = 0
        while index < len(king_positions):
            if self.game_over:
                return

            king_position = king_positions[index]
            index += 1

            for neighbor in self.get_neighbors(king_position):
                if not self.can_cross(king_position, neighbor):
                    continue

                infestation = self.get_infestation_at(neighbor)

                if isinstance(infestation, RatSwarm):
                    new_king = self.promote_rat_swarm(infestation)
                    king_positions.append(new_king.pos)

    def remove_exterior_rat_kings(self):
        """Remove outbreak RatKings that ended outside the house."""
        for entity in list(self.agents):
            if (
                isinstance(entity, RatKing)
                and entity.pos is not None
                and self.is_exterior_position(entity.pos)
            ):
                self.remove_infestation(entity)

    # ==========================================================
    # POIs and Patients
    # ==========================================================

    def create_poi_pool(self):
        """Create and shuffle the finite 10-patient, 5-empty POI pool."""
        self.poi_pool = [True] * self.TOTAL_PATIENTS
        self.poi_pool += [False] * self.TOTAL_EMPTY_POIS
        self.random.shuffle(self.poi_pool)

    def draw_poi_content(self):
        if not self.poi_pool:
            return None
        return self.poi_pool.pop()

    def create_poi(self, position, has_patient):
        poi = POI(self, has_patient)
        self.grid.place_agent(poi, position)
        return poi

    def remove_poi(self, poi):
        if poi.pos is not None:
            self.grid.remove_agent(poi)
        poi.remove()

    def place_poi(self, position):
        """Place one POI if the target does not already contain a POI."""
        if not self.poi_pool or not self.is_interior_position(position):
            return None

        # Family rules reroll if a POI already occupies the target cell.
        if self.get_poi_at(position) is not None:
            return None

        # A new POI removes infestation from its target first.
        infestation = self.get_infestation_at(position)
        if infestation is not None:
            self.remove_infestation(infestation)

        has_patient = self.draw_poi_content()
        poi = self.create_poi(position, has_patient)

        # A POI placed under a Doctor is revealed immediately.
        if self.get_doctors_at(position):
            self.reveal_poi(poi)

        return poi

    def spawn_round_poi(self):
        """Roll until one legal POI target is found."""
        if not self.poi_pool:
            return None

        while True:
            position = self.random_interior_position()

            if self.get_poi_at(position) is not None:
                continue

            return self.place_poi(position)

    def count_active_pois(self):
        """Count unidentified POIs and all patients still in active play."""
        poi_count = sum(
            isinstance(entity, POI) and entity.pos is not None
            for entity in self.agents
        )

        patient_count = sum(
            isinstance(entity, Patient) and entity.pos is not None
            for entity in self.agents
        )

        # Carried Patients stay active even though they are removed from the grid.
        carried_count = sum(
            getattr(doctor, "carried_patient", None) is not None
            for doctor in self.doctors
        )

        return poi_count + patient_count + carried_count

    def replenish_pois(self):
        """Replenish until three POI/Patients are active or the pool is empty."""
        while self.poi_pool and self.count_active_pois() < self.ACTIVE_POIS_TARGET:
            self.spawn_round_poi()

    def reveal_poi(self, poi):
        """Reveal a POI and create a Patient only if it contains one."""
        position = poi.pos
        has_patient = poi.reveal()
        self.remove_poi(poi)

        if not has_patient:
            return None

        return self.create_patient(position)

    def create_patient(self, position):
        patient = Patient(self)
        self.grid.place_agent(patient, position)
        return patient

    def remove_patient(self, patient):
        if patient.pos is not None:
            self.grid.remove_agent(patient)
        patient.remove()

    def kill_patient(self, patient):
        self.remove_patient(patient)
        self.patients_killed += 1
        self.check_game_end()

    def kill_hidden_patient(self, poi):
        if not poi.has_patient:
            return False

        self.remove_poi(poi)
        self.patients_killed += 1
        self.check_game_end()
        return True

    def rescue_patient(self, patient):
        self.remove_patient(patient)
        self.patients_rescued += 1
        self.check_game_end()

    def resolve_rat_king_cell(self, position):
        """Resolve Patients and POIs when a RatKing appears in a cell."""
        # More than one revealed Patient can share a MultiGrid cell.
        for patient in list(self.get_patients_at(position)):
            self.kill_patient(patient)

        poi = self.get_poi_at(position)
        if poi is None:
            return

        if poi.has_patient:
            self.kill_hidden_patient(poi)
        else:
            self.remove_poi(poi)

    # ==========================================================
    # Environment phase and game state
    # ==========================================================

    def run_environment_phase(self):
        """Run Advance Infestation, Flashover, cleanup, and POI replenishment."""
        if self.game_over:
            return

        self.spawn_round_infestation()

        if self.game_over:
            return

        self.resolve_flashover()
        self.remove_exterior_rat_kings()

        if not self.game_over:
            self.replenish_pois()

        self.check_game_end()

    def finish_game(self, won):
        self.game_over = True
        self.game_won = won
        self.running = False

    def check_game_end(self):
        if self.patients_killed >= self.MAX_PATIENTS_KILLED:
            self.finish_game(False)
            return

        if self.house_damage >= self.MAX_HOUSE_DAMAGE:
            self.finish_game(False)
            return

        if self.patients_rescued >= self.PATIENTS_TO_RESCUE:
            self.finish_game(True)

    def advance_turn(self):
        if self.game_over:
            return

        self.turn += 1
        self.run_environment_phase()

    def step(self):
        """Mesa calls this method to advance one environment turn."""
        self.advance_turn()

    # ==========================================================
    # Unity state
    # ==========================================================

    def get_state(self):
        """Return JSON-ready simulation data for Unity."""
        walls = []
        doors = []

        for cells, boundary in self.boundaries.items():
            boundary_state = {
                "cells": [list(cells[0]), list(cells[1])],
                "damage": boundary.damage,
                "is_destroyed": boundary.is_destroyed,
            }

            if isinstance(boundary, Wall):
                walls.append(boundary_state)
            else:
                boundary_state["is_open"] = boundary.is_open
                doors.append(boundary_state)

        state = {
            "width": self.width,
            "height": self.height,
            "turn": self.turn,
            "running": self.running,
            "game_over": self.game_over,
            "game_won": self.game_won,
            "house_damage": self.house_damage,
            "patients_rescued": self.patients_rescued,
            "patients_killed": self.patients_killed,
            "walls": walls,
            "doors": doors,
            "rat_swarms": [],
            "rat_kings": [],
            "pois": [],
            "patients": [],
            "doctors": [],
        }

        for entity in self.agents:
            # Carried or removed entities may have no grid position.
            if entity.pos is None:
                continue

            if isinstance(entity, RatSwarm):
                state["rat_swarms"].append(list(entity.pos))

            elif isinstance(entity, RatKing):
                state["rat_kings"].append(list(entity.pos))

            elif isinstance(entity, POI):
                state["pois"].append({
                    "id": entity.unique_id,
                    "position": list(entity.pos),
                })

            elif isinstance(entity, Patient):
                state["patients"].append({
                    "id": entity.unique_id,
                    "position": list(entity.pos),
                })

        for doctor in self.doctors:
            if doctor.pos is None:
                continue

            carried_patient = getattr(doctor, "carried_patient", None)

            state["doctors"].append({
                "id": doctor.unique_id,
                "position": list(doctor.pos),
                "action_points": getattr(doctor, "action_points", None),
                "strategy": getattr(doctor, "strategy", None),
                "carried_patient_id": (
                    carried_patient.unique_id if carried_patient is not None else None
                ),
                "turn_completed": getattr(doctor, "turn_completed", None),
                "current_action": getattr(doctor, "current_action", None),
            })

        return state
