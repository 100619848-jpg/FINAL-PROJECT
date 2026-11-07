# Service Rush: Project Plan

Final project for Programming 2026-2027 (UC3M). Cooperative cooking game in Python with Pyxel, built by a team of two.

This document contains the project analysis, the architecture proposal, the backlog (epics and issues with acceptance criteria) and a short manual to run the whole project on GitHub.

## 1. Project summary

Two chefs share a kitchen divided in two zones by a counter. Chef 1 (upper zone) owns the onion, egg and chorizo drawers, a chopping board, the blender and the delivery counter. Chef 2 (lower zone) owns the tomato and potato drawers, a chopping board, the pan and the dish stack. No recipe can be completed by one chef alone, so every order requires hand-overs through the dividing counter. Orders arrive on a service board with a countdown; a level lasts 3 minutes; each level adds one order; the game ends after 3 failures.

### 1.1 Grading and constraints

| Item | Weight |
|------|--------|
| Sprint 1: objects and graphical interface | 0.5 |
| Sprint 2: chef movement | 0.5 |
| Sprint 3: ingredients, stations and recipes | 0.5 |
| Sprint 4: orders, scoring and end of service | 0.5 |
| Report (PDF, maximum 10 pages) | 0.5 |
| Sprint 5 optional features (sound 0.10, stars and screens 0.10, dish cycle 0.20, timed actions 0.20) | up to 0.5 |
| Graphics bonus (first 3 groups to upload the pyxres file) | 0.1 |
| Cap for the whole project | 2.5 |

Penalties to design against from day one:

| Penalty | Trigger |
|---------|---------|
| 0.25 | Insufficient comments. All classes and methods documented, plus comments inside methods. |
| 0.5 | Unused methods, repetitive code instead of loops, poor class design, orders or ingredients not represented with lists, practices not taught in the course. |
| 0.5 | Unnecessary attributes, public attributes that should be private, attributes created outside `__init__`, properties not used where they should be. |
| 0.5 | Code outside classes (except the main program) or methods too long (one screen without scrolling). |
| Exclusion | Plagiarism, for both the copier and the copied. |

Submission rules: group of 2, one zip named `initials1-initials2.zip` containing the report (PDF), the `.py` files and the `.pyxres` file, uploaded to Aula Global before the deadline.

## 2. Working assumptions and open questions

The brief is detailed but silent on a few points. The assumptions below are used throughout the backlog. Items marked "Confirm" should be checked with the instructor before the related issue starts.

| ID | Topic | Assumption | Confirm |
|----|-------|------------|---------|
| A1 | Constants | Fixed values live as class attributes of a `Settings` class, because module-level constants may be read as code outside classes. | Yes |
| A2 | Allowed language features | Only features taught in the course are used (plain classes, inheritance, properties, lists, dictionaries, tuples). Dataclasses, enums, abstract base classes and third-party libraries are avoided unless the syllabus covers them. | Yes |
| A3 | Movement | Tile-based movement with a fixed number of frames per tile. Pressing a direction towards a blocked tile turns the chef without moving. Speed is not specified in the brief. | No |
| A4 | Order matching | A delivered dish completes the oldest waiting order of the same recipe. | No |
| A5 | Wrong hand-in | Adds one failure, no score deduction, and the dish disappears. An empty dish at the delivery counter does nothing. | No |
| A6 | Dish contents | A dish holds either loose ingredients or one finished preparation, never both. Adding or pouring is rejected (the action key does nothing) when it would mix them. | Yes |
| A7 | Occupied stations | A chopping board or piece of equipment that already holds contents rejects a new deposit. | No |
| A8 | Chopping board | A full dish deposits all its contents on the board; ingredients that can be chopped are chopped, the others stay unchanged. The dish stays empty in the chef's hands. | No |
| A9 | Order schedule | With N orders in a level, order i (starting at 0) is scheduled at `3 s + i * (180 s - 3 s) / N`. If 3 orders are already waiting, the order appears as soon as there is room. | No |
| A10 | Failures | The failure counter is cumulative across levels. The third failure ends the game immediately. | No |
| A11 | Level cleanup | At the end of a service, orders, dishes, station contents and carried items are cleared and both chefs return to their start tiles. Score and failures are kept. | No |
| A12 | Stars | One star is always granted. Two stars at 40% or more of the points available in the level's orders, three stars at 75% or more. Thresholds are constants. | No |
| A13 | Sprint 5 timings | Proposed values, to be tuned in playtests: chopping 60 frames, cooking 150 frames, washing 60 frames, return delay 360 frames, 6 dishes in the pool. | No |
| A14 | Washing | The sink is on the dividing counter and reachable by both chefs, but only Chef 2 can wash. The stack starts with a finite number of clean dishes when the dish cycle is enabled. | Yes |

## 3. Architecture proposal

### 3.1 Principles

1. All behaviour of an entity lives in its class. The main program only creates the game object and starts it.
2. Game logic classes do not call Pyxel directly, except in their `draw` methods. This keeps logic testable without opening a window.
3. Time is measured in frames at 30 frames per second. Every duration is stored in frames, derived from seconds in `Settings`.
4. Stations are polymorphic: the chef calls `station.interact(chef)` and each station type decides what happens. No chain of `if` on station type in `Chef` or `Game`.
5. Attributes are created in `__init__`, are private (leading underscore) and are exposed through properties when read from outside.

### 3.2 Suggested layout

```
service-rush/
    README.md
    requirements.txt
    .gitignore
    .github/
        ISSUE_TEMPLATE/
        pull_request_template.md
    docs/
        PROJECT_PLAN.md
        design.md
        sprites.md
        test-plan.md
    assets/
        service_rush.pyxres
    src/
        main.py
        game.py
        settings.py
        ingredient.py
        container.py
        dish.py
        recipe.py
        order.py
        order_manager.py
        stations.py
        kitchen.py
        chef.py
        score_keeper.py
        service_clock.py
        service.py
        service_board.py
        screens.py
        sound_player.py
    tests/
```

### 3.3 Class responsibilities

| Class | Responsibility |
|-------|----------------|
| `Settings` | All fixed values from the brief: screen, tile size, fps, durations, points, penalties, recipes data, layout, key bindings. |
| `Ingredient` | Kind, processing state (whole, chopped, blended) and cooked flag. Knows whether it can be chopped. |
| `Container` | List of ingredients plus an optional finished preparation. Shared by dishes, chopping boards and equipment through composition. |
| `Dish` | A container carried by a chef or placed on a station. Draws itself according to its content. |
| `Recipe` | Name, ingredient signature, equipment kind, points, time limit, penalty, icon. |
| `RecipeBook` | List of recipes. Validates a set of ingredients against an equipment kind and returns the matching recipe or nothing. |
| `Order` | One waiting order: recipe and remaining frames. |
| `OrderManager` | Waiting orders list, spawn schedule, expiry, matching of delivered dishes. |
| `Station` | Base class: tile position, content slot, `interact(chef)`, `draw()`. |
| `Worktop`, `HandOverSurface`, `Wall`, `Drawer`, `ChoppingBoard`, `Equipment` (with `Blender` and `Pan`), `DishStack`, `DeliveryCounter`, `Bin`, `Sink`, `ReturnCounter` | Concrete stations. The last two are optional. |
| `Kitchen` | Builds the station grid from the layout data, answers walkability and "what is in front of this chef" queries, draws the kitchen. |
| `Chef` | Position, facing, carried dish, key bindings, movement, action key, drawing. |
| `ScoreKeeper` | Score (never below zero), failures, points earned in the current level. |
| `ServiceClock` | Frame counter and remaining time of a service. |
| `Service` | One level: clock, order manager, kitchen contents, finished state. |
| `ServiceBoard` | Draws the top band: tickets, score, failures, timer, level. |
| `Screens` | Start screen and end-of-service screen (optional). |
| `SoundPlayer` | Plays named sound effects (optional). |
| `Game` | Pyxel loop owner and state machine (playing, service over, game over). |

### 3.4 Action key interaction matrix

The action key affects the tile the chef is facing. Any case not listed does nothing.

