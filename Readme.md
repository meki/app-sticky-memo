# App Sticky Memo

> 📖 **日本語版** | [Japanese Documentation](docs/Readme.ja.md)

A Windows-exclusive application that allows you to save notes for each application.
When you switch between applications, the relevant notes for that application are automatically displayed.
Notes are saved per application, making it easy to view different notes by simply switching applications.
This makes it easy to check notes for rarely used applications just by switching to them.

## Features

- **Per-Application Note Storage**: Automatically creates independent memo files for each application (exe name)
- **Automatic Switching**: Automatically switches to relevant notes when switching applications
- **Settings Configuration**: Customizable data save directory
- **Window Position Memory**: Saves window position and size on exit, restores on next startup
- **Always on Top**: Checkbox to keep the application window always on top
- **Markdown Support**: Memo files are saved in Markdown format, supporting headers, lists, links, etc.
- **Auto-Save**: Note contents are automatically saved, no manual saving required
- **Multi-language Support**: UI text is externalized to files, making future language additions easy

## Installation

1. Download the latest release from the Release page
2. Extract the downloaded ZIP file
3. Run `AppStickyMemo.exe` from the extracted folder

## Usage

1. **App Startup**: When the app starts, it detects the currently active application and automatically creates the corresponding memo file
2. **Settings**: Open the settings panel via the gear button in the top right to change the memo file save directory
3. **App Switching**: When switching to another application, the memo file related to that app is automatically created
4. **Window Size**: Window size and position changes are automatically saved on app exit and restored on next startup
5. **Always on Top**: Use the "Pin to Front" checkbox in the header to keep the app always visible

## About Memo Files

- Memo files are saved in the format `[AppName].md`
- Files are in Markdown format, so they can be directly edited with text editors
- Default save location: `C:\Users\[Username]\Documents\StickyMemos\`

## Development

### Requirements

- Python 3.11+
- uv package manager

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd app-sticky-memo

# Install dependencies
uv sync

# Run the application
uv run python app.py
```

### Code Quality

The project uses pre-commit hooks for code quality:

```bash
# Run all quality checks
uv run pre-commit run --all-files
```

### Project Structure

```
app-sticky-memo/
├── app.py                 # Main application entry point
├── src/
│   ├── components/        # UI components
│   │   ├── header.py      # Header with title and controls
│   │   ├── memo_editor.py # Memo editor with auto-save
│   │   ├── app_display.py # Current app name display
│   │   └── settings_panel.py # Settings configuration panel
│   ├── core/              # Core business logic
│   │   ├── foreground_monitor.py # Tracks foreground apps
│   │   ├── memo_manager.py # Manages per-app memo files
│   │   └── settings_manager.py # Handles app settings
│   └── locales/           # Internationalization
│       ├── i18n.py        # I18n manager
│       └── ja.yaml        # Japanese translations
├── docs/
│   └── Readme.ja.md       # Japanese documentation
└── pyproject.toml         # Project configuration
```

## Architecture

The application follows a modular architecture:

- **UI Components**: Separate classes for each UI element with clear responsibilities
- **Core Logic**: Business logic separated from UI concerns
- **Settings Management**: Persistent configuration with JSON storage
- **Memo Management**: Per-application file handling with auto-save
- **Foreground Monitoring**: Background service to track active applications
- **Internationalization**: YAML-based translation system

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run code quality checks: `uv run pre-commit run --all-files`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
