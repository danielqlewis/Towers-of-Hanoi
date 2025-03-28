# Towers of Hanoi - Program Architecture Documentation

## 1. Components and Basic Structure

### Primary Components

**Model Components**:
- `menu_model` - Handles menu system and non-game states
- `game_model` - Manages game board state and game logic
- `button_entity` - Shared sub-model for interactive buttons

**View Components**:
- `assets` - Contains `AssetsContainer` class and factory function
- `renderer` - Houses `GameRenderer` for drawing to screen

**Controller Components**:
- `controller` - Manages active model and state transitions
- `program_loop` - Central coordinator and main game loop

**Utility Modules**:
- `asset_loader` - Finds file paths for loading image assets
- `validation` - Verifies required dependencies

**Entry Point**:
- `main` - Program entry point that validates dependencies and initializes `ProgramLoop`

### Component Hierarchy

```
main
├── validation
└── program_loop
    ├── controller
    │   ├── menu_model
    │   │   └── button_entity
    │   └── game_model
    │       └── button_entity
    └── renderer
        └── assets
            └── asset_loader
```

## 2. Overall Structure and Program Flow

### Initialization Process
The program begins in the `main` module, which first runs validation checks to ensure all dependencies are properly installed. After successful validation, `main` creates a single `ProgramLoop` instance that serves as the central coordinator for the entire application.

During initialization, the `ProgramLoop` sets up the core components of the system. It creates a single `menu_model` instance that will persist throughout the program's lifetime. This menu model is passed to a new `Controller` instance as its initial active model. The initialization process also creates an `AssetsContainer` instance using the factory function in the `assets` module, which in turn uses the `asset_loader` utility to locate all necessary image files. Finally, a `GameRenderer` instance is created and provided with the `AssetsContainer`.

### Game Loop Structure
Once initialized, the `ProgramLoop` manages the main game loop that drives the application. Each frame begins with checking for window exit events to determine if the program should terminate. The loop then processes user input, focusing on cursor location and click state, before passing this processed input to the `Controller`.

The `Controller` uses this input to update the active model, whether that's the menu model or a game model. After the model is updated, the `ProgramLoop` checks if any changes occurred that would require redrawing the screen. When changes are detected, it triggers a redraw operation through the `GameRenderer`, which uses the current state of the active model to determine what to display.

At the end of each frame, the loop checks for state transition requests from the `Controller`. When a transition is requested, the `ProgramLoop` handles the model switch appropriately. For transitions to the game state, it creates a new `game_model` instance based on the current difficulty setting. For transitions back to the menu, it simply switches to the existing persistent `menu_model` instance.

### State Transitions
State transitions are managed through the `Controller`'s `next_state` attribute, which is normally set to `None`. When a user action triggers a state change, this attribute is set to a valid state enum value, signaling to the `ProgramLoop` that a transition should occur.

The transition process differs depending on the destination state. When moving from the menu to the game, the system creates a new `game_model` instance configured according to the current difficulty setting in the menu model. This ensures that each new game starts with a fresh state. When returning from the game to the menu, the system simply switches back to the persistent `menu_model` instance, which maintains all user settings between game sessions.

### Visual Theme Handling
The program supports multiple visual themes that affect specific assets. When the user selects a new theme, the system creates a new immutable `AssetsContainer` instance rather than modifying the existing one. This immutability ensures that asset states remain consistent during rendering operations.

The factory function in the `assets` module handles the creation of new containers, using the `asset_loader` utility to find the appropriate themed assets in the directory structure. Once the new container is created, the `GameRenderer` is updated to use it for all subsequent rendering operations. This design allows theme changes to take effect immediately without requiring a restart of the application.

### Resolution Scaling
To support multiple screen resolutions while maintaining consistent gameplay, the program implements a virtual screen architecture. All rendering operations target a fixed-size virtual screen (960×640 pixels), regardless of the actual display resolution.