| Chef carries | Chef faces | Result |
|--------------|-----------|--------|
| Nothing | Dish stack (Chef 2 only) | Takes one empty dish. |
| Nothing | Station holding a dish | Picks the dish up. |
| Dish (empty or full) | Free surface | Leaves the dish. |
| Dish (empty or full) | Drawer | Adds the raw ingredient to the dish. |
| Empty dish | Equipment or chopping board | Takes out whatever is inside. |
| Full dish | Equipment | Leaves all contents to be processed. |
| Full dish | Chopping board | Leaves contents; choppable ingredients are chopped. |
| Full dish | Station holding a dish | Pours the contents into the other dish. |
| Full dish | Delivery counter (Chef 1 only) | Hands the dish in: completes the matching order, or adds a failure. |
| Full dish | Bin | Food is lost; the dish is emptied and stays in the chef's hands. |

### 3.5 Kitchen layout as data

The kitchen is a grid of 12 columns by 9 rows with tiles of 32 x 32 pixels (sprites of 16 x 16 shown at double size). The service board occupies the top 384 x 64 pixels; the kitchen starts at y = 64. Total screen: 384 x 352.

Legend: `.` floor, `w` free worktop, `#` solid wall, `P` hand-over surface, `B` bin, `1` onion drawer, `2` egg drawer, `3` chorizo drawer, `4` tomato drawer, `5` potato drawer, `C` chopping board, `L` blender, `N` pan, `D` dish stack, `V` delivery counter, `S` sink (optional), `R` return counter (optional).

```
row 0:  123wCwLwwwwV
row 1:  ............
row 2:  ............
row 3:  ............
row 4:  #P#P#B#P#SP#
row 5:  ............
row 6:  ............
row 7:  ............
row 8:  45wwwCwNRDww
```

Chef 1 starts at row 2, column 5. Chef 2 starts at row 6, column 5. When the dish cycle is disabled, `S` is loaded as a wall and `R` as a free worktop.

### 3.6 Recipe data

| Recipe | Ingredients | Equipment | Points | Time limit | Penalty if lost |
|--------|-------------|-----------|--------|------------|-----------------|
| Gazpacho | chopped tomato, chopped onion | Blender | 10 | 48 s | 5 |
| Spanish omelette | chopped potato, chopped onion, egg | Pan | 12 | 60 s | 6 |
| Broken eggs with chorizo | chopped potato, egg, chopped chorizo | Pan | 12 | 60 s | 6 |

Ingredients that must be chopped: tomato, potato, onion, chorizo. The egg goes in whole.

## 4. Conventions and definition of done

### 4.1 Coding conventions

- English for identifiers, comments and documentation.
- One class per responsibility; no code outside classes except the main program.
- Methods stay short enough to fit one screen. Extract helpers early.
- Every class and every method has a docstring; non-trivial blocks have inline comments.
- Private attributes with a leading underscore; read access through properties; no attributes created outside `__init__`.
- Orders, ingredients and recipes are stored in lists. Use loops instead of repeated blocks.
- No magic numbers: every fixed value comes from `Settings`.

### 4.2 Definition of done

An issue is done when all of the following are true:

- [ ] Every acceptance criterion is checked.
- [ ] The code follows the conventions above and passes the penalty checklist (SR-601).
- [ ] Classes and methods are documented.
- [ ] The change was reviewed by the other developer in a pull request.
- [ ] The game runs from `src/main.py` without errors and the feature was exercised manually.
- [ ] The pull request is merged into `main` and the issue is closed automatically.

## 5. Roadmap

| Milestone | Epic | Grade weight | Exit criterion |
|-----------|------|--------------|----------------|
| Sprint 0 | E0 Foundation | none | Empty Pyxel window at the right size runs from `main.py`; repository and board ready. |
| Sprint 1 | E1 Objects and graphical interface | 0.5 | Static scene matches Figure 1 with all stations, board and counters visible. |
| Sprint 2 | E2 Chef movement | 0.5 | Both chefs move simultaneously and are confined to their zones. |
| Sprint 3 | E3 Ingredients, stations and recipes | 0.5 | All three dishes can be prepared and plated by hand-over. |
| Sprint 4 | E4 Orders, scoring and end of service | 0.5 | Game is playable from start to game over across several levels. |
| Sprint 5 | E5 Optional features | up to 0.5 | Selected optional features complete. |
| Delivery | E6 Quality, report and delivery | 0.5 | Zip uploaded to Aula Global. |

Suggested split of ownership: Developer A leads the engine side (kitchen, stations, chef, input); Developer B leads the domain side (ingredients, recipes, orders, scoring, board). Both review each other's pull requests. Interface agreements are written in `docs/design.md` (SR-004) before Sprint 1 starts.

Critical path: SR-003, SR-004, SR-102, SR-103, SR-201 to SR-203, SR-301, SR-302, SR-306 to SR-308, SR-402, SR-404, SR-406. Everything else can run in parallel once its dependencies are merged.

Sizes: S is up to 2 hours, M is up to half a day, L is a day or more.

## 6. Labels

| Label | Meaning |
|-------|---------|
| epic | Tracking issue grouping other issues |
| feature | New behaviour visible in the game |
| task | Technical or design work |
| docs | Documentation or report |
| chore | Repository, tooling or packaging |
| bug | Defect in existing behaviour |
| optional | Sprint 5 work |
| sprint-0 to sprint-5, delivery | Planning period |
| size-S, size-M, size-L | Effort estimate |
| priority-high | Blocks other work or grading |
| blocked | Waiting on another issue or a question |

## 7. Epics and issues

Each issue starts with a level-three heading so that the file can be split automatically (see the manual in section 8.7). Replace the issue IDs in the epic task lists with real issue numbers after import.

## Epic 0: Foundation

### E0 Foundation and project setup

**Labels:** epic, sprint-0
**Milestone:** Sprint 0

**Goal**

Establish the repository, tooling, constants and architecture so that the later sprints can proceed in parallel without rework.

**Child issues**

- [ ] SR-001 Bootstrap repository and team conventions
- [ ] SR-002 Project skeleton and Pyxel smoke test
- [ ] SR-003 Fixed constants in a Settings class
- [ ] SR-004 Class model and module layout

**Done when**

All child issues are closed and a Pyxel window of 384 x 352 pixels runs from `src/main.py`.

### SR-001 Bootstrap repository and team conventions

**Labels:** chore, sprint-0, size-S, priority-high
**Milestone:** Sprint 0
**Depends on:** none
**Suggested owner:** Pair

**Description**

Create the private repository, define the working agreements and set up the issue tracking structure described in the GitHub manual.

**Acceptance criteria**

- [ ] The repository is private and both developers have write access.
- [ ] `README.md` explains the purpose, requirements, setup, run command and folder layout.
- [ ] `.gitignore` covers Python caches, virtual environments, IDE and operating system files. The `.pyxres` file is tracked.
- [ ] `requirements.txt` pins the Pyxel version used in the course.
- [ ] Labels, milestones, issue template, pull request template and project board exist.
- [ ] Branch naming, commit message format and review rules are written in the README.
- [ ] The `main` branch is protected, or an equivalent team rule is documented if protection is unavailable on the plan in use.

### SR-002 Project skeleton and Pyxel smoke test

**Labels:** task, sprint-0, size-S, priority-high
**Milestone:** Sprint 0
**Depends on:** SR-001
**Suggested owner:** Developer A

**Description**

Create the minimal runnable application: folder layout, `Game` class owning the Pyxel loop and a `main.py` that only starts it.

**Acceptance criteria**

- [ ] Running `python src/main.py` opens a window of 384 x 352 pixels titled "Service Rush".
- [ ] Pyxel is initialised with 30 fps and `display_scale=2`.
- [ ] `Game` implements `update` and `draw` and is the only owner of `pyxel.run`.
- [ ] `main.py` contains no game logic: it creates `Game` and runs it.
- [ ] The `.pyxres` file in `assets/` loads without errors and the path works regardless of the directory the command is run from.
- [ ] A frame counter confirms that 30 frames elapse per second.

### SR-003 Fixed constants in a Settings class

**Labels:** task, sprint-0, size-M, priority-high
**Milestone:** Sprint 0
**Depends on:** SR-002
**Suggested owner:** Developer B

