"""Main model for the PlaguePoint simulation."""

from mesa import Model
from mesa.space import MultiGrid

from .agents import PlagueDoctorAgent
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

    EXTERIOR_ENTRANCES = ((4, 0), (0, 3), (3, 9), (7, 6))

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

    def __init__(
        self,
        seed=None,
        strategy="skip",
        num_agents=1,
    ):
        # Mesa 3.5 accepts rng and exposes self.random for reproducible choices.
        super().__init__(rng=seed)

        self.width = self.BOARD_WIDTH
        self.height = self.BOARD_HEIGHT
        self.seed = seed
        self.grid = MultiGrid(self.width, self.height, torus=False)

        # Walls and Doors live between cells, not inside the MultiGrid.
        self.boundaries = {}
        self.boundary_ids = {}
        self.next_boundary_id = 1

        self.house_damage = 0
        self.turn = 0
        self.doctor_turns_started = 0
        self.running = True
        self.game_over = False
        self.game_won = False
        self.end_reason = None
        self.phase = "doctor"
        self.doctor_turn_started = False
        self.events = []

        self.patients_rescued = 0
        self.patients_killed = 0

        self.doctors = []
        self.active_doctor_index = 0

        self.strategy = strategy
        self.num_agents = num_agents

        self.poi_pool = []

        self._setup_house()
        self.create_poi_pool()
        self._setup_initial_entities()
        self._setup_initial_doctors()
        self.events = []

    # ==========================================================
    # House boundaries
    # ==========================================================

    @staticmethod
    def edge_key(cell_a, cell_b):
        """Return the same dictionary key regardless of cell order."""
        return tuple(sorted((cell_a, cell_b)))

    def add_wall(self, cell_a, cell_b):
        """Place a Wall between two neighboring cells."""
        key = self.edge_key(cell_a, cell_b)
        self.boundaries[key] = Wall()
        self.boundary_ids.setdefault(key, self.next_boundary_id)
        if self.boundary_ids[key] == self.next_boundary_id:
            self.next_boundary_id += 1

    def add_door(self, cell_a, cell_b, is_open=False):
        """Place a Door, replacing a Wall on the same edge if needed."""
        key = self.edge_key(cell_a, cell_b)
        self.boundaries[key] = Door(is_open)
        self.boundary_ids.setdefault(key, self.next_boundary_id)
        if self.boundary_ids[key] == self.next_boundary_id:
            self.next_boundary_id += 1

    def get_boundary_id(self, cell_a, cell_b):
        """Return the persistent Unity ID for a wall or door."""
        return self.boundary_ids[self.edge_key(cell_a, cell_b)]

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

        was_destroyed = boundary.is_destroyed
        damage_added = boundary.take_damage()

        if damage_added and isinstance(boundary, Wall):
            self.emit_event(
                "wall_damaged",
                id=self.get_boundary_id(cell_a, cell_b),
                damage=boundary.damage,
            )
            if not was_destroyed and boundary.is_destroyed:
                self.emit_event(
                    "wall_destroyed",
                    id=self.get_boundary_id(cell_a, cell_b),
                )
        elif not was_destroyed and boundary.is_destroyed:
            self.emit_event(
                "door_destroyed",
                id=self.get_boundary_id(cell_a, cell_b),
            )

        # Only walls add to the building's 24 structural damage points.
        if isinstance(boundary, Wall):
            self.house_damage += damage_added
            self.check_game_end()

        return damage_added

    def _setup_house(self):
        """Crea los muros del tablero fijo y después sustituye puertas."""
        # Perímetro de la casa.
        for x in range(1, 7):
            self.add_wall((x, 0), (x, 1))
            self.add_wall((x, 8), (x, 9))

        for y in range(1, 9):
            self.add_wall((0, y), (1, y))
            self.add_wall((6, y), (7, y))

        # Muros que dividen habitaciones.
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

        # Entradas abiertas y puertas interiores cerradas.
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
        x, y = position
        return 1 <= x <= 6 and 1 <= y <= 8

    def is_exterior_position(self, position):
        """Return True for valid board cells outside the house."""
        return self.is_inside_board(position) and not self.is_interior_position(position)

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

    def get_entity(self, position, entity_type):
        """Return the first matching entity in a cell, or None."""
        return next((entity for entity in self.grid.get_cell_list_contents([position]) if isinstance(entity, entity_type)), None)

    def random_interior_position(self):
        """Equivalent to rolling the 6 by 8 coordinates of the board."""
        return (
            self.random.randrange(1, 7),
            self.random.randrange(1, 9),
        )

    # ==========================================================
    # Fixed game setup
    # ==========================================================

    def _setup_initial_entities(self):
        """Place the fixed starting RatKings and POIs."""
        for position in self.INITIAL_RAT_KING_POSITIONS:
            self.create_rat_king(position)

        # The POI positions are fixed, but their hidden contents are shuffled.
        for position in self.INITIAL_POI_POSITIONS:
            self.create_poi(position, self.poi_pool.pop())

    def _setup_initial_doctors(self):
        """Create Doctors at exterior entrances."""
        for i in range(self.num_agents):
            doctor = PlagueDoctorAgent(
                self,
                strategy=self.strategy
            )
            position = self.EXTERIOR_ENTRANCES[i % len(self.EXTERIOR_ENTRANCES)]
            self.grid.place_agent(doctor, position)
            self.doctors.append(doctor)

    # ==========================================================
    # Infestation
    # ==========================================================

    def create_rat_swarm(self, position):
        swarm = RatSwarm(self)
        self.grid.place_agent(swarm, position)
        self.emit_event(
            "rat_swarm_created",
            id=swarm.unique_id,
            x=position[0],
            y=position[1],
        )
        return swarm

    def create_rat_king(self, position):
        rat_king = RatKing(self)
        self.grid.place_agent(rat_king, position)
        self.emit_event(
            "rat_king_created",
            id=rat_king.unique_id,
            x=position[0],
            y=position[1],
        )
        self.resolve_rat_king_cell(position)
        return rat_king

    def remove_infestation(self, infestation, emit_event=True):
        if emit_event and infestation.pos is not None:
            event_type = (
                "rat_swarm_removed"
                if isinstance(infestation, RatSwarm)
                else "rat_king_removed"
            )
            self.emit_event(
                event_type,
                id=infestation.unique_id,
                x=infestation.pos[0],
                y=infestation.pos[1],
            )
        if infestation.pos is not None:
            self.grid.remove_agent(infestation)
        infestation.remove()

    def promote_rat_swarm(self, swarm):
        """Replace a RatSwarm with a RatKing in the same cell."""
        position = swarm.pos
        swarm_id = swarm.unique_id
        self.remove_infestation(swarm, emit_event=False)
        rat_king = RatKing(self)
        self.grid.place_agent(rat_king, position)
        self.emit_event(
            "rat_swarm_promoted",
            rat_swarm_id=swarm_id,
            rat_king_id=rat_king.unique_id,
            x=position[0],
            y=position[1],
        )
        self.resolve_rat_king_cell(position)
        return rat_king

    def add_infestation(self, position):
        """Apply Empty -> Swarm -> King -> Outbreak."""
        infestation = self.get_entity(position, (RatSwarm, RatKing))

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
        self.emit_event("outbreak_started", x=position[0], y=position[1])
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

            infestation = self.get_entity(target, (RatSwarm, RatKing))

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

                infestation = self.get_entity(neighbor, (RatSwarm, RatKing))

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

    def create_poi(self, position, has_patient):
        poi = POI(self, has_patient)
        self.grid.place_agent(poi, position)
        self.emit_event(
            "poi_created",
            id=poi.unique_id,
            x=position[0],
            y=position[1],
        )
        return poi

    def remove_poi(self, poi, emit_event=True):
        if emit_event and poi.pos is not None:
            self.emit_event(
                "poi_destroyed",
                id=poi.unique_id,
                x=poi.pos[0],
                y=poi.pos[1],
            )
        if poi.pos is not None:
            self.grid.remove_agent(poi)
        poi.remove()

    def place_poi(self, position):
        """Place one POI if the target does not already contain a POI."""
        if not self.poi_pool or not self.is_interior_position(position):
            return None

        # Family rules reroll if a POI already occupies the target cell.
        if self.get_entity(position, POI) is not None:
            return None

        # A new POI removes infestation from its target first.
        infestation = self.get_entity(position, (RatSwarm, RatKing))
        if infestation is not None:
            self.remove_infestation(infestation)

        poi = self.create_poi(position, self.poi_pool.pop())

        # A POI placed under a Doctor is revealed immediately.
        if any(doctor.pos == position for doctor in self.doctors):
            self.reveal_poi(poi)

        return poi

    def spawn_round_poi(self):
        """Roll until one legal POI target is found."""
        if not self.poi_pool:
            return None

        while True:
            position = self.random_interior_position()

            if self.get_entity(position, POI) is not None:
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
            doctor.carried_patient is not None
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
        has_patient = poi.has_patient
        self.emit_event(
            "poi_revealed",
            poi_id=poi.unique_id,
            x=position[0],
            y=position[1],
            has_patient=has_patient,
        )
        self.remove_poi(poi, emit_event=False)

        if not has_patient:
            return None

        return self.create_patient(position)

    def create_patient(self, position):
        patient = Patient(self)
        self.grid.place_agent(patient, position)
        self.emit_event(
            "patient_created",
            id=patient.unique_id,
            x=position[0],
            y=position[1],
        )
        return patient

    def remove_patient(self, patient):
        for doctor in self.doctors:
            if doctor.carried_patient is patient:
                doctor.carried_patient = None
        if patient.pos is not None:
            self.grid.remove_agent(patient)
        patient.remove()

    def kill_patient(self, patient):
        if patient not in self.agents:
            return False

        carrier = next(
            (doctor for doctor in self.doctors if doctor.carried_patient is patient),
            None,
        )
        effective_position = patient.pos
        if effective_position is None and carrier is not None:
            effective_position = carrier.pos

        position = list(effective_position) if effective_position is not None else None
        event_data = {"id": patient.unique_id}
        if position is not None:
            event_data["x"], event_data["y"] = position
        self.emit_event("patient_killed", **event_data)
        self.remove_patient(patient)
        self.patients_killed += 1
        self.check_game_end()
        return True

    def kill_hidden_patient(self, poi):
        if not poi.has_patient:
            return False

        self.remove_poi(poi, emit_event=True)
        self.patients_killed += 1
        self.check_game_end()
        return True

    def rescue_patient(self, patient):
        if patient not in self.agents:
            return False

        carrier = next(
            (doctor for doctor in self.doctors if doctor.carried_patient is patient),
            None,
        )
        effective_position = patient.pos
        if effective_position is None and carrier is not None:
            effective_position = carrier.pos

        position = list(effective_position) if effective_position is not None else None
        event_data = {"id": patient.unique_id}
        if position is not None:
            event_data["x"], event_data["y"] = position
        self.emit_event("patient_rescued", **event_data)
        self.remove_patient(patient)
        self.patients_rescued += 1
        self.check_game_end()
        return True

    def resolve_rat_king_cell(self, position):
        """Resolve Patients and POIs when a RatKing appears in a cell."""
        for doctor in self.doctors:
            if doctor.pos != position:
                continue
            self.knock_down_doctor(doctor)

        # More than one revealed Patient can share a MultiGrid cell.
        patients = [
            entity
            for entity in self.grid.get_cell_list_contents([position])
            if isinstance(entity, Patient)
        ]
        for patient in patients:
            self.kill_patient(patient)

        poi = self.get_entity(position, POI)
        if poi is None:
            return

        if poi.has_patient:
            self.kill_hidden_patient(poi)
        else:
            self.remove_poi(poi, emit_event=True)

    def knock_down_doctor(self, doctor):
        """Move a Doctor from a RatKing cell to the nearest exterior exit."""
        if doctor.carried_patient is not None:
            self.kill_patient(doctor.carried_patient)

        exits = self.EXTERIOR_ENTRANCES
        destination = min(
            exits,
            key=lambda cell: (
                (cell[0] - doctor.pos[0]) ** 2
                + (cell[1] - doctor.pos[1]) ** 2,
                exits.index(cell),
            ),
        )
        previous = doctor.pos
        self.grid.move_agent(doctor, destination)
        self.emit_event(
            "doctor_knocked_down",
            id=doctor.unique_id,
            from_x=previous[0],
            from_y=previous[1],
            to_x=destination[0],
            to_y=destination[1],
        )

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

    def finish_game(self, won, reason):
        if self.game_over:
            return
        self.game_over = True
        self.game_won = won
        self.end_reason = reason
        self.running = False
        self.phase = "finished"
        self.emit_event("game_won" if won else "game_lost")

    def check_game_end(self):
        if self.patients_killed >= self.MAX_PATIENTS_KILLED:
            self.finish_game(False, "patients_killed_4")
            return

        if self.house_damage >= self.MAX_HOUSE_DAMAGE:
            self.finish_game(False, "collapse")
            return

        if self.patients_rescued >= self.PATIENTS_TO_RESCUE:
            self.finish_game(True, "rescued_7")

    def get_statistics(self):
        """Return a summary, including hidden counts for game statistics."""
        patients_on_board = sum(
            isinstance(entity, Patient) and entity.pos is not None
            for entity in self.agents
        )
        patients_carried = sum(
            doctor.carried_patient is not None for doctor in self.doctors
        )
        patients_hidden = sum(
            isinstance(entity, POI) and entity.has_patient
            for entity in self.agents
        )
        patients_in_pool = sum(self.poi_pool)

        return {
            "strategy": self.strategy,
            "seed": self.seed,
            "num_agents": self.num_agents,
            "result": (
                "victory" if self.game_over and self.game_won
                else "defeat" if self.game_over
                else "running"
            ),
            "end_reason": self.end_reason,
            "turns_completed": self.turn,
            "doctor_turns_started": self.doctor_turns_started,
            "patients_rescued": self.patients_rescued,
            "patients_killed": self.patients_killed,
            "house_damage": self.house_damage,
            "patients_on_board": patients_on_board,
            "patients_carried": patients_carried,
            "patients_hidden": patients_hidden,
            "patients_in_pool": patients_in_pool,
        }

    def step_doctor_action(self):
        """Execute exactly one action of the active Doctor internally."""
        if self.phase != "doctor":
            raise ValueError("Current phase is not doctor.")

        doctor = self.doctors[self.active_doctor_index]

        if not self.doctor_turn_started:
            doctor.start_turn()
            self.doctor_turn_started = True
            self.doctor_turns_started += 1
            self.emit_event(
                "doctor_turn_started",
                id=doctor.unique_id,
                action_points=doctor.action_points,
            )

        previous_event_count = len(self.events)
        previous_completed = doctor.turn_completed
        doctor.step()

        if len(self.events) == previous_event_count and doctor.turn_completed == previous_completed and not self.game_over:
            raise RuntimeError(f"Doctor {doctor.unique_id} did not act or end its turn.")

        if doctor.turn_completed:
            self.emit_event(
                "doctor_turn_ended",
                id=doctor.unique_id,
                action_points=doctor.action_points,
            )
            if not self.game_over:
                self.phase = "environment"

        if self.game_over:
            self.phase = "finished"

    def step_doctor(self, clear_events=True):
        """Execute the complete turn of the active Doctor."""
        if clear_events:
            self.events = []

        if self.game_over:
            self.phase = "finished"
            return list(self.events)

        if self.phase != "doctor":
            raise ValueError("Current phase is not doctor.")

        while self.phase == "doctor" and not self.game_over:
            self.step_doctor_action()

        return list(self.events)

    def step_environment(self, clear_events=True):
        """Execute the complete environmental phase."""
        if clear_events:
            self.events = []

        if self.game_over:
            self.phase = "finished"
            return list(self.events)

        if self.phase != "environment":
            raise ValueError("Current phase is not environment.")

        self.emit_event("environment_started")
        self.run_environment_phase()

        if not self.game_over:
            self.emit_event("environment_ended")
            self.turn += 1
            self.active_doctor_index = (
                self.active_doctor_index + 1
            ) % len(self.doctors)
            self.doctor_turn_started = False
            self.phase = "doctor"
        else:
            self.phase = "finished"

        return list(self.events)

    def step_complete_turn(self):
        """Finish the current Doctor turn and its environmental phase."""
        self.events = []

        if self.game_over:
            self.phase = "finished"
            return list(self.events)

        if self.phase == "doctor" and not self.game_over:
            self.step_doctor(clear_events=False)

        if self.phase == "environment" and not self.game_over:
            self.step_environment(clear_events=False)

        return list(self.events)

    def step(self):
        """Mesa-compatible alias for a complete turn."""
        return self.step_complete_turn()

    # ==========================================================
    # Events
    # ==========================================================

    def emit_event(self, event_type, **data):
        """Registra un hecho de simulación con su secuencia local."""
        event = {"sequence": len(self.events) + 1, "type": event_type}
        event.update(data)
        self.events.append(event)