When it's time to present the frame to the user, the virtual screen is scaled to match the selected resolution. This approach simplifies the rendering logic by allowing the game to be designed for a single resolution while still supporting various display sizes. The scaling operation occurs only at the final stage of rendering, maintaining performance while providing flexibility.

## 3. Module Structure Details

### `main` Module

The `main` module serves as the entry point for the entire application, containing the minimal code necessary to initialize and launch the program. 

**Key Responsibilities:**
- Verifies that all system requirements and dependencies are met before starting
- Creates the primary `ProgramLoop` instance that drives the application
- Handles critical startup errors gracefully with appropriate exit codes
- Provides the standard Python entry point mechanism (`if __name__ == "__main__"`)

This module exemplifies the principle of separation of concerns, delegating detailed initialization to the `ProgramLoop` class and dependency checking to the `validation` utility. Its streamlined design ensures that the application startup process is clear and maintainable.

### `menu_model` Module

The `menu_model` module implements the persistent menu system of the application, maintaining both the menu state and all user-configurable settings. Unlike the game_model, a single menu_model instance exists throughout the program's lifetime, providing consistent access to user preferences.

**Key Responsibilities:**
- Manages the current menu state (main menu, options, tutorial, credits)
- Stores and provides access to user settings (theme, resolution, difficulty)
- Maintains temporary settings during options menu interaction
- Tracks button states and highlights for menu navigation
- Handles tutorial slide progression
- Provides methods for cycling through available setting options
- Manages the active set of buttons based on the current menu context

The module plays a dual role in the architecture:
1. As the model component for the menu system, following MVC principles
2. As a centralized settings repository that influences the entire application

The menu system has several states handled by this model:
- Main menu: Provides access to game start, options, tutorial, credits, and exit
- Options menu: Allows customization of theme, resolution, and difficulty
- Tutorial mode: Displays a series of instructional slides
- Credits screen: Shows acknowledgments and attributions

Settings modifications follow a two-step process where changes are first displayed for preview in the options menu, then committed only when the user accepts them. This approach allows users to experiment with different configurations before applying them, while maintaining the current settings if the user cancels.

The module is designed to be immutable from the perspective of other components - they read settings from it but any modifications must go through the controller, maintaining proper separation of concerns.

### `game_model` Module

The `game_model` module implements the core data structure and logic for the Towers of Hanoi puzzle. It encapsulates the game state and rules while remaining independent of the user interface and input handling, following the model component responsibilities in the MVC pattern.

**Key Responsibilities:**
- Maintains the state of the three towers and discs using a simple list-based representation
- Implements the rules of the Towers of Hanoi puzzle including move validation
- Tracks the currently selected tower during gameplay
- Manages game notifications for events like victory or illegal moves
- Provides methods for game state manipulation (moving discs, resetting the board)
- Handles button highlighting for game interface elements
- Determines when the puzzle is complete (victory condition)

The module represents the game state with elegant simplicity:
- The three towers are stored as a tuple of three lists
- Discs are represented as integers (smaller numbers represent larger discs)
- The first tower is initialized with discs in descending order (largest to smallest)

Each new game creates a fresh `GameModel` instance with the specified number of discs (default is 3), allowing for variable difficulty levels. The model focuses exclusively on maintaining valid game state, with all game rules being enforced through the `check_move_legal` method that ensures the fundamental rule of Towers of Hanoi: a larger disc cannot be placed on a smaller one.

The module is designed to be purely functional in its representation of game mechanics, with no dependencies on rendering or input processing. This separation of concerns allows the game logic to be tested and maintained independently of the user interface.

### `button_entity` Module

The `button_entity` module provides a simple but essential abstraction for interactive elements in both the menu and game interfaces. It defines the `ButtonEntity` class which encapsulates the concept of a clickable button.