**Description**

Define every fixed value from the brief as a class attribute of `Settings`, grouped by topic. Derived values (frames) are computed from seconds and fps.

**Acceptance criteria**

- [ ] Display: screen 384 x 352, tile 32, sprite 16, board height 64, grid 12 x 9, fps 30.
- [ ] Timing: service 180 s, first order at 3 s, order limits 48 s, 60 s and 60 s, all also available in frames.
- [ ] Orders: at most 3 waiting, 4 orders in level 1 and one more per level.
- [ ] Scoring: points 10, 12, 12; penalties 5, 6, 6; failure limit 3; score floor 0.
- [ ] Recipes data (ingredients, equipment, points, time, penalty) defined as data that `RecipeBook` reads.
- [ ] Kitchen layout and chef start tiles defined as data (section 3.5).
- [ ] Key bindings for both chefs defined as data.
- [ ] No fixed value from the brief is repeated as a literal anywhere else in the code base.

### SR-004 Class model and module layout

**Labels:** docs, sprint-0, size-M, priority-high
**Milestone:** Sprint 0
**Depends on:** SR-003
**Suggested owner:** Pair

**Description**

Write `docs/design.md` with the class list, responsibilities, public methods between classes and the interaction matrix, so both developers can work against agreed interfaces.

**Acceptance criteria**

- [ ] Every class from section 3.3 has a responsibility, main attributes and main methods listed.
- [ ] The interface between `Chef`, `Kitchen` and `Station` (`interact`, carried dish access) is defined.
- [ ] The interface between `Service`, `OrderManager`, `ScoreKeeper` and `ServiceClock` is defined.
- [ ] Open questions from section 2 are resolved or escalated, with the decision written down.
- [ ] A first class diagram draft is included and reviewed by both developers.
- [ ] No behaviour is assigned to the main program.

## Epic 1: Objects and graphical interface (Sprint 1)

### E1 Objects and graphical interface

**Labels:** epic, sprint-1
**Milestone:** Sprint 1

**Goal**

Model the main game elements as classes and render the static scene: kitchen, stations, service board and sprites.

**Child issues**

- [ ] SR-101 Sprite sheet and sprite catalog
- [ ] SR-102 Kitchen layout as data and loader
- [ ] SR-103 Station hierarchy and static kitchen rendering
- [ ] SR-104 Ingredient, Container and Dish models with visual states
- [ ] SR-105 Recipe and RecipeBook data structures
- [ ] SR-106 Order model and waiting orders list
- [ ] SR-107 Service board layout
- [ ] SR-108 Static scene integration
- [ ] SR-109 Publish sprite sheet to the class repository

**Done when**

The static scene matches Figure 1 and the score, failure counter and timer are visible.

### SR-101 Sprite sheet and sprite catalog

**Labels:** task, sprint-1, size-L
**Milestone:** Sprint 1
**Depends on:** SR-002
**Suggested owner:** Developer B

**Description**

Create the 16 x 16 sprites in the Pyxel editor with a consistent retro palette and document where each sprite lives in the image bank. Check how to draw them at double size with the Pyxel version used in the course. Time spent here must stay limited, as visual appearance is not graded.

**Acceptance criteria**

- [ ] Sprites exist for floor, worktop, wall, hand-over surface, bin, delivery counter, dish stack, chopping board, blender, pan, and the five drawers.
- [ ] Optional sprites exist for sink and return counter.
- [ ] Ingredients have raw, chopped and processed (blended or cooked) sprites for tomato, potato, onion, egg and chorizo.
- [ ] Dishes have an empty sprite and one sprite for each finished recipe, plus a generic sprite for mixed or junk contents.
- [ ] Both chefs have a sprite for each facing direction.
- [ ] Ticket icons exist for the three recipes.
- [ ] `docs/sprites.md` lists every sprite name, image bank and coordinates.
- [ ] Sprites render at 32 x 32 on screen with a transparent color key.

### SR-102 Kitchen layout as data and loader

**Labels:** feature, sprint-1, size-M, priority-high
**Milestone:** Sprint 1
**Depends on:** SR-003
**Suggested owner:** Developer A

**Description**

Store the layout as a list of strings in `Settings` and provide a validation step so a wrong layout is detected at startup.

**Acceptance criteria**

- [ ] The layout is a list of 9 strings of 12 characters, matching section 3.5 and Figure 1.
- [ ] Validation checks dimensions, known tile codes, exactly four hand-over surfaces, exactly one of each unique station and one of each drawer.
- [ ] Optional codes `S` and `R` are replaced by wall and free worktop when the dish cycle is disabled.
- [ ] Chef start tiles are data, not code.
- [ ] The kitchen reads the layout once at startup; no position is hard-coded in any other class.

### SR-103 Station hierarchy and static kitchen rendering

**Labels:** feature, sprint-1, size-L, priority-high
**Milestone:** Sprint 1
**Depends on:** SR-101, SR-102
**Suggested owner:** Developer A

**Description**

Create the `Station` base class and its subclasses, build the grid in `Kitchen` and draw the floor and every station. Interaction behaviour comes later; this issue defines structure and drawing.

**Acceptance criteria**

- [ ] `Station` provides tile position, a single content slot and `draw()`; `interact(chef)` exists as an overridable method.
- [ ] Subclasses exist for worktop, hand-over surface, wall, drawer, chopping board, equipment (blender and pan), dish stack, delivery counter, bin, and the optional sink and return counter.
- [ ] `Kitchen` creates stations through a mapping from layout code to class, without a long `if` chain.
- [ ] The rendered kitchen matches Figure 1, including all four hand-over surfaces and both chopping boards.
- [ ] Each station can hold at most one element.
- [ ] Every class and method is documented.

### SR-104 Ingredient, Container and Dish models with visual states

**Labels:** feature, sprint-1, size-M, priority-high
**Milestone:** Sprint 1
**Depends on:** SR-101, SR-003
**Suggested owner:** Developer B

**Description**

Model ingredients with their state, a reusable `Container` holding a list of ingredients and an optional preparation, and `Dish` built on it. Each must draw itself according to its state.

**Acceptance criteria**

- [ ] `Ingredient` stores kind, processing state (whole, chopped, blended) and cooked flag, with methods to change state and a property telling whether it can be chopped.
- [ ] `Container` provides add, clear, transfer-to-another-container and emptiness queries, and keeps ingredients in a list.
- [ ] `Dish` reuses `Container` by composition or inheritance and exposes empty and full state; a dish is full when it has any content.
- [ ] A dish draws an empty sprite, a sprite for each finished recipe, or the generic mixed sprite.
- [ ] Ingredients draw a different sprite for raw, chopped and processed states.
- [ ] No attribute is public; read access uses properties.

### SR-105 Recipe and RecipeBook data structures

**Labels:** feature, sprint-1, size-M
**Milestone:** Sprint 1
**Depends on:** SR-003
**Suggested owner:** Developer B

**Description**

Create `Recipe` and `RecipeBook` from the data in `Settings`. Validation logic is implemented in SR-302; this issue provides the structures.

**Acceptance criteria**

- [ ] `Recipe` exposes name, ingredient signature, equipment kind, points, time limit in frames, penalty and icon through read-only properties.
- [ ] `RecipeBook` holds the three recipes in a list and offers lookup by name and random selection.
- [ ] Recipe data is read from `Settings`, not duplicated.
- [ ] Ingredient signatures describe kind and required state (for example chopped tomato).

### SR-106 Order model and waiting orders list

**Labels:** feature, sprint-1, size-S
**Milestone:** Sprint 1
**Depends on:** SR-105
**Suggested owner:** Developer B

**Description**

Define `Order` and the list of waiting orders inside `OrderManager`. Only the data structures are required in this sprint.

**Acceptance criteria**

- [ ] `Order` stores its recipe and remaining frames, with properties for remaining time and fraction left.
- [ ] `OrderManager` keeps waiting orders in a list with a maximum of 3.
- [ ] Adding an order beyond the limit is refused by the manager.
- [ ] The structures are documented in `docs/design.md`.

### SR-107 Service board layout

