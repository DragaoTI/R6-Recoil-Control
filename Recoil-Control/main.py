import sys
import os
import json
import logging
from typing import Optional

script_dir = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "RecoilControl")
else:
    CONFIG_DIR = script_dir

os.makedirs(CONFIG_DIR, exist_ok=True)

import customtkinter
import tkinter as tk
from CTkMessagebox import CTkMessagebox

from pynput import keyboard, mouse
from pynput.mouse import Button
from PIL import Image

try:
    from recoil_controller import RecoilController
except ImportError:
    logging.error("Module 'recoil_controller' not found.")
    sys.exit(1)


class SettingsDialog(customtkinter.CTkToplevel):
    def __init__(self, recoil_controller, main_app_instance, parent=None):
        super().__init__(parent)
        self.title("Settings")
        self.recoil_controller = recoil_controller
        self.main_app_instance = main_app_instance
        self.geometry("400x510")
        self.init_ui()

    def init_ui(self):
        main_frame = customtkinter.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        customtkinter.CTkLabel(main_frame, text="Shoot Delay (s):").grid(row=0, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.shoot_delay_spinbox = customtkinter.CTkEntry(main_frame)
        self.shoot_delay_spinbox.insert(0, str(self.recoil_controller.settings.shoot_delay))
        self.shoot_delay_spinbox.grid(row=0, column=1, sticky="ew", padx=(5,1), pady=(10,2))
        self.shoot_delay_spinbox.bind("<Return>", self.update_settings_event)
        self.shoot_delay_spinbox.bind("<FocusOut>", self.update_settings_event)

        customtkinter.CTkLabel(main_frame, text="Max Shots:").grid(row=1, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.max_shots_spinbox = customtkinter.CTkEntry(main_frame)
        self.max_shots_spinbox.insert(0, str(self.recoil_controller.settings.max_shots))
        self.max_shots_spinbox.grid(row=1, column=1, sticky="ew", padx=(1,0), pady=(10,2))
        self.max_shots_spinbox.bind("<Return>", self.update_settings_event)
        self.max_shots_spinbox.bind("<FocusOut>", self.update_settings_event)

        customtkinter.CTkLabel(main_frame, text="Smoothing Factor:").grid(row=2, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.smoothing_factor_spinbox = customtkinter.CTkEntry(main_frame)
        self.smoothing_factor_spinbox.insert(0, str(self.recoil_controller.settings.smoothing_factor))
        self.smoothing_factor_spinbox.grid(row=2, column=1, sticky="ew", padx=(5,8), pady=(10,2))
        self.smoothing_factor_spinbox.bind("<Return>", self.update_settings_event)
        self.smoothing_factor_spinbox.bind("<FocusOut>", self.update_settings_event)

        customtkinter.CTkLabel(main_frame, text="Sensitivity:").grid(row=3, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.sensitivity_spinbox = customtkinter.CTkEntry(main_frame)
        self.sensitivity_spinbox.insert(0, str(self.recoil_controller.settings.sensitivity))
        self.sensitivity_spinbox.grid(row=3, column=1, sticky="ew", padx=(5,8), pady=(10,2))
        self.sensitivity_spinbox.bind("<Return>", self.update_settings_event)
        self.sensitivity_spinbox.bind("<FocusOut>", self.update_settings_event)

        customtkinter.CTkLabel(main_frame, text="Max Movement:").grid(row=4, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.max_movement_spinbox = customtkinter.CTkEntry(main_frame)
        self.max_movement_spinbox.insert(0, str(self.recoil_controller.settings.max_movement))
        self.max_movement_spinbox.grid(row=4, column=1, sticky="ew", padx=(5,4), pady=(10,2))
        self.max_movement_spinbox.bind("<Return>", self.update_settings_event)
        self.max_movement_spinbox.bind("<FocusOut>", self.update_settings_event)

        customtkinter.CTkLabel(main_frame, text="Timeout (s):").grid(row=5, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.timeout_spinbox = customtkinter.CTkEntry(main_frame)
        self.timeout_spinbox.insert(0, str(self.recoil_controller.settings.timeout))
        self.timeout_spinbox.grid(row=5, column=1, sticky="ew", padx=(5,10), pady=(10,2))
        self.timeout_spinbox.bind("<Return>", self.update_settings_event)
        self.timeout_spinbox.bind("<FocusOut>", self.update_settings_event)

        self.hotkey_capture_mode = False
        self.current_hotkey_field = None

        row_offset = 6

        customtkinter.CTkLabel(main_frame, text="Primary Weapon Hotkey 1:").grid(row=row_offset, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.primary_hotkey_input = customtkinter.CTkEntry(main_frame, state="readonly")
        self.primary_hotkey_input.grid(row=row_offset, column=1, sticky="ew", padx=(5,5), pady=(10,2))
        customtkinter.CTkButton(main_frame, text="Record", command=lambda: self.start_hotkey_capture(self.primary_hotkey_input, "primary_weapon_hotkey")).grid(row=row_offset, column=2, padx=(5,10), pady=(10,2))
        self.primary_hotkey_input.configure(state="normal")
        self.primary_hotkey_input.delete(0, tk.END)
        self.primary_hotkey_input.insert(0, ", ".join(self.recoil_controller.settings.primary_weapon_hotkey))
        self.primary_hotkey_input.configure(state="readonly")
        row_offset += 1

        customtkinter.CTkLabel(main_frame, text="Primary Weapon Hotkey 2:").grid(row=row_offset, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.primary_hotkey_2_input = customtkinter.CTkEntry(main_frame, state="readonly")
        self.primary_hotkey_2_input.grid(row=row_offset, column=1, sticky="ew", padx=(5,5), pady=(10,2))
        customtkinter.CTkButton(main_frame, text="Record", command=lambda: self.start_hotkey_capture(self.primary_hotkey_2_input, "primary_weapon_hotkey_2")).grid(row=row_offset, column=2, padx=(5,10), pady=(10,2))
        self.primary_hotkey_2_input.configure(state="normal")
        self.primary_hotkey_2_input.delete(0, tk.END)
        self.primary_hotkey_2_input.insert(0, ", ".join(self.recoil_controller.settings.primary_weapon_hotkey_2))
        self.primary_hotkey_2_input.configure(state="readonly")
        row_offset += 1

        customtkinter.CTkLabel(main_frame, text="Secondary Weapon Hotkey 1:").grid(row=row_offset, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.secondary_hotkey_input = customtkinter.CTkEntry(main_frame, state="readonly")
        self.secondary_hotkey_input.grid(row=row_offset, column=1, sticky="ew", padx=(5,5), pady=(10,2))
        customtkinter.CTkButton(main_frame, text="Record", command=lambda: self.start_hotkey_capture(self.secondary_hotkey_input, "secondary_weapon_hotkey")).grid(row=row_offset, column=2, padx=(5,10), pady=(10,2))
        self.secondary_hotkey_input.configure(state="normal")
        self.secondary_hotkey_input.delete(0, tk.END)
        self.secondary_hotkey_input.insert(0, ", ".join(self.recoil_controller.settings.secondary_weapon_hotkey))
        self.secondary_hotkey_input.configure(state="readonly")
        row_offset += 1

        customtkinter.CTkLabel(main_frame, text="Secondary Weapon Hotkey 2:").grid(row=row_offset, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.secondary_hotkey_2_input = customtkinter.CTkEntry(main_frame, state="readonly")
        self.secondary_hotkey_2_input.grid(row=row_offset, column=1, sticky="ew", padx=(5,5), pady=(10,2))
        customtkinter.CTkButton(main_frame, text="Record", command=lambda: self.start_hotkey_capture(self.secondary_hotkey_2_input, "secondary_weapon_hotkey_2")).grid(row=row_offset, column=2, padx=(5,10), pady=(10,2))
        self.secondary_hotkey_2_input.configure(state="normal")
        self.secondary_hotkey_2_input.delete(0, tk.END)
        self.secondary_hotkey_2_input.insert(0, ", ".join(self.recoil_controller.settings.secondary_weapon_hotkey_2))
        self.secondary_hotkey_2_input.configure(state="readonly")
        row_offset += 1

        main_frame.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(main_frame, text="Created by K1ngPT-X").grid(row=row_offset + 1, column=0, columnspan=3, pady=(20, 2), sticky="ew")
        customtkinter.CTkLabel(main_frame, text="App Version: 1.0.0").grid(row=row_offset + 2, column=0, columnspan=3, pady=(2, 10), sticky="ew")

    def start_hotkey_capture(self, input_field, setting_key):
        self.current_hotkey_field = input_field
        self.setting_key_to_update = setting_key
        self.hotkey_capture_mode = True
        
        if self.current_hotkey_field is not None:
            self.current_hotkey_field.configure(state="normal")
            self.current_hotkey_field.delete(0, tk.END)
            self.current_hotkey_field.insert(0, "Press a key or mouse button...")
            self.current_hotkey_field.configure(state="readonly")

    def stop_hotkey_capture(self, hotkey_string):
        if self.hotkey_capture_mode:
            self.hotkey_capture_mode = False
            if self.current_hotkey_field is not None:
                self.current_hotkey_field.configure(state="normal")
                self.current_hotkey_field.delete(0, tk.END)
                self.current_hotkey_field.insert(0, hotkey_string)
                self.current_hotkey_field.configure(state="readonly")
            
            current_hotkeys = getattr(self.recoil_controller.settings, self.setting_key_to_update)
            if current_hotkeys and len(current_hotkeys) > 0:
                current_hotkeys[0] = hotkey_string
            else:
                setattr(self.recoil_controller.settings, self.setting_key_to_update, [hotkey_string])

        if self.setting_key_to_update in ["primary_weapon_hotkey", "secondary_weapon_hotkey", "primary_weapon_hotkey_2", "secondary_weapon_hotkey_2"]:
            self.main_app_instance.update_main_ui_recoil_values()
            self.main_app_instance.save_settings()
        print(f"[DEBUG] Hotkey capture for {self.setting_key_to_update} finished with: {hotkey_string}")

    def process_captured_key(self, key_or_mouse_hotkey_string):
        if hasattr(key_or_mouse_hotkey_string, 'char') or str(key_or_mouse_hotkey_string).startswith('Key.'):
            hotkey_string = self.main_app_instance._get_key_string(key_or_mouse_hotkey_string)
        else:
            hotkey_string = key_or_mouse_hotkey_string
            
        if hotkey_string:
            self.stop_hotkey_capture(hotkey_string)
            print(f"[DEBUG] Hotkey captured in dialog: {hotkey_string}")

    def update_settings_event(self, event=None):
        self.update_settings()
        self.main_app_instance.update_main_ui_recoil_values()
        self.main_app_instance.save_settings()

    def update_settings(self):
        try:
            self.recoil_controller.settings.shoot_delay = float(self.shoot_delay_spinbox.get())
            self.recoil_controller.settings.max_shots = int(self.max_shots_spinbox.get())
            self.recoil_controller.settings.smoothing_factor = float(self.smoothing_factor_spinbox.get())
            self.recoil_controller.settings.sensitivity = float(self.sensitivity_spinbox.get())
            self.recoil_controller.settings.max_movement = int(self.max_movement_spinbox.get())
            self.recoil_controller.settings.timeout = int(self.timeout_spinbox.get())
        except ValueError:
            logging.error("Invalid input values for settings. Please enter valid numbers.")


class PresetsDialog(customtkinter.CTkToplevel):
    def __init__(self, recoil_controller, main_app_instance, parent=None):
        super().__init__(parent)
        self.title("Agent Presets")
        self.recoil_controller = recoil_controller
        self.main_app_instance = main_app_instance
        self.geometry("800x600")
        self.init_ui()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.attackers_frame = self.tabview.add("Attackers")
        self.defenders_frame = self.tabview.add("Defenders")

        self.attackers_frame.grid_columnconfigure(0, weight=1)
        self.defenders_frame.grid_columnconfigure(0, weight=1)

        self.load_agents("attackers", self.attackers_frame)
        self.load_agents("defenders", self.defenders_frame)

    def load_agents(self, agent_type, parent_frame):
        agents_grid_frame = customtkinter.CTkScrollableFrame(parent_frame)
        agents_grid_frame.pack(fill="both", expand=True)

        base_path = os.path.join(script_dir, "Agents")
        agent_path = os.path.join(base_path, agent_type)

        if not os.path.exists(agent_path):
            print(f"Directory not found: {agent_path}")
            return

        if agent_type == "attackers":
            agents = [
                "Striker", "Sledge", "Thatcher", "Ash", "Thermite", "Twitch",
                "Montagne", "Glaz", "Fuze", "Blitz", "IQ", "Buck",
                "Blackbeard", "Capitao", "Hibana", "Jackal", "Ying", "Zofia",
                "Dokkaebi", "Finka", "Lion", "Maverick", "Nomad", "Gridlock",
                "Nokk", "Amaru", "Kali", "Iana", "Ace", "Zero",
                "Flores", "Osa", "Sens", "Grim", "Brava", "Ram",
                "Deimos", "Rauora"
            ]
        elif agent_type == "defenders":
            agents = [
                "Sentry", "Smoke", "Mute", "Castle", "Pulse", "Doc",
                "Rook", "Kapkan", "Tachanka", "Jager", "Bandit", "Frost",
                "Valkyrie", "Caveira", "Echo", "Mira", "Lesion", "Ela",
                "Vigil", "Maestro", "Alibi", "Clash", "Kaid", "Mozzie",
                "Warden", "Goyo", "Wamai", "Oryx", "Melusi", "Aruni",
                "Thunderbird", "Thorn", "Azami", "Solis", "Fenrir",
                "Tubarao", "Skopos"
            ]
        else:
            agents = []

        row = 0
        col = 0
        for agent_name in agents:
            icon_path = os.path.join(agent_path, f"{agent_name.lower()}.png")
            if os.path.exists(icon_path):
                try:
                    img = Image.open(icon_path)
                    icon = customtkinter.CTkImage(light_image=img, dark_image=img, size=(64, 64))
                    
                    button = customtkinter.CTkButton(
                        agents_grid_frame,
                        image=icon,
                        text=agent_name,
                        compound="top",
                        command=lambda name=agent_name: self.select_agent(name)
                    )
                    button.grid(row=row, column=col, padx=5, pady=5)
                    col += 1
                    if col > 5:
                        col = 0
                        row += 1
                except Exception as e:
                    print(f"Error loading icon or creating button for {agent_name}: {e}")
            else:
                print(f"Icon not found for {agent_name} at {icon_path}")

        agents_grid_frame.grid_columnconfigure(tuple(range(6)), weight=1)

    def select_agent(self, agent_name):
        print(f"Agent selected: {agent_name}")
        self.agent_preset_dialog = AgentPresetDialog(agent_name, self.recoil_controller, self.main_app_instance)
        self.agent_preset_dialog.grab_set()
        self.agent_preset_dialog.wait_window()


class AgentPresetDialog(customtkinter.CTkToplevel):
    def __init__(self, agent_name, recoil_controller, main_app_instance, parent=None):
        super().__init__(parent)
        self.agent_name = agent_name
        self.recoil_controller = recoil_controller
        self.main_app_instance = main_app_instance
        self.title(f"Manage Presets for {self.agent_name}")
        self.geometry("400x250")
        self.init_ui()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = customtkinter.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        main_frame.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(main_frame, text="Preset Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.preset_name_input = customtkinter.CTkEntry(main_frame, placeholder_text="Preset Name to Save")
        self.preset_name_input.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        customtkinter.CTkLabel(main_frame, text="Load Existing Preset:").grid(row=1, column=0, sticky="w", pady=5)
        self.preset_combo_box = customtkinter.CTkOptionMenu(main_frame, values=["No preset found"], command=self.on_preset_selected)
        self.preset_combo_box.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        button_frame = customtkinter.CTkFrame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        button_frame.grid_columnconfigure((0,1,2), weight=1)

        self.load_button = customtkinter.CTkButton(button_frame, text="Load Preset", command=self.load_preset)
        self.load_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.save_button = customtkinter.CTkButton(button_frame, text="Save Preset", command=self.save_preset)
        self.save_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.delete_button = customtkinter.CTkButton(button_frame, text="Delete Preset", command=self.delete_preset)
        self.delete_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.populate_presets_combobox()

    def on_preset_selected(self, choice):
        print(f"Preset selected in combobox: {choice}")


    def populate_presets_combobox(self):
        agent_presets_dir = os.path.join(script_dir, "presets", self.agent_name.lower().replace(" ", "_"))
        presets = []
        if os.path.exists(agent_presets_dir):
            for filename in os.listdir(agent_presets_dir):
                if filename.endswith(".json"):
                    preset_name = os.path.splitext(filename)[0]
                    presets.append(preset_name)
        
        if presets:
            self.preset_combo_box.configure(values=presets)
            self.preset_combo_box.set(presets[0])
            self.load_button.configure(state="normal")
            self.delete_button.configure(state="normal")
        else:
            self.preset_combo_box.configure(values=["No preset found"])
            self.preset_combo_box.set("No preset found")
            self.load_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

    def load_preset(self):
        selected_preset = self.preset_combo_box.get()
        if selected_preset == "No preset found" or not selected_preset:
            msg = CTkMessagebox(title="Warning", message="Please select a preset to load.", icon="warning")
            msg.get()
            return

        msg = CTkMessagebox(title="Confirm Load Preset",
                            message=f"Are you sure you want to load the preset '{selected_preset}'?\nThis will overwrite current settings.",
                            option_1="No", option_2="Yes", icon="question")
        response = msg.get()
        if response != "Yes":
            return

        agent_presets_dir = os.path.join(script_dir, "presets", self.agent_name.lower().replace(" ", "_"))
        preset_file_path = os.path.join(agent_presets_dir, f"{selected_preset}.json")

        if not os.path.exists(preset_file_path):
            msg = CTkMessagebox(title="Error", message=f"Preset file not found: {preset_file_path}", icon="cancel")
            msg.get()
            return

        try:
            with open(preset_file_path, 'r') as f:
                loaded_settings = json.load(f)
            
            self.recoil_controller.settings.primary_recoil_y = loaded_settings.get("primary_recoil_y", 0.0)
            self.recoil_controller.settings.primary_recoil_x = loaded_settings.get("primary_recoil_x", 0.0)
            self.recoil_controller.settings.secondary_recoil_y = loaded_settings.get("secondary_recoil_y", 0.0)
            self.recoil_controller.settings.secondary_recoil_x = loaded_settings.get("secondary_recoil_x", 0.0)
            self.recoil_controller.settings.secondary_weapon_enabled = loaded_settings.get("secondary_weapon_enabled", False)

            self.main_app_instance.update_main_ui_recoil_values()
            msg = CTkMessagebox(title="Success", message=f"Preset '{selected_preset}' loaded successfully for {self.agent_name}!", icon="info")
            msg.get()
            self.destroy()
        except Exception as e:
            msg = CTkMessagebox(title="Error", message=f"Error loading preset: {e}", icon="cancel")
            msg.get()

    def save_preset(self):
        preset_name = self.preset_name_input.get().strip()
        if not preset_name:
            msg = CTkMessagebox(title="Error", message="Please enter a name for the preset.", icon="warning")
            msg.get()
            return

        agent_presets_dir = os.path.join(script_dir, "presets", self.agent_name.lower().replace(" ", "_"))
        os.makedirs(agent_presets_dir, exist_ok=True)

        preset_file_path = os.path.join(agent_presets_dir, f"{preset_name}.json")

        settings_to_save = {
            "primary_recoil_y": self.recoil_controller.settings.primary_recoil_y,
            "primary_recoil_x": self.recoil_controller.settings.primary_recoil_x,
            "secondary_recoil_y": self.recoil_controller.settings.secondary_recoil_y,
            "secondary_recoil_x": self.recoil_controller.settings.secondary_recoil_x,
            "secondary_weapon_enabled": self.recoil_controller.settings.secondary_weapon_enabled
        }

        try:
            with open(preset_file_path, 'w') as f:
                json.dump(settings_to_save, f, indent=4)
            msg = CTkMessagebox(title="Success", message=f"Preset '{preset_name}' saved for {self.agent_name}!", icon="info")
            msg.get()
            self.populate_presets_combobox()
        except Exception as e:
            msg = CTkMessagebox(title="Error", message=f"Error saving preset: {e}", icon="cancel")
            msg.get()
        
        print(f"Saving preset '{preset_name}' for {self.agent_name}")

    def delete_preset(self):
        selected_preset = self.preset_combo_box.get()
        if selected_preset == "No preset found" or not selected_preset:
            msg = CTkMessagebox(title="Warning", message="Please select a preset to delete.", icon="warning")
            msg.get()
            return

        msg = CTkMessagebox(title="Confirm Delete Preset",
                            message=f"Are you sure you want to delete the preset '{selected_preset}'?",
                            option_1="No", option_2="Yes", icon="question")
        response = msg.get()
        if response != "Yes":
            return

        agent_presets_dir = os.path.join(script_dir, "presets", self.agent_name.lower().replace(" ", "_"))
        preset_file_path = os.path.join(agent_presets_dir, f"{selected_preset}.json")

        try:
            if os.path.exists(preset_file_path):
                os.remove(preset_file_path)
                msg = CTkMessagebox(title="Success", message=f"Preset '{selected_preset}' deleted successfully!", icon="info")
                msg.get()
                self.populate_presets_combobox()
            else:
                msg = CTkMessagebox(title="Error", message=f"Preset file not found: {preset_file_path}", icon="cancel")
                msg.get()
        except Exception as e:
            msg = CTkMessagebox(title="Error", message=f"Error deleting preset: {e}", icon="cancel")
            msg.get()


class AboutDialog(customtkinter.CTkToplevel):
    def __init__(self, parent=None, recoil_controller=None):
        super().__init__(parent)
        self.parent = parent
        self.recoil_controller = recoil_controller
        self.title("About")
        self.geometry("380x150")
        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 380
        window_height = 200

        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.grab_set()
        self.focus_set()
        self.transient(parent)

        main_frame = customtkinter.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        customtkinter.CTkLabel(main_frame, text="Created by K1ngPT-X").pack(pady=5)
        customtkinter.CTkLabel(main_frame, text="GitHub: https://github.com/K1ngPT-X/R6-Recoil-Control").pack(pady=5)
        customtkinter.CTkLabel(main_frame, text="App Version: 1.0.0").pack(pady=5)

        button_checkbox_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_checkbox_frame.pack(pady=10)
        button_checkbox_frame.grid_columnconfigure(0, weight=2)
        button_checkbox_frame.grid_columnconfigure(1, weight=1)

        continue_button = customtkinter.CTkButton(button_checkbox_frame, text="Continue", command=self.destroy)
        continue_button.grid(row=0, column=0, padx=(0, 5), sticky="e")

        self.do_not_show_again_checkbox = customtkinter.CTkCheckBox(button_checkbox_frame, text="Do not show again", command=self.toggle_show_on_startup)
        if self.recoil_controller and not self.recoil_controller.settings.show_about_on_startup:
            self.do_not_show_again_checkbox.select()
        else:
            self.do_not_show_again_checkbox.deselect()
        self.do_not_show_again_checkbox.grid(row=0, column=1, padx=(5,0), sticky="w")

    def toggle_show_on_startup(self):
        if self.recoil_controller:
            self.recoil_controller.settings.show_about_on_startup = not self.do_not_show_again_checkbox.get()
            if self.parent:
                self.parent.save_settings()


class RecoilControllerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.recoil_controller = RecoilController()
        self.load_settings()

        if self.recoil_controller.settings.show_about_on_startup:
            self.about_dialog = AboutDialog(self, recoil_controller=self.recoil_controller)
            self.about_dialog.wait_window()

        self.title("Recoil Control")
        self.geometry("500x660")
        self.iconbitmap(os.path.join(script_dir, "icon.ico"))

        self.overrideredirect(False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        content_frame = customtkinter.CTkFrame(self)
        content_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        content_frame.grid_columnconfigure(0, weight=1)

        primary_weapon_group_box = customtkinter.CTkFrame(content_frame, border_width=2, corner_radius=10)
        primary_weapon_group_box.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        primary_weapon_group_box.grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(primary_weapon_group_box, text="Primary Weapon Recoil", font=customtkinter.CTkFont(weight="bold")).grid(row=0, column=0, pady=(5,0))

        customtkinter.CTkLabel(primary_weapon_group_box, text="Vertical Recoil (Y):").grid(row=1, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.primary_recoil_y_entry = customtkinter.CTkEntry(primary_weapon_group_box, width=50)
        self.primary_recoil_y_entry.grid(row=2, column=0, sticky="w", padx=10, pady=(0,5))
        self.primary_recoil_y_entry.bind("<Return>", self._update_primary_recoil_y_from_entry)
        self.primary_recoil_y_slider = customtkinter.CTkSlider(primary_weapon_group_box, from_=0, to=2000, number_of_steps=2000, command=self._update_primary_recoil_y_from_slider_scaled)
        self.primary_recoil_y_slider.set(0)
        self.primary_recoil_y_slider.grid(row=3, column=0, sticky="ew", padx=10, pady=(2,10))

        customtkinter.CTkLabel(primary_weapon_group_box, text="Horizontal Recoil (X):").grid(row=4, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.primary_recoil_x_entry = customtkinter.CTkEntry(primary_weapon_group_box, width=50)
        self.primary_recoil_x_entry.grid(row=5, column=0, sticky="w", padx=10, pady=(0,2))
        self.primary_recoil_x_entry.bind("<Return>", self._update_primary_recoil_x_from_entry)
        self.primary_recoil_x_slider = customtkinter.CTkSlider(primary_weapon_group_box, from_=-5000, to=5000, number_of_steps=10000, command=self._update_primary_recoil_x_from_slider_scaled)
        self.primary_recoil_x_slider.set(0)
        self.primary_recoil_x_slider.grid(row=6, column=0, sticky="ew", padx=10, pady=(2,10))

        secondary_weapon_group_box = customtkinter.CTkFrame(content_frame, border_width=2, corner_radius=10)
        secondary_weapon_group_box.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        secondary_weapon_group_box.grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(secondary_weapon_group_box, text="Secondary Weapon Recoil", font=customtkinter.CTkFont(weight="bold")).grid(row=0, column=0, pady=(5,0))

        customtkinter.CTkLabel(secondary_weapon_group_box, text="Vertical Recoil (Y):").grid(row=1, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.secondary_recoil_y_entry = customtkinter.CTkEntry(secondary_weapon_group_box, width=50)
        self.secondary_recoil_y_entry.grid(row=2, column=0, sticky="w", padx=10, pady=(0,5))
        self.secondary_recoil_y_entry.bind("<Return>", self._update_secondary_recoil_y_from_entry)
        self.secondary_recoil_y_slider = customtkinter.CTkSlider(secondary_weapon_group_box, from_=0, to=2000, number_of_steps=2000, command=self._update_secondary_recoil_y_from_slider_scaled)
        self.secondary_recoil_y_slider.set(0)
        self.secondary_recoil_y_slider.grid(row=3, column=0, sticky="ew", padx=10, pady=(2,10))

        customtkinter.CTkLabel(secondary_weapon_group_box, text="Horizontal Recoil (X):").grid(row=4, column=0, sticky="w", padx=(10,5), pady=(10,2))
        self.secondary_recoil_x_entry = customtkinter.CTkEntry(secondary_weapon_group_box, width=50)
        self.secondary_recoil_x_entry.grid(row=5, column=0, sticky="w", padx=10, pady=(0,2))
        self.secondary_recoil_x_entry.bind("<Return>", self._update_secondary_recoil_x_from_entry)
        self.secondary_recoil_x_slider = customtkinter.CTkSlider(secondary_weapon_group_box, from_=-5000, to=5000, number_of_steps=10000, command=self._update_secondary_recoil_x_from_slider_scaled)
        self.secondary_recoil_x_slider.set(0)
        self.secondary_recoil_x_slider.grid(row=6, column=0, sticky="ew", padx=10, pady=(2,10))

        self.secondary_weapon_enabled_checkbox = customtkinter.CTkCheckBox(content_frame, text="Enable Secondary Weapon", command=self.toggle_secondary_weapon_enabled)
        self.secondary_weapon_enabled_checkbox.select() if self.recoil_controller.settings.secondary_weapon_enabled else self.secondary_weapon_enabled_checkbox.deselect()
        self.secondary_weapon_enabled_checkbox.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.toggle_button = customtkinter.CTkButton(content_frame, text="Disabled", command=self.toggle_recoil, fg_color="#e83434", hover_color="#BE2B2B")
        self.toggle_button.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.settings_button = customtkinter.CTkButton(content_frame, text="Settings", command=self.open_settings)
        self.settings_button.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        self.presets_button = customtkinter.CTkButton(content_frame, text="Presets", command=self.open_presets_dialog)
        self.presets_button.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        self.recoil_active = False
        self.active_weapon = "primary"

        self.update_main_ui_recoil_values()

        self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        self.keyboard_listener.start()

        self.pynput_mouse_listener = mouse.Listener(on_click=self._on_mouse_click, on_scroll=self._on_scroll_event)
        self.pynput_mouse_listener.start()

    def toggle_secondary_weapon_enabled(self):
        is_checked = self.secondary_weapon_enabled_checkbox.get() == 1
        self.recoil_controller.settings.secondary_weapon_enabled = is_checked
        self.recoil_controller.logger.info(f"Enable Secondary Weapon: {is_checked}")
        self.update_main_ui_recoil_values()
        self.save_settings()

    def _update_primary_recoil_y_from_slider_scaled(self, value):
        scaled_value = value / 100.0
        self.recoil_controller.settings.primary_recoil_y = scaled_value
        self.primary_recoil_y_entry.delete(0, tk.END)
        self.primary_recoil_y_entry.insert(0, f"{scaled_value:.2f}")
        if self.active_weapon == "primary":
            self.recoil_controller.set_recoil_y(scaled_value)
        self.save_settings()

    def _update_primary_recoil_x_from_slider_scaled(self, value):
        scaled_value = value / 1000.0
        self.recoil_controller.settings.primary_recoil_x = scaled_value
        self.primary_recoil_x_entry.delete(0, tk.END)
        self.primary_recoil_x_entry.insert(0, f"{scaled_value:.3f}")
        if self.active_weapon == "primary":
            self.recoil_controller.set_recoil_x(scaled_value)
        self.save_settings()

    def _update_secondary_recoil_y_from_slider_scaled(self, value):
        scaled_value = value / 100.0
        self.recoil_controller.settings.secondary_recoil_y = scaled_value
        self.secondary_recoil_y_entry.delete(0, tk.END)
        self.secondary_recoil_y_entry.insert(0, f"{scaled_value:.2f}")
        if self.active_weapon == "secondary":
            self.recoil_controller.set_recoil_y(scaled_value)
        self.save_settings()

    def _update_secondary_recoil_x_from_slider_scaled(self, value):
        scaled_value = value / 1000.0
        self.recoil_controller.settings.secondary_recoil_x = scaled_value
        self.secondary_recoil_x_entry.delete(0, tk.END)
        self.secondary_recoil_x_entry.insert(0, f"{scaled_value:.3f}")
        if self.active_weapon == "secondary":
            self.recoil_controller.set_recoil_x(scaled_value)
        self.save_settings()

    def _update_primary_recoil_y_from_entry(self, event):
        try:
            value = float(self.primary_recoil_y_entry.get())
            self.recoil_controller.settings.primary_recoil_y = value
            self.primary_recoil_y_slider.set(int(value * 100))
            if self.active_weapon == "primary":
                self.recoil_controller.set_recoil_y(value)
            self.save_settings()
        except ValueError:
            CTkMessagebox(title="Error", message="Invalid value for Primary Recoil Y. Please enter a number.", icon="cancel").get()
            self.primary_recoil_y_entry.delete(0, tk.END)
            self.primary_recoil_y_entry.insert(0, f"{self.recoil_controller.settings.primary_recoil_y:.2f}")

    def _update_primary_recoil_x_from_entry(self, event):
        try:
            value = float(self.primary_recoil_x_entry.get())
            self.recoil_controller.settings.primary_recoil_x = value
            self.primary_recoil_x_slider.set(int(value * 1000))
            if self.active_weapon == "primary":
                self.recoil_controller.set_recoil_x(value)
            self.save_settings()
        except ValueError:
            CTkMessagebox(title="Error", message="Invalid value for Primary Recoil X. Please enter a number.", icon="cancel").get()
            self.primary_recoil_x_entry.delete(0, tk.END)
            self.primary_recoil_x_entry.insert(0, f"{self.recoil_controller.settings.primary_recoil_x:.3f}")

    def _update_secondary_recoil_y_from_entry(self, event):
        try:
            value = float(self.secondary_recoil_y_entry.get())
            self.recoil_controller.settings.secondary_recoil_y = value
            self.secondary_recoil_y_slider.set(int(value * 100))
            if self.active_weapon == "secondary":
                self.recoil_controller.set_recoil_y(value)
            self.save_settings()
        except ValueError:
            CTkMessagebox(title="Error", message="Invalid value for Secondary Recoil Y. Please enter a number.", icon="cancel").get()
            self.secondary_recoil_y_entry.delete(0, tk.END)
            self.secondary_recoil_y_entry.insert(0, f"{self.recoil_controller.settings.secondary_recoil_y:.2f}")

    def _update_secondary_recoil_x_from_entry(self, event):
        try:
            value = float(self.secondary_recoil_x_entry.get())
            self.recoil_controller.settings.secondary_recoil_x = value
            self.secondary_recoil_x_slider.set(int(value * 1000))
            if self.active_weapon == "secondary":
                self.recoil_controller.set_recoil_x(value)
            self.save_settings()
        except ValueError:
            CTkMessagebox(title="Error", message="Invalid value for Secondary Recoil X. Please enter a number.", icon="cancel").get()
            self.secondary_recoil_x_entry.delete(0, tk.END)
            self.secondary_recoil_x_entry.insert(0, f"{self.recoil_controller.settings.secondary_recoil_x:.3f}")

    def _on_key_press(self, key):
        if hasattr(self, 'settings_dialog') and self.settings_dialog and self.settings_dialog.winfo_exists() and self.settings_dialog.hotkey_capture_mode:
            self.settings_dialog.process_captured_key(key)
            return

        hotkey_string = self._get_key_string(key)
        self._process_hotkey(hotkey_string)

    def update_main_ui_recoil_values(self):
        self.primary_recoil_y_slider.set(int(self.recoil_controller.settings.primary_recoil_y * 100))
        self.primary_recoil_y_entry.delete(0, tk.END)
        self.primary_recoil_y_entry.insert(0, f"{self.recoil_controller.settings.primary_recoil_y:.2f}")

        self.primary_recoil_x_slider.set(int(self.recoil_controller.settings.primary_recoil_x * 1000))
        self.primary_recoil_x_entry.delete(0, tk.END)
        self.primary_recoil_x_entry.insert(0, f"{self.recoil_controller.settings.primary_recoil_x:.3f}")

        self.secondary_recoil_y_slider.set(int(self.recoil_controller.settings.secondary_recoil_y * 100))
        self.secondary_recoil_y_entry.delete(0, tk.END)
        self.secondary_recoil_y_entry.insert(0, f"{self.recoil_controller.settings.secondary_recoil_y:.2f}")

        self.secondary_recoil_x_slider.set(int(self.recoil_controller.settings.secondary_recoil_x * 1000))
        self.secondary_recoil_x_entry.delete(0, tk.END)
        self.secondary_recoil_x_entry.insert(0, f"{self.recoil_controller.settings.secondary_recoil_x:.3f}")

        if self.active_weapon == "primary":
            self.recoil_controller.set_recoil_y(self.recoil_controller.settings.primary_recoil_y)
            self.recoil_controller.set_recoil_x(self.recoil_controller.settings.primary_recoil_x)
        else:
            self.recoil_controller.set_recoil_y(self.recoil_controller.settings.secondary_recoil_y)
            self.recoil_controller.set_recoil_x(self.recoil_controller.settings.secondary_recoil_x)
        
        self.recoil_controller.logger.info("UI updated: Primary (X={:.3f}, Y={:.2f}) | Secondary (X={:.3f}, Y={:.2f})".format(
            self.recoil_controller.settings.primary_recoil_x,
            self.recoil_controller.settings.primary_recoil_y,
            self.recoil_controller.settings.secondary_recoil_x,
            self.recoil_controller.settings.secondary_recoil_y
        ))

    def _get_key_string(self, key):
        """Converte um objeto key do pynput para uma string."""
        try:
            return key.char.upper()
        except AttributeError:
            return str(key).replace('Key.', '').upper()

    def _get_mouse_hotkey_string(self, button):
        """Converte um evento de botão do mouse para uma string de hotkey."""
        if button == Button.x1:
            return "MOUSE_X1"
        elif button == Button.x2:
            return "MOUSE_X2"
        elif button == Button.left:
            return "MOUSE_LEFT"
        elif button == Button.right:
            return "MOUSE_RIGHT"
        elif button == Button.middle:
            return "MOUSE_MIDDLE"
        
        return ""

    def _on_mouse_click(self, x, y, button, pressed):
        if hasattr(self, 'settings_dialog') and self.settings_dialog and self.settings_dialog.winfo_exists() and self.settings_dialog.hotkey_capture_mode:
            if pressed:
                if button is not None:
                    hotkey_string = self._get_mouse_hotkey_string(button)
                    self.settings_dialog.process_captured_key(hotkey_string)
            return

        if pressed:
            if button is not None:
                hotkey_string = self._get_mouse_hotkey_string(button)
                self._process_hotkey(hotkey_string)

    def _on_scroll_event(self, x, y, dx, dy):
        if hasattr(self, 'settings_dialog') and self.settings_dialog and self.settings_dialog.winfo_exists() and self.settings_dialog.hotkey_capture_mode:
            hotkey_string = ""
            if dy > 0:
                hotkey_string = "SCROLL_UP"
            elif dy < 0:
                hotkey_string = "SCROLL_DOWN"
            
            if hotkey_string:
                self.settings_dialog.process_captured_key(hotkey_string)
            return

        if dy > 0:
            self._process_hotkey("SCROLL_UP")
        elif dy < 0:
            self._process_hotkey("SCROLL_DOWN")

    def open_settings(self):
        self.settings_dialog = SettingsDialog(self.recoil_controller, self)
        self.settings_dialog.grab_set()
        self.settings_dialog.wait_window()
        self.recoil_controller.logger.info("SettingsDialog closed. Re-registering hotkeys.")
        self.save_settings()

    def open_presets_dialog(self):
        self.presets_dialog = PresetsDialog(self.recoil_controller, self)
        self.presets_dialog.grab_set()
        self.presets_dialog.wait_window()

    def load_settings(self):
        settings_path = os.path.join(CONFIG_DIR, "settings.cfg")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    loaded_settings_dict = json.load(f)
                self.recoil_controller.settings = self.recoil_controller.settings.from_dict(loaded_settings_dict)
                self.recoil_controller.logger.info("Settings loaded successfully.")
            except Exception as e:
                self.recoil_controller.logger.error(f"Error loading settings: {e}")
        else:
            self.recoil_controller.logger.info("settings.cfg not found. Using default settings.")

    def save_settings(self):
        settings_path = os.path.join(CONFIG_DIR, "settings.cfg")
        try:
            with open(settings_path, 'w') as f:
                json.dump(self.recoil_controller.settings.to_dict(), f, indent=4)
            self.recoil_controller.logger.info("Configurações salvas com sucesso.")
        except Exception as e:
            self.recoil_controller.logger.error(f"Erro ao salvar configurações: {e}")

    def toggle_script_running(self):
        if self.recoil_controller.script_running:
            self.recoil_controller.stop()
            self.toggle_button.configure(text="Disabled", fg_color="#e83434", hover_color="#BE2B2B")
            self.recoil_active = False
            print("Script principal DISABLED")
        else:
            self.recoil_controller.start()
            self.toggle_button.configure(text="Enabled", fg_color="#0fa711", hover_color="#0e8d0f")
            self.recoil_active = True
            print("Script principal ENABLED")

    def toggle_recoil(self):
        if self.recoil_active:
            self.recoil_controller.stop()
            self.recoil_active = False
            self.toggle_button.configure(text="Disabled", fg_color="#e83434", hover_color="#BE2B2B")
            self.recoil_controller.logger.info("Recoil Disabled.")
        else:
            self.recoil_controller.start()
            self.recoil_active = True
            self.toggle_button.configure(text="Enabled", fg_color="#0fa711", hover_color="#0e8d0f")
            self.recoil_controller.logger.info("Recoil Enabled.")

    def on_closing(self):
        self.recoil_controller.stop()
        if self.keyboard_listener and self.keyboard_listener.is_alive():
            self.keyboard_listener.stop()
            self.keyboard_listener.join()
        if self.pynput_mouse_listener and self.pynput_mouse_listener.is_alive():
            self.pynput_mouse_listener.stop()
            self.pynput_mouse_listener.join()
        self.destroy()

    def _process_hotkey(self, hotkey_string):
        if hotkey_string in self.recoil_controller.settings.primary_weapon_hotkey or \
           hotkey_string in self.recoil_controller.settings.primary_weapon_hotkey_2:
            self.active_weapon = "primary"
            self.recoil_controller.base_recoil_y = self.recoil_controller.settings.primary_recoil_y
            self.recoil_controller.base_recoil_x = self.recoil_controller.settings.primary_recoil_x
            self.update_main_ui_recoil_values()
            self.recoil_controller.logger.info(f"Primary weapon activated by hotkey: {hotkey_string}. Slider values now control primary recoil.")

        elif hotkey_string in self.recoil_controller.settings.secondary_weapon_hotkey or \
             hotkey_string in self.recoil_controller.settings.secondary_weapon_hotkey_2:
            if self.recoil_controller.settings.secondary_weapon_enabled:
                self.active_weapon = "secondary"
                self.recoil_controller.base_recoil_y = self.recoil_controller.settings.secondary_recoil_y
                self.recoil_controller.base_recoil_x = self.recoil_controller.settings.secondary_recoil_x
                self.update_main_ui_recoil_values()
                self.recoil_controller.logger.info(f"Secondary weapon activated by hotkey: {hotkey_string}. Slider values now control secondary recoil.")
            else:
                self.recoil_controller.logger.warning(f"Secondary weapon disabled in settings. Hotkey {hotkey_string} ignored.")

        elif hotkey_string == 'F6':
            self.toggle_recoil()
        elif hotkey_string == 'F7':
            self.open_settings()
        elif hotkey_string == 'F8':
            self.toggle_script_running()


if __name__ == '__main__':
    customtkinter.set_appearance_mode("Dark")
    customtkinter.set_default_color_theme("blue")

    app = RecoilControllerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