**Key Responsibilities:**
- Represents buttons with position, size, and type information
- Stores predefined positions for all button types in the application
- Creates collision rectangles for detecting user interactions
- Provides a factory method for creating sets of buttons efficiently

The module maintains a dictionary of predefined button positions, ensuring consistent placement of UI elements throughout the application. Buttons come in two standard sizes: regular buttons for menu navigation and smaller buttons for in-game controls.

Each `ButtonEntity` instance contains just two attributes: a flag indicating the button type and a Pygame Rect for collision detection. This minimalist design allows the button entities to be used efficiently by both model types without unnecessary complexity.

The module exemplifies single-responsibility design by focusing exclusively on button positioning and identity, while leaving visual rendering to the view components and interaction handling to the controllers.

### `assets` Module

The `assets` module serves as the organizational backbone for all visual resources in the application. It implements a sophisticated container system using immutable dataclasses to ensure asset integrity and maintain clean separation between different types of visual elements.

**Key Responsibilities:**
- Defines a structured hierarchy of containers for organizing different asset types
- Implements the immutable `AssetsContainer` class as the primary asset repository
- Provides the `build_asset_container` factory function for creating asset containers
- Manages the loading of theme-specific assets (main menu, options menu, game board)
- Handles common assets shared across all themes (buttons, discs, indicators)
- Organizes assets by their functional purpose (backgrounds, buttons, discs, etc.)
- Ensures proper error handling during asset loading

The module employs a nested dataclass structure to organize assets by type:
- `BackgroundContainer` for main screens and game board
- `ButtonContainer` for standard and highlighted button states
- `DiscContainer` for standard and highlighted disc states
- `SettingIndicatorContainer` for visualizing user settings
- `GameNotificationContainer` for in-game messages
- `TutorialSlidesContainer` for educational content

The asset loading process is separated into theme-specific and common assets, with the theme-specific assets (backgrounds) varying based on the user's selected theme. All containers are created as immutable objects (`frozen=True`), ensuring they cannot be modified after creation - when theme changes occur, entirely new containers are created rather than modifying existing ones.

The module works closely with the `asset_loader` utility module, which handles the low-level file operations. The `assets` module focuses on the organizational structure and creation of properly configured asset containers, while delegating the actual file loading to specialized utility functions.

### `renderer` Module

The `renderer` module implements the visual presentation layer for the entire application through its `GameRenderer` class. This module translates the abstract data in the models into concrete visual elements on the screen, following the view component responsibilities in the MVC pattern.

**Key Responsibilities:**
- Renders both the menu system and game board to the screen
- Handles the visual representation of all UI elements (backgrounds, buttons, discs)
- Manages positional constants for consistent element placement
- Draws highlighted elements to provide visual feedback for user interactions
- Displays game notifications (victory, illegal moves)
- Visualizes the current state of settings in the options menu
- Renders tutorial slides sequentially

The renderer is designed to be completely decoupled from input processing and game logic. It receives an immutable `AssetsContainer` with all visual resources and uses it to draw the current state of whichever model is active. When the visual theme changes, the renderer receives a completely new `AssetsContainer` rather than modifying the existing one.

The module provides two primary rendering methods:
- `render_menu()`: Handles all menu states (main menu, options, tutorial, credits)
- `render_game()`: Visualizes the game board, discs, and game-specific notifications

For drawing game elements, the renderer uses carefully calculated positioning based on class constants. The Towers of Hanoi board is drawn with precise positioning for each disc, with the size of discs represented visually based on their numerical value in the model. When a tower or disc is selected, it's highlighted to provide visual feedback to the user.

The module demonstrates a clean separation of concerns, focusing exclusively on visualization without any knowledge of how user input is processed or how the game logic works.

### `controller` Module

The `controller` module houses the `ProgramController` class, which serves as the intermediary between user input and model state changes, implementing the controller component of the MVC architecture. This module translates raw user interactions into meaningful game actions and state transitions.