**Labels:** feature, sprint-1, size-M
**Milestone:** Sprint 1
**Depends on:** SR-101, SR-003
**Suggested owner:** Developer B

**Description**

Draw the top band of 384 x 64 pixels with room for three tickets on the left and the score, failure counter, timer and level on the right.

**Acceptance criteria**

- [ ] Three ticket slots fit at the same time inside the band.
- [ ] Score, failures and timer are visible and read their values from `ScoreKeeper` and `ServiceClock`.
- [ ] The board class draws only; it contains no scoring or timing logic.
- [ ] The timer is shown as minutes and seconds.
- [ ] Empty ticket slots render cleanly.

### SR-108 Static scene integration

**Labels:** task, sprint-1, size-S
**Milestone:** Sprint 1
**Depends on:** SR-103, SR-104, SR-107
**Suggested owner:** Pair

**Description**

Assemble board and kitchen in `Game.draw` and show both chefs on their start tiles as placeholders. This is the Sprint 1 review point.

**Acceptance criteria**

- [ ] The screen is 384 x 352 with the board on top and the kitchen below.
- [ ] A screenshot is stored in `docs/` and compared with Figure 1.
- [ ] No game logic exists in `main.py` or `Game.draw`.
- [ ] The penalty checklist (SR-601) was run on all Sprint 1 code.
- [ ] Milestone Sprint 1 is closed and tagged `sprint-1`.

### SR-109 Publish sprite sheet to the class repository

**Labels:** chore, sprint-1, size-S, priority-high
**Milestone:** Sprint 1
**Depends on:** SR-101
**Suggested owner:** Developer B

**Description**

The first three groups that upload their pyxres file to the class repository in Aula Global receive an extra 0.1 points, within the 2.5 cap. Upload as soon as the sprite sheet is usable.

**Acceptance criteria**

- [ ] The pyxres file loads in a clean checkout.
- [ ] The file follows the naming and size conventions of the common repository.
- [ ] The upload is confirmed in Aula Global and the date is noted in the issue.

## Epic 2: Chef movement (Sprint 2)

### E2 Chef movement

**Labels:** epic, sprint-2
**Milestone:** Sprint 2

**Goal**

Two fully controllable chefs, each confined to the floor of their own zone.

**Child issues**

- [ ] SR-201 Chef class and key bindings
- [ ] SR-202 Movement and facing
- [ ] SR-203 Collision detection
- [ ] SR-204 Chef rendering with carried item

**Done when**

Both chefs can be played at the same time and can never leave their zone.

### SR-201 Chef class and key bindings

**Labels:** feature, sprint-2, size-M, priority-high
**Milestone:** Sprint 2
**Depends on:** SR-103
**Suggested owner:** Developer A

**Description**

Create `Chef` with position, facing, carried dish slot and key bindings passed through its constructor. Both chefs are instances of the same class that differ only in data.

**Acceptance criteria**

- [ ] Chef 1 uses W, A, S, D for movement and left Shift for the action; Chef 2 uses the arrow keys and right Shift.
- [ ] Bindings come from `Settings`, not from literals in the class.
- [ ] Each chef has a zone defined by the rows it may walk on.
- [ ] The carried dish is private, exposed through a property, and starts empty-handed.
- [ ] Input is read inside `Chef.update`, not in `Game`.

### SR-202 Movement and facing

**Labels:** feature, sprint-2, size-M, priority-high
**Milestone:** Sprint 2
**Depends on:** SR-201
**Suggested owner:** Developer A

**Description**

Implement four-direction, tile-based movement with a fixed delay between steps. Pressing a direction towards a blocked tile changes facing without moving, so chefs can face worktops.

**Acceptance criteria**

- [ ] Movement is in four directions only; diagonal input is resolved by a documented priority rule.
- [ ] Facing updates on every direction press, even when the move is blocked.
- [ ] The chef exposes the tile it is facing to the kitchen.
- [ ] Both chefs move at the same time without interfering with each other.
- [ ] Speed is a constant from `Settings`.

### SR-203 Collision detection

**Labels:** feature, sprint-2, size-M, priority-high
**Milestone:** Sprint 2
**Depends on:** SR-202
**Suggested owner:** Developer A

**Description**

Allow chefs to stand only on floor tiles of their own zone. Worktops, the dividing counter and the screen limits are obstacles.

**Acceptance criteria**

- [ ] `Kitchen` answers whether a tile is walkable for a given zone.
- [ ] Chef 1 can walk rows 1 to 3 only; Chef 2 can walk rows 5 to 7 only.
- [ ] A chef can never cross or stand on the dividing counter or a worktop.
- [ ] Chefs cannot leave the grid.
- [ ] Unit tests cover the four borders of each zone.

### SR-204 Chef rendering with carried item

**Labels:** feature, sprint-2, size-S
**Milestone:** Sprint 2
**Depends on:** SR-201, SR-101
**Suggested owner:** Developer B

**Description**

Draw each chef with a sprite matching the facing direction and the carried dish on top or next to the chef.

**Acceptance criteria**

- [ ] The chef sprite changes with the facing direction.
- [ ] A carried dish is visible and shows its content state.
- [ ] Chef 1 and Chef 2 are visually distinguishable.
- [ ] Sprint 2 code passes the penalty checklist and the milestone is tagged `sprint-2`.

## Epic 3: Ingredients, stations and recipes (Sprint 3)

### E3 Ingredients, stations and recipes

**Labels:** epic, sprint-3
**Milestone:** Sprint 3

**Goal**

Implement the contextual action key and the whole flow of ingredients, so that a complete dish can be prepared and plated by both chefs.

**Child issues**

- [ ] SR-301 Interaction framework
- [ ] SR-302 Recipe validation and preparation outcome
- [ ] SR-303 Drawers
- [ ] SR-304 Free worktops and hand-over surfaces
- [ ] SR-305 Dish stack
- [ ] SR-306 Chopping boards
- [ ] SR-307 Equipment: blender and pan
- [ ] SR-308 Pouring between dishes
- [ ] SR-309 Bin
- [ ] SR-310 Visual states of contents
- [ ] SR-311 End-to-end preparation test

**Done when**

Each recipe can be cooked, handed over and left ready for delivery, with no orders or scoring yet.

### SR-301 Interaction framework

**Labels:** feature, sprint-3, size-M, priority-high
**Milestone:** Sprint 3
**Depends on:** SR-203, SR-103
**Suggested owner:** Developer A

**Description**

Implement the action key: `Chef.act` asks the kitchen for the station in front and calls `station.interact(chef)`. Each station subclass overrides the method. Cases not handled do nothing.

**Acceptance criteria**

- [ ] `Chef.act` contains no per-station-type logic.
- [ ] Facing a floor tile, the other chef or a wall does nothing.
- [ ] The chef exposes a minimal API to stations: current dish, take dish, give dish, and a flag for being empty-handed.
- [ ] Each row of the interaction matrix (section 3.4) has a test or a documented manual test.
- [ ] Adding a new station type requires no change in `Chef`.

### SR-302 Recipe validation and preparation outcome

**Labels:** feature, sprint-3, size-M, priority-high
**Milestone:** Sprint 3
**Depends on:** SR-104, SR-105
**Suggested owner:** Developer B

**Description**

Given an equipment kind and a list of ingredients, `RecipeBook` returns the matching recipe or nothing. A match requires the exact set of ingredients: nothing missing and nothing extra, regardless of order.

**Acceptance criteria**

- [ ] Validation compares ingredient kind and state and respects quantities (two units are different from one).
- [ ] The same ingredients in a different order give the same result.
- [ ] Extra or missing ingredients return no recipe.
- [ ] A valid recipe in the wrong equipment returns no recipe.
- [ ] When no recipe matches, the equipment still processes the contents (blended or cooked) and the result is flagged as unusable for any recipe.
- [ ] Unit tests cover all three recipes, a missing item, an extra item and a wrong equipment case.

### SR-303 Drawers

**Labels:** feature, sprint-3, size-S
**Milestone:** Sprint 3
**Depends on:** SR-301, SR-104
**Suggested owner:** Developer A

**Description**

Each drawer is an unlimited source of one raw ingredient. Facing a drawer with a dish adds the ingredient to the dish.

