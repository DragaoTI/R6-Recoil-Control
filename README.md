# Recoil Control User Guide | [PT VERSION HERE](https://github.com/DragaoTI/R6-Recoil-Control/blob/main/README.md)

This guide explains how to use the Recoil Control application to manage weapon recoil settings and agent presets.

https://github.com/user-attachments/assets/459f8606-34a4-4efe-a69f-15d24bfd72f1

## File Structure

Ensure that the `Agents` and `presets` folders are in the same directory as the main script `main.py`.

```
Recoil-Control/
├── main.py
├── recoil_controller.py
├── settings.cfg
├── Agents/
│   ├── attackers/
│   └── defenders/
└── presets/
    ├── <agent_name>/
    └── ...
```

## How to Start the Application

To start the application, run the `main.py` script:

```bash
python main.py
```

## Core Features

### Recoil Control

*   **Enable/Disable Recoil**: The main button on the interface (`Disabled`/`Enabled`) toggles recoil control.
    *   **Red**: Recoil disabled.
    *   **Green**: Recoil enabled.
    *   Button and hover colors change dynamically.
*   **Adjust Recoil Values**:
    *   Use the **sliders** to visually adjust vertical (Y) and horizontal (X) recoil values for both primary and secondary weapons.
    *   You can also **click and type** values directly into the input fields next to the sliders for greater precision. Press `Enter` after typing to apply the change.
*   **Active Weapon**: The application automatically switches between primary and secondary weapon recoil control based on configured hotkeys.

### Settings

Click the "Settings" button to open the settings window:

*   **Hotkeys**:
    *   **Primary Weapon Hotkey 1 & 2**: Set the keys or mouse buttons to switch to the primary weapon. Click "Record" and press the desired key/button.
    *   **Secondary Weapon Hotkey 1 & 2**: Set the keys or mouse buttons to switch to the secondary weapon. Click "Record" and press the desired key/button.
*   **Secondary Weapon Enabled**: Check or uncheck this box to enable or disable recoil control for the secondary weapon.
*   **Shoot Delay**: Adjusts the delay between recoil corrections.
*   **Sensitivity**: Adjusts the overall sensitivity of recoil control.
*   **Max Movement**: Defines the maximum allowed movement for recoil correction.

Settings are automatically saved to the `settings.cfg` file whenever you make a change.

### Preset Management

Click the "Presets" button to open the preset management window:

1.  **Agent Selection**: Choose between "Attackers" or "Defenders" to view the list of agents. Click an agent's icon to manage their presets.
2.  **Manage Presets for Selected Agent**:
    *   **Save Preset**: Enter a name in the "Preset Name" field and click "Save Preset" to save the current recoil settings (X and Y for both weapons, and if secondary weapon is enabled) as a new preset for the selected agent.
    *   **Load Preset**: Select an existing preset from the "Load Existing Preset" dropdown and click "Load Preset" to apply these settings. A confirmation will be requested.
    *   **Delete Preset**: Select an existing preset from the dropdown and click "Delete Preset" to remove it. A confirmation will be requested.

## Logging

The application logs information, warnings, and errors to a log file named `recoil_controller.log` in the same directory as the main script. This can be useful for debugging and understanding application behavior.

---
**Note**: This application is designed to assist with recoil control in games. Use it responsibly and in accordance with game terms of service. 