**Key Responsibilities:**
- Processes interpreted user input from the `program_loop`
- Updates the currently active model (menu or game) based on input
- Maintains state transition information via the `next_state` attribute
- Handles button interactions for both menu and game states
- Implements game logic for tower selection and disc movement
- Manages game notifications (victory, illegal moves)
- Tracks settings changes that require updates to assets or display

The controller maintains several flags to coordinate with the `program_loop`:
- `model_updated`: Signals when the model has changed and needs rerendering
- `next_state`: Indicates a requested transition between menu and game states
- `exit_flag`: Signals when the program should terminate
- `asset_package_updated`: Indicates when the visual theme has changed
- `resolution_updated`: Indicates when the screen resolution has changed

The module employs a strategy pattern using a dictionary of button handlers to map button types to specific actions, providing a clean way to handle the various button interactions in the menu system. For game board interactions, it translates user clicks into appropriate calls to the game_model's methods, coordinating tower selection and invoking the model's move validation and game state checking functionality without implementing the actual game logic itself.

The controller is designed to be stateless regarding the specific model it controls, allowing it to seamlessly transition between different model types (menu or game) while maintaining consistent behavior patterns.

### `program_loop` Module

The `program_loop` module serves as the central coordinator for the entire application, providing the main execution loop and orchestrating all other components. It contains the `ProgramLoop` class which initializes the program, manages state transitions, processes input, and coordinates rendering.

**Key Responsibilities:**
- Initializes Pygame and creates the virtual screen architecture
- Maintains the main game loop that drives the entire application
- Processes and translates user input between the physical and virtual screen
- Mediates communication between Controller and Renderer
- Handles program state transitions (menu to game and back)
- Manages settings changes that affect the display or assets
- Ensures proper cleanup when the program exits

The class uses a virtual screen system for resolution independence, where all game elements are rendered to a fixed-size virtual screen (960×640), which is then scaled to match the user's selected resolution. This allows the game to maintain consistent proportions across different display sizes.

During initialization, the `ProgramLoop` creates persistent instances of core components:
- A single `MenuModel` that persists throughout the program's lifetime
- The `GameRenderer` that handles all drawing operations
- The `ProgramController` that processes input and updates models

New `GameModel` instances are created dynamically whenever the user transitions from the menu to the game state, with the configuration determined by the current settings in the `MenuModel`.

The module effectively decouples the game's internal logic from its presentation and input handling, maintaining a clean MVC architecture throughout.

### `asset_loader` Utility Module

The `asset_loader` module provides low-level utility functions for loading image resources from the file system. It abstracts away the details of file paths and image loading, allowing the rest of the application to work with relative paths rather than absolute ones.

**Key Responsibilities:**
- Converts relative asset paths to absolute file system paths
- Handles image loading with appropriate Pygame conversion methods
- Provides separate functions for standard images and those requiring alpha channel support
- Implements error checking for missing asset files

This module creates a clean separation between the logical organization of assets in the code and their physical location in the file system. By centralizing path management, it ensures that asset loading remains consistent throughout the application while making the codebase more portable across different development environments.

### `validation` Utility Module

The `validation` module provides comprehensive system verification to ensure the application has all required dependencies and assets before execution begins. It implements a thorough preflight check system that prevents runtime errors due to missing components.

**Key Responsibilities:**
- Verifies that required Python dependencies (primarily Pygame) are installed
- Checks for the existence and proper structure of the Assets directory
- Validates theme folders and their contents
- Ensures all required image assets are present and properly named
- Provides detailed logging of any missing components
- Delivers a simple success/failure result with appropriate messaging

The module uses a layered verification approach, checking dependencies first, then validating the overall asset structure, theme folders, and finally individual image files. This hierarchical verification prevents cryptic runtime errors by ensuring all required resources exist before the application starts.

By centralizing validation logic, the module simplifies the main program entry point and creates a single source of truth for what constitutes a valid program environment.