**Acceptance criteria**

- [ ] Five drawers exist: onion, egg and chorizo in the upper zone; tomato and potato in the lower zone.
- [ ] An empty or loose-content dish gets one new raw ingredient per action.
- [ ] A dish holding a finished preparation rejects the ingredient.
- [ ] An empty-handed chef facing a drawer does nothing.
- [ ] A single `Drawer` class is used with the ingredient kind as data.

### SR-304 Free worktops and hand-over surfaces

**Labels:** feature, sprint-3, size-M
**Milestone:** Sprint 3
**Depends on:** SR-301
**Suggested owner:** Developer A

**Description**

Any free worktop tile and every hand-over surface can hold one dish. Hand-over surfaces are the only tiles reachable by both chefs.

**Acceptance criteria**

- [ ] A chef carrying a dish leaves it on an empty surface; an empty-handed chef picks it up.
- [ ] A surface already holding a dish does not accept another dish by placement.
- [ ] Both chefs can place and pick up on the four hand-over surfaces.
- [ ] Nothing is ever dropped on the floor.
- [ ] A chef cannot reach worktops of the other zone.

### SR-305 Dish stack

**Labels:** feature, sprint-3, size-S
**Milestone:** Sprint 3
**Depends on:** SR-301
**Suggested owner:** Developer A

**Description**

The dish stack in the lower zone is an unlimited source of empty dishes that only Chef 2 can take.

**Acceptance criteria**

- [ ] An empty-handed Chef 2 facing the stack receives an empty dish.
- [ ] A chef that already carries something does not receive a second dish.
- [ ] Chef 1 can never interact with the stack.
- [ ] Chef 2 can pass the dish to Chef 1 through a hand-over surface.

### SR-306 Chopping boards

**Labels:** feature, sprint-3, size-M
**Milestone:** Sprint 3
**Depends on:** SR-301, SR-104
**Suggested owner:** Developer B

**Description**

One chopping board in each zone. A full dish deposits its contents on the board, where choppable ingredients are chopped; an empty dish takes everything out again.

**Acceptance criteria**

- [ ] The same class serves both boards.
- [ ] After depositing, the chef keeps an empty dish and the board holds the contents.
- [ ] All choppable ingredients (tomato, potato, onion, chorizo) become chopped; the egg is unchanged.
- [ ] An empty dish facing the board takes all contents out.
- [ ] An occupied board rejects a new deposit.
- [ ] Chopping is instantaneous in this sprint; the design leaves room for the timed version in SR-507.

### SR-307 Equipment: blender and pan

**Labels:** feature, sprint-3, size-L, priority-high
**Milestone:** Sprint 3
**Depends on:** SR-302, SR-301
**Suggested owner:** Developer B

**Description**

Create `Equipment` with `Blender` and `Pan` subclasses. A full dish deposits all contents; the equipment processes them; an empty dish takes the result out.

**Acceptance criteria**

- [ ] The blender is in the upper zone and the pan in the lower zone, according to the layout.
- [ ] A valid recipe for the equipment becomes that finished preparation.
- [ ] An invalid mix is still blended or cooked and becomes unusable for any recipe.
- [ ] Everything is taken out together, only with an empty dish.
- [ ] A full dish facing occupied equipment is rejected.
- [ ] Processing is instantaneous in this sprint; the design leaves room for the timed version in SR-508.

### SR-308 Pouring between dishes

**Labels:** feature, sprint-3, size-M
**Milestone:** Sprint 3
**Depends on:** SR-304, SR-104
**Suggested owner:** Developer A

**Description**

A chef carrying a full dish and facing a station that holds a dish pours the contents into that dish. This is the mechanism for combining ingredients from both zones.

**Acceptance criteria**

- [ ] The source dish becomes empty and stays in the chef's hands.
- [ ] The target dish receives all ingredients in its list.
- [ ] Pouring is rejected when either dish holds a finished preparation.
- [ ] It works on free worktops and on hand-over surfaces.
- [ ] A chef carrying an empty dish facing a station with a dish does nothing.

### SR-309 Bin

**Labels:** feature, sprint-3, size-S
**Milestone:** Sprint 3
**Depends on:** SR-301
**Suggested owner:** Developer A

**Description**

The bin on the dividing counter is shared by both chefs. A full dish thrown in loses its content but the dish is never destroyed.

**Acceptance criteria**

- [ ] The dish is emptied and stays in the chef's hands.
- [ ] Binning is never counted as a failure.
- [ ] An empty dish or an empty-handed chef does nothing at the bin.
- [ ] Both chefs can use the bin.

### SR-310 Visual states of contents

**Labels:** feature, sprint-3, size-M
**Milestone:** Sprint 3
**Depends on:** SR-104, SR-306, SR-307
**Suggested owner:** Developer B

**Description**

Make the content of dishes, chopping boards and equipment visible and consistent with its state.

**Acceptance criteria**

- [ ] A dish shows its loose ingredients with raw or chopped sprites.
- [ ] A dish with a finished recipe shows the recipe sprite.
- [ ] A dish with unusable content shows the generic sprite.
- [ ] A chopping board and a piece of equipment show that they hold something.
- [ ] Changes in state are visible on the frame they happen.

### SR-311 End-to-end preparation test

**Labels:** task, sprint-3, size-M
**Milestone:** Sprint 3
**Depends on:** SR-303 to SR-310
**Suggested owner:** Pair

**Description**

Write and run a scripted manual test that prepares each recipe using the hand-over surfaces, plus negative cases. This closes Sprint 3.

**Acceptance criteria**

- [ ] Gazpacho is prepared with both chefs and ends as a finished dish ready for Chef 1.
- [ ] Spanish omelette and broken eggs with chorizo are prepared the same way.
- [ ] A wrong mix is cooked and then thrown in the bin without failure.
- [ ] The steps are written in `docs/test-plan.md` and the results are noted.
- [ ] The penalty checklist (SR-601) is run on Sprint 3 code and the milestone is tagged `sprint-3`.

## Epic 4: Orders, scoring and end of service (Sprint 4)

### E4 Orders, scoring and end of service

**Labels:** epic, sprint-4
**Milestone:** Sprint 4

**Goal**

Turn the kitchen into a playable game: orders, delivery, scoring, failures, timer, levels and game over.

**Child issues**

- [ ] SR-401 Frame clock and service timer
- [ ] SR-402 Order generation and scheduling
- [ ] SR-403 Order expiry, penalty and failure
- [ ] SR-404 Delivery counter
- [ ] SR-405 Score keeper
- [ ] SR-406 Game state machine
- [ ] SR-407 Level progression and cleanup
- [ ] SR-408 Ticket rendering

**Done when**

The game is playable from start to game over across several levels.

### SR-401 Frame clock and service timer

**Labels:** feature, sprint-4, size-S, priority-high
**Milestone:** Sprint 4
**Depends on:** SR-003
**Suggested owner:** Developer B

**Description**

`ServiceClock` counts frames and exposes the remaining time of the 3-minute service.

**Acceptance criteria**

- [ ] The service lasts 5400 frames (180 s at 30 fps), taken from `Settings`.
- [ ] Properties expose remaining frames, remaining seconds and a finished flag.
- [ ] The board shows the timer as minutes and seconds.
- [ ] The clock stops advancing when the service is not in the playing state.

### SR-402 Order generation and scheduling

**Labels:** feature, sprint-4, size-L, priority-high
**Milestone:** Sprint 4
**Depends on:** SR-106, SR-401
**Suggested owner:** Developer B

**Description**

`OrderManager` creates random orders according to the schedule in assumption A9, respecting the limit of 3 waiting orders.

**Acceptance criteria**

- [ ] The first order appears 3 seconds after the service starts.
- [ ] A level with level number n creates 3 + n orders, so level 1 has 4.
- [ ] Orders are spread evenly over the service.
- [ ] Recipes are picked at random from the three available.
- [ ] If 3 orders are waiting, the next one appears as soon as there is room.
- [ ] Orders still waiting when the service ends are not failures.
- [ ] Unit tests cover the schedule and the waiting limit.

### SR-403 Order expiry, penalty and failure

**Labels:** feature, sprint-4, size-M
**Milestone:** Sprint 4
**Depends on:** SR-402, SR-405
**Suggested owner:** Developer B

**Description**

Each order counts down every frame. When it reaches zero the order is lost.

**Acceptance criteria**

- [ ] The order is removed from the waiting list when its time runs out.
- [ ] One failure is added and the recipe penalty (5, 6 or 6) is subtracted from the score.
- [ ] The score never goes below zero.
- [ ] Several orders expiring in different frames are handled independently.
- [ ] Unit tests cover expiry with a zero score.

### SR-404 Delivery counter

**Labels:** feature, sprint-4, size-M, priority-high
**Milestone:** Sprint 4
**Depends on:** SR-402, SR-405, SR-307
**Suggested owner:** Developer A

**Description**

Only Chef 1 reaches the delivery counter in the upper zone. A full dish handed in completes the matching order or adds a failure.

**Acceptance criteria**

- [ ] A finished dish that matches a waiting order completes the oldest one for that recipe and awards its points.
- [ ] A dish with loose ingredients, unusable content or a recipe nobody ordered adds one failure and no score deduction.
- [ ] The dish disappears in every full-dish case and the chef is left empty-handed.
- [ ] An empty dish does nothing.
- [ ] The completed order disappears from the board and frees a slot.

### SR-405 Score keeper

**Labels:** feature, sprint-4, size-S, priority-high
**Milestone:** Sprint 4
**Depends on:** SR-003
**Suggested owner:** Developer B

**Description**

`ScoreKeeper` owns the score and the failure counter and also tracks the points earned in the current level, needed later for stars.

**Acceptance criteria**

- [ ] Score and failures are exposed through read-only properties.
- [ ] Methods exist to add points, apply a penalty and add a failure.
- [ ] The score is clamped at zero.
- [ ] A property reports whether the failure limit of 3 has been reached.
- [ ] Level points can be reset without touching the total score or the failures.

### SR-406 Game state machine

**Labels:** feature, sprint-4, size-M, priority-high
**Milestone:** Sprint 4
**Depends on:** SR-401, SR-405
**Suggested owner:** Developer A

**Description**

`Game` manages the states playing, service over and game over, delegating behaviour to the current service and screens.

**Acceptance criteria**

- [ ] When the timer runs out the game stops and the score stays visible on the board.
- [ ] After the third failure the game stops and shows "Game over" and the score stays visible.
- [ ] No chef input or order update happens outside the playing state.
- [ ] State transitions are implemented in one place and documented.
- [ ] Without optional screens, the next level starts after a short pause defined as a constant.

### SR-407 Level progression and cleanup

**Labels:** feature, sprint-4, size-M
**Milestone:** Sprint 4
**Depends on:** SR-406, SR-402
**Suggested owner:** Developer A

**Description**

After a service ends by timer, clean the kitchen and start the next level with one more order.

**Acceptance criteria**

- [ ] Orders, dishes, station contents and carried items are cleared.
- [ ] Both chefs return to their start tiles.
- [ ] The next level has one more order than the previous one.
- [ ] Score and failures carry over.
- [ ] The level number is shown on the board.
- [ ] The penalty checklist (SR-601) is run on Sprint 4 code and the milestone is tagged `sprint-4`.

### SR-408 Ticket rendering

**Labels:** feature, sprint-4, size-M
**Milestone:** Sprint 4
**Depends on:** SR-107, SR-402
**Suggested owner:** Developer B

**Description**

Draw one ticket per waiting order with the dish icon, the ingredients and the time counter.

**Acceptance criteria**

- [ ] Each ticket shows the recipe icon, the ingredients and the remaining time.
- [ ] The countdown changes visibly when time is low.
- [ ] Up to three tickets fit at once without overlap.
- [ ] Tickets disappear when the order is completed or lost.

## Epic 5: Optional features (Sprint 5)

### E5 Optional features

**Labels:** epic, sprint-5, optional
**Milestone:** Sprint 5

**Goal**

Earn up to 0.5 additional points, never exceeding the 2.5 project cap. Start only when Sprint 4 is stable and the report outline exists.

**Child issues**

- [ ] SR-501 Sound effects (0.10)
- [ ] SR-502 Start screen with controls (0.10 together with SR-503 and SR-504)
- [ ] SR-503 Star rating
- [ ] SR-504 End-of-service and game over screens
- [ ] SR-505 Dish pool and dirty dishes (0.20 together with SR-506)
- [ ] SR-506 Sink and return counter
- [ ] SR-507 Timed chopping (0.20 together with SR-508)
- [ ] SR-508 Timed cooking

**Done when**

Every selected feature meets its criteria and is described in the report.

### SR-501 Sound effects

**Labels:** feature, sprint-5, optional, size-M
**Milestone:** Sprint 5
**Depends on:** SR-407
**Suggested owner:** Developer B

**Description**

Add short sound effects for chopping, a preparation being ready, a dish being served and an order being lost, through a `SoundPlayer` class.

**Acceptance criteria**

- [ ] Sounds are defined in the pyxres file and played by name through `SoundPlayer`.
- [ ] Each of the four events triggers its own sound.
- [ ] Logic classes report events; they do not call Pyxel sound functions directly.
- [ ] Sound can be muted with a documented key.

### SR-502 Start screen with controls

**Labels:** feature, sprint-5, optional, size-S
**Milestone:** Sprint 5
**Depends on:** SR-406
**Suggested owner:** Developer B

**Description**

Show a start screen with the controls of both chefs before the first level.

**Acceptance criteria**

- [ ] The screen shows the movement and action keys of both chefs.
- [ ] The game starts on a documented key press.
- [ ] The screen is a new state in the state machine and does not add logic to `main.py`.

### SR-503 Star rating

**Labels:** feature, sprint-5, optional, size-S
**Milestone:** Sprint 5
**Depends on:** SR-405
**Suggested owner:** Developer B

**Description**

Compute one, two or three stars from the points scored in the level, according to assumption A12.

**Acceptance criteria**

- [ ] The result is never zero, even if the service ended through failures.
- [ ] Thresholds are constants in `Settings`.
- [ ] Unit tests cover each threshold boundary.

### SR-504 End-of-service and game over screens

**Labels:** feature, sprint-5, optional, size-M
**Milestone:** Sprint 5
**Depends on:** SR-503, SR-406
**Suggested owner:** Developer A

**Description**

At the end of each level show the score and stars and let the player continue or quit. After "Game over" let the player play again or quit.

**Acceptance criteria**

- [ ] End of service shows score, stars and the options continue or quit.
- [ ] Game over shows the options play again or quit.
- [ ] Play again resets score, failures and level.
- [ ] Navigation keys are documented on the screen.

### SR-505 Dish pool and dirty dishes

**Labels:** feature, sprint-5, optional, size-L
**Milestone:** Sprint 5
**Depends on:** SR-404, SR-309
**Suggested owner:** Developer A

**Description**

Limit the number of dishes. A served dish comes back dirty to the return counter after a delay. A dish emptied in the bin becomes dirty. Nothing can be plated without a clean dish.

**Acceptance criteria**

- [ ] A fixed number of dishes exists (assumption A13) and the stack runs out when all are in use.
- [ ] A served dish returns dirty to the return counter after the configured delay.
- [ ] A dish emptied in the bin becomes dirty and stays dirty in the chef's hands.
- [ ] A dirty dish cannot receive ingredients.
- [ ] The feature can be disabled through `Settings`, restoring the base behaviour.

### SR-506 Sink and return counter

**Labels:** feature, sprint-5, optional, size-M
**Milestone:** Sprint 5
**Depends on:** SR-505
**Suggested owner:** Developer A

**Description**

Add the sink on the dividing counter and the return counter in the lower zone. Chef 2 washes dirty dishes.

**Acceptance criteria**

- [ ] Chef 2 picks up a dirty dish from the return counter.
- [ ] Chef 2 facing the sink with a dirty dish washes it; it stays clean in his hands.
- [ ] Chef 1 cannot wash.
- [ ] Both stations are loaded from the layout only when the dish cycle is enabled.

### SR-507 Timed chopping

**Labels:** feature, sprint-5, optional, size-M
**Milestone:** Sprint 5
**Depends on:** SR-306
**Suggested owner:** Developer B

**Description**

Chopping takes time and blocks the chef while it happens.

**Acceptance criteria**

- [ ] The chef cannot move or act during the chopping time.
- [ ] A progress indicator is visible on the board or above the chef.
- [ ] The duration is a constant in frames.
- [ ] The other chef can keep playing.

### SR-508 Timed cooking

**Labels:** feature, sprint-5, optional, size-M
**Milestone:** Sprint 5
**Depends on:** SR-307
**Suggested owner:** Developer B

**Description**

Cooking and blending take time but do not block the chef.

**Acceptance criteria**

- [ ] Equipment shows progress while processing.
- [ ] The contents can only be taken out when processing is finished.
- [ ] The chef can do other things while the equipment is working.
- [ ] A visual or sound cue signals when the preparation is ready.

## Epic 6: Quality, report and delivery

### E6 Quality, report and delivery

**Labels:** epic, delivery
**Milestone:** Delivery

**Goal**

Avoid penalties, document the work and deliver the zip file correctly.

**Child issues**

- [ ] SR-601 Penalty checklist review
- [ ] SR-602 Documentation and comments pass
- [ ] SR-603 Test plan and playtest
- [ ] SR-604 Class diagram
- [ ] SR-605 Report
- [ ] SR-606 Packaging
- [ ] SR-607 Final release and submission

**Done when**

The zip is uploaded to Aula Global and the upload is confirmed.

### SR-601 Penalty checklist review

**Labels:** task, delivery, size-M, priority-high
**Milestone:** Delivery
**Depends on:** none (repeat at the end of every sprint)
**Suggested owner:** Pair

**Description**

Run a structured self-audit against the grading penalties and fix findings before closing each sprint and before delivery.

**Acceptance criteria**

- [ ] Comments: every class and method has a docstring; non-trivial blocks have inline comments.
- [ ] Methods: no method needs scrolling to be read; helpers extracted where needed.
- [ ] No unused methods or attributes remain.
- [ ] No repeated blocks that should be loops.
- [ ] Orders and ingredients are lists.
- [ ] All attributes are private and created in `__init__`; properties are used for outside access.
- [ ] No code exists outside classes except the main program.
- [ ] No game logic exists in `main.py`.
- [ ] Only course-taught constructs are used.
- [ ] The audit result is recorded in the issue.

### SR-602 Documentation and comments pass

**Labels:** docs, delivery, size-M
**Milestone:** Delivery
**Depends on:** SR-407
**Suggested owner:** Pair

**Description**

Final read-through of the whole code base to make comments accurate, consistent and in English.

**Acceptance criteria**

- [ ] Each docstring states purpose, parameters and return value where relevant.
- [ ] Inline comments explain intent, not syntax.
- [ ] Names are consistent across modules.
- [ ] No commented-out code or debugging output is left.

### SR-603 Test plan and playtest

**Labels:** task, delivery, size-M
**Milestone:** Delivery
**Depends on:** SR-407
**Suggested owner:** Pair

**Description**

Define scenarios in `docs/test-plan.md`, play full sessions and log defects as bug issues.

**Acceptance criteria**

- [ ] Scenarios cover each recipe, each interaction matrix row, expiry, wrong hand-in, level change and game over.
- [ ] At least two complete sessions of several levels are played with both developers.
- [ ] Every defect is logged as an issue with the `bug` label and closed or explicitly deferred.
- [ ] Results are summarised for the report.

### SR-604 Class diagram

**Labels:** docs, delivery, size-M
**Milestone:** Delivery
**Depends on:** SR-407
**Suggested owner:** Developer A

**Description**

Produce the final class diagram for the report from the real code.

**Acceptance criteria**

- [ ] All classes appear with main attributes and methods and their relationships (inheritance, composition, association).
- [ ] The diagram matches the code, not the initial plan.
- [ ] It is exported as an image legible on an A4 page.

### SR-605 Report

**Labels:** docs, delivery, size-L, priority-high
**Milestone:** Delivery
**Depends on:** SR-604, SR-603
**Suggested owner:** Pair

**Description**

Write the PDF report, maximum 10 pages, with the required content.

**Acceptance criteria**

- [ ] Cover page, index and a brief summary.
- [ ] Class diagram and description of the classes with main attributes and methods.
- [ ] General description of the main algorithms (movement and collision, interaction dispatch, recipe validation, order scheduling, scoring).
- [ ] Work carried out, functionalities included, unimplemented parts and additional functionalities.
- [ ] Game user manual explaining how to play.
- [ ] Conclusions: summary of the work, main problems encountered, personal comments, evaluation and aspects to improve.
- [ ] Total length is 10 pages or fewer.
- [ ] Exported as a PDF and checked for readable diagrams.

### SR-606 Packaging

**Labels:** chore, delivery, size-S, priority-high
**Milestone:** Delivery
**Depends on:** SR-602, SR-605
**Suggested owner:** Developer B

**Description**

Create the deliverable zip and verify it on a clean machine or directory.

**Acceptance criteria**

- [ ] The zip is named `initials1-initials2.zip`.
- [ ] It contains the report PDF, the `.py` files and the `.pyxres` file.
- [ ] It contains no caches, virtual environments or unrelated files.
- [ ] After unzipping in a new location, the game runs with the documented command.
- [ ] The resource path works from the unzipped location.

### SR-607 Final release and submission

**Labels:** chore, delivery, size-S, priority-high
**Milestone:** Delivery
**Depends on:** SR-606
**Suggested owner:** Pair

**Description**

Tag the final version and upload the zip before the deadline published in Aula Global.

**Acceptance criteria**

- [ ] All milestones are closed and the final regression pass is complete.
- [ ] The commit is tagged `v1.0`.
- [ ] The zip is uploaded to Aula Global and the confirmation is stored.
- [ ] The repository remains private.

## 8. GitHub manual

A short guide to create and run the project on GitHub. Commands assume a terminal on macOS or Linux; adapt paths on Windows. The GitHub CLI is called `gh`.

### 8.1 Requirements

- A GitHub account for each developer.
- Git and the GitHub CLI installed (`git --version`, `gh --version`).
- Authentication done once with `gh auth login`.
- Identity configured once:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 8.2 Create the repository

Keep the repository private. The brief penalises plagiarism for both parties, and a public repository exposes the code.

```bash
gh repo create service-rush --private --clone --description "Service Rush final project"
cd service-rush
```

Alternative through the web: GitHub, New repository, private, add a README and a Python `.gitignore`.

### 8.3 Add your partner

Web: Settings, Collaborators, Add people, role Write. Or with the CLI:

```bash
gh api -X PUT repos/:owner/service-rush/collaborators/PARTNER_USERNAME -f permission=push
```

The invitation must be accepted by your partner.

### 8.4 First commit and structure

Create the folders from section 3.2, add this plan as `docs/PROJECT_PLAN.md`, then:

```bash
mkdir -p src assets docs tests .github/ISSUE_TEMPLATE
git add .
git commit -m "SR-001: initial project structure"
git push -u origin main
```

Suggested `.gitignore` content:

```
__pycache__/
*.pyc
.venv/
venv/
.idea/
.vscode/
.DS_Store
*.zip
dist/
```

Do not ignore `.pyxres`. It is a deliverable.

### 8.5 Labels and milestones

Create the labels from section 6. `--force` updates a label if it already exists.

```bash
gh label create epic --color 5319E7 --description "Tracking issue" --force
gh label create feature --color 0E8A16 --description "New game behaviour" --force
gh label create task --color 1D76DB --description "Technical or design work" --force
gh label create docs --color 0075CA --description "Documentation or report" --force
gh label create chore --color C5DEF5 --description "Repository, tooling, packaging" --force
gh label create bug --color D73A4A --description "Defect" --force
gh label create optional --color FBCA04 --description "Sprint 5 work" --force
gh label create priority-high --color B60205 --description "Blocks other work or grading" --force
gh label create blocked --color 000000 --description "Waiting on something" --force
for s in 0 1 2 3 4 5; do gh label create "sprint-$s" --color BFD4F2 --force; done
gh label create delivery --color BFD4F2 --force
for z in S M L; do gh label create "size-$z" --color EDEDED --force; done
```

Create the milestones and set their due dates in the web interface once the deadline is known:

```bash
for m in "Sprint 0" "Sprint 1" "Sprint 2" "Sprint 3" "Sprint 4" "Sprint 5" "Delivery"; do
  gh api repos/:owner/:repo/milestones -f title="$m" > /dev/null
done
```

### 8.6 Templates

Add the issue template and the pull request template from Appendix A:

- `.github/ISSUE_TEMPLATE/task.md`
- `.github/pull_request_template.md`

Commit them to `main`.

### 8.7 Import this plan as issues

Each epic and issue in section 7 starts with a level-three heading and carries its labels and milestone in the first lines. Save this document as `docs/PROJECT_PLAN.md` and split it into one file per issue:

```bash
mkdir -p issues
awk '
/^### (SR-|E)[0-9]/ { if (out != "") close(out); out = "issues/" $2 ".md" }
/^## / || /^# / { if (out != "") close(out); out = "" }
out != "" { print > out }
' docs/PROJECT_PLAN.md
ls issues | head
```

Create the issues. Epics are created first because their files sort first. The pause avoids GitHub rate limits.

```bash
for f in issues/E*.md issues/SR-*.md; do
  title=$(head -n 1 "$f" | sed 's/^### //')
  labels=$(grep -m 1 '^\*\*Labels:\*\*' "$f" | sed 's/^\*\*Labels:\*\* //')
  milestone=$(grep -m 1 '^\*\*Milestone:\*\*' "$f" | sed 's/^\*\*Milestone:\*\* //')
  tail -n +2 "$f" > /tmp/issue_body.md
  gh issue create --title "$title" --body-file /tmp/issue_body.md --label "$labels" --milestone "$milestone"
  sleep 2
done
```

Run it once only. If it stops midway, check `gh issue list --limit 100` and create the missing ones by hand to avoid duplicates. Delete the `issues/` folder afterwards (`rm -r issues`) and do not commit it.

If you prefer to create issues manually, open a new issue on GitHub, paste the heading text as the title and the rest as the body, and set labels and milestone from the first lines.

### 8.8 Link epics to their issues

Open each epic issue and replace the plain issue IDs in its task list by issue numbers, for example:

```
- [ ] #8 SR-001 Bootstrap repository and team conventions
```

GitHub then shows progress on the epic as children are closed. If sub-issues are available in your account, add the children as sub-issues of the epic instead; both approaches can coexist.

### 8.9 Project board

1. Open the Projects tab and create a new project from the Board template.
2. Name it "Service Rush".
3. Use the columns Backlog, Ready, In progress, In review and Done.
4. Add custom fields: Size (S, M, L) and Sprint (a single-select or an iteration).
5. Enable the built-in workflows that add new issues and move closed issues to Done.
6. Add all issues to the board (the "Add item" bar accepts a repository filter, or enable auto-add).
7. Work from the board: only pick items from Ready; a maximum of two items In progress per developer.

### 8.10 Daily workflow

1. Pick an issue from Ready, assign yourself and move it to In progress.
2. Update `main` and create a branch named after the issue:

```bash
git switch main
git pull
git switch -c feature/SR-103-station-hierarchy
```

3. Work in small commits. Message format: issue ID, colon, imperative summary, 72 characters at most:

```bash
git add src/stations.py
git commit -m "SR-103: add Station base class and subclasses"
```

4. Push and open a pull request:

```bash
git push -u origin feature/SR-103-station-hierarchy
gh pr create --fill
```

5. In the pull request description write `Closes #N` so the issue closes on merge, and complete the checklist from the template.
6. The other developer reviews: reads the diff, runs the branch, checks acceptance criteria, comments or approves.
7. Merge with "Squash and merge" and delete the branch. Then locally:

```bash
git switch main
git pull
git branch -d feature/SR-103-station-hierarchy
```

Rules of thumb: never commit directly to `main`; keep branches short-lived (one issue, one or two days at most); pull `main` into your branch before opening the pull request if it moved.

### 8.11 Repository settings

- Settings, General, Pull Requests: allow squash merging only and enable "Automatically delete head branches".
- Settings, Branches (or Rules): protect `main`, require a pull request and one approval, and disallow force pushes. Availability of these rules on private repositories depends on the account plan. If they are unavailable, apply the same rules by convention and check them in review.

### 8.12 Working with the pyxres file

The `.pyxres` file is binary and Git cannot merge it. To avoid conflicts:

- Only one developer edits it at a time. Announce it in the related issue before starting.
- Commit and push the file immediately after every editing session, in a commit that changes nothing else.
- The other developer pulls before touching it.
- If a conflict happens, keep one version (`git checkout --theirs assets/service_rush.pyxres` or `--ours`) and redo the lost edits.

### 8.13 Sprint routine

At the start of each sprint:

- Review the milestone's issues, adjust sizes and move the first ones to Ready.
- Check dependencies and agree who takes which issue.

During the sprint:

- Each developer posts a short note on the issue when it is blocked and adds the `blocked` label.
- Bugs found are logged as new issues with the `bug` label and linked to the originating issue.
- Scope changes are written in the issue, not agreed verbally.

At the end of the sprint:

- Run the penalty checklist (SR-601) and the sprint test.
- Close the milestone and tag the release:

```bash
git switch main
git pull
git tag -a sprint-1 -m "Sprint 1 complete"
git push origin sprint-1
```

- Move unfinished issues to the next milestone and note why.

### 8.14 Packaging the delivery

From a clean `main`:

```bash
git switch main
git pull
git status
mkdir -dist 2>/dev/null; mkdir -p dist/pkg
cp -r src assets dist/pkg/
cp docs/report.pdf dist/pkg/
cd dist/pkg
zip -r ../abc-def.zip . -x "*/__pycache__/*" "*.pyc" ".DS_Store"
cd ../..
```

Replace `abc-def` with the initials of both students in the required format. Unzip the result in a temporary folder and run the game before uploading to Aula Global. Finally tag the version:

```bash
git tag -a v1.0 -m "Final delivery"
git push origin v1.0
```

### 8.15 Common situations

| Situation | What to do |
|-----------|------------|
| Committed on `main` by mistake, not pushed | `git switch -c feature/SR-XXX-name` then `git switch main` and `git reset --hard origin/main`. |
| Last commit has a typo in the message | `git commit --amend` (only if not pushed). |
| Need to undo a pushed commit | `git revert <hash>` and push. |
| Merge conflict when updating a branch | `git pull origin main`, edit the marked files, `git add` them, `git commit`. |
| Need to switch task with unfinished work | `git stash`, switch branch, later `git stash pop`. |
| Accidentally committed a large or unwanted file | Remove it, add it to `.gitignore`, commit; ask before rewriting history. |
| Issue was created with wrong labels | Edit labels in the issue sidebar; the import script is not needed again. |

## Appendix A: Templates

### A.1 Issue template

Save as `.github/ISSUE_TEMPLATE/task.md`.

```markdown
---
name: Task
about: Implementation or documentation task
title: "SR-XXX "
labels: task
---

**Description**

What needs to be done and why.

**Acceptance criteria**

- [ ] Criterion 1
- [ ] Criterion 2

**Depends on**

None

**Notes**

Anything relevant for the reviewer.
```

### A.2 Pull request template

Save as `.github/pull_request_template.md`.

```markdown
## Summary

Short description of the change.

## Related issue

Closes #

## How to test

Steps to verify the change in the game.

## Checklist

- [ ] Acceptance criteria of the issue are met
- [ ] Classes and methods are documented, inline comments added
- [ ] No game logic in the main program
- [ ] Attributes are private, created in `__init__`, exposed with properties
- [ ] No unused methods, no repeated blocks that should be loops
- [ ] The game runs from `src/main.py`
```

### A.3 Bug report template

Save as `.github/ISSUE_TEMPLATE/bug.md`.

```markdown
---
name: Bug
about: Defect found while playing or reviewing
title: "BUG: "
labels: bug
---

**What happened**

**What should have happened**

**Steps to reproduce**

1. 
2. 

**Related issue**

SR-XXX
```
