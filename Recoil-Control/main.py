import sys
import os
import json
import logging
import requests
import shutil
from typing import Optional
import subprocess
import threading
import time

NGROK_BASE_URL = "https://proven-on-owl.ngrok-free.app"

__version__ = "2.0.0"

script_dir = os.path.dirname(os.path.abspath(__file__))

COLOR_BACKGROUND = "#121212"
COLOR_FRAME = "#1A1A1A"
COLOR_ACCENT = "#007BFF"
COLOR_ACCENT_DARK = "#004C99"
COLOR_ACCENT_LIGHT = "#66B2FF"
COLOR_TEXT = "#EAEAEA"
COLOR_DANGER = "#e83434"
COLOR_SUCCESS = "#0fa711"
COLOR_HOVER = "#0056b3"

FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 14, "bold")
FONT_BODY = (FONT_FAMILY, 12)
FONT_BUTTON = (FONT_FAMILY, 12, "bold")

TRANSLATIONS = {
    "en": {
        "settings": "Settings",
        "general": "General",
        "language": "Language",
        "shoot_delay": "Shoot Delay (s):",
        "max_shots": "Max Shots:",
        "sensitivity": "Sensitivity",
        "mouse_dpi": "Mouse DPI:",
        "game_sensitivity": "Game Sensitivity:",
        "global_sensitivity_multiplier": "Global Sensitivity Multiplier:",
        "hotkeys": "Hotkeys",
        "primary_weapon_1": "Primary Weapon 1:",
        "primary_weapon_2": "Primary Weapon 2:",
        "secondary_weapon_1": "Secondary Weapon 1:",
        "secondary_weapon_2": "Secondary Weapon 2:",
        "record": "Record",
        "press_key_prompt": "Press a key or mouse button...",
        "tbag_macro": "T-bag Macro",
        "activation_hotkey": "Activation Hotkey:",
        "action_key": "Action Key:",
        "delay_s": "Delay (s):",
        "version_info": "Version {__version__} | Created by K1ngPT-X",
        "language_change": "Language Change",
        "restart_prompt": "Please restart the application for the language changes to take full effect.",
        "app_title": "Recoil Control",
        "primary": "Primary",
        "secondary": "Secondary",
        "enable_tbag_macro": "T-bag Macro",
        "presets": "Presets",
        "advanced": "Advanced",
        "disabled": "Disabled",
        "enabled": "Enabled",
        "vertical_recoil": "Vertical Recoil (Y)",
        "horizontal_recoil": "Horizontal Recoil (X)",
        "enable_secondary_weapon": "Enable Secondary Weapon",
        "about": "About",
        "created_by": "Created by K1ngPT-X",
        "do_not_show_again": "Do not show again",
        "close": "Close",
        "agent_presets": "Agent Presets",
        "attackers": "Attackers",
        "defenders": "Defenders",
        "previous": "Previous",
        "next": "Next",
        "page_info": "Page {current_page} of {total_pages}",
        "presets_for": "Presets for {agent_name}",
        "save_preset": "Save Preset",
        "enter_preset_name": "Enter preset name...",
        "save": "Save",
        "manage_existing": "Manage Existing",
        "no_presets_found": "No presets found",
        "load": "Load",
        "delete": "Delete",
        "confirm_load_title": "Confirm Load Preset",
        "confirm_load_message": "Are you sure you want to load the preset '{selected_preset}'?\nThis will overwrite current settings.",
        "confirm_delete_title": "Confirm Delete Preset",
        "confirm_delete_message": "Are you sure you want to delete the preset '{selected_preset}'?",
        "warning": "Warning",
        "select_preset_to_load": "Please select a preset to load.",
        "select_preset_to_delete": "Please select a preset to delete.",
        "error": "Error",
        "preset_not_found": "Preset file not found: {preset_file_path}",
        "error_loading_preset": "Error loading preset: {e}",
        "error_saving_preset": "Error saving preset: {e}",
        "error_deleting_preset": "Error deleting preset: {e}",
        "success": "Success",
        "preset_loaded_successfully": "Preset '{selected_preset}' loaded successfully for {agent_name}!",
        "preset_saved_successfully": "Preset '{preset_name}' saved for {agent_name}!",
        "preset_deleted_successfully": "Preset '{selected_preset}' deleted successfully!",
        "enter_preset_name_error": "Please enter a name for the preset.",
        "ask_ai_placeholder": "Ask the AI for help or to make a change...",
        "ask_ai_button": "Ask AI",
        "chat_title": "AI Assistant Chat",
        "chat_input_placeholder": "Type your message here...",
        "chat_send_button": "Send",
        "pin_dialog_title": "Enter PIN",
        "enter_pin_prompt": "Please enter the PIN you received from the Discord bot to send a report",
        "report_auth_required_message": "To use /report, you need to authenticate your Discord account. Type /login on Discord to get a PIN and enter it in the box that appears. This helps us identify you for better support, as moderators receive the chat history."
    },
    "pt": {
        "settings": "Configurações",
        "general": "Geral",
        "language": "Idioma",
        "shoot_delay": "Atraso de Disparo (s):",
        "max_shots": "Máximo de Disparos:",
        "sensitivity": "Sensibilidade",
        "mouse_dpi": "DPI do Mouse:",
        "game_sensitivity": "Sensibilidade do Jogo:",
        "global_sensitivity_multiplier": "Multiplicador Global de Sensibilidade:",
        "hotkeys": "Teclas de Atalho",
        "primary_weapon_1": "Arma Primária 1:",
        "primary_weapon_2": "Arma Primária 2:",
        "secondary_weapon_1": "Arma Secundária 1:",
        "secondary_weapon_2": "Arma Secundária 2:",
        "record": "Gravar",
        "press_key_prompt": "Pressione uma tecla ou botão do mouse...",
        "tbag_macro": "Macro T-bag",
        "activation_hotkey": "Tecla de Ativação:",
        "action_key": "Tecla de Ação:",
        "delay_s": "Atraso (s):",
        "version_info": "Versão {__version__} | Criado por K1ngPT-X",
        "language_change": "Mudança de Idioma",
        "restart_prompt": "Por favor, reinicie a aplicação para que as alterações de idioma tenham efeito.",
        "app_title": "Controle de Recuo",
        "primary": "Primária",
        "secondary": "Secundária",
        "enable_tbag_macro": "Macro T-bag",
        "presets": "Predefinições",
        "advanced": "Avançado",
        "disabled": "Desativado",
        "enabled": "Ativado",
        "vertical_recoil": "Recuo Vertical (Y)",
        "horizontal_recoil": "Recuo Horizontal (X)",
        "enable_secondary_weapon": "Ativar Arma Secundária",
        "about": "Sobre",
        "created_by": "Criado por K1ngPT-X",
        "do_not_show_again": "Não mostrar novamente",
        "close": "Fechar",
        "agent_presets": "Predefinições de Agentes",
        "attackers": "Atacantes",
        "defenders": "Defensores",
        "previous": "Anterior",
        "next": "Próximo",
        "page_info": "Página {current_page} de {total_pages}",
        "presets_for": "Predefinições para {agent_name}",
        "save_preset": "Salvar Predefinição",
        "enter_preset_name": "Digite o nome da predefinição...",
        "save": "Salvar",
        "manage_existing": "Gerenciar Existentes",
        "no_presets_found": "Nenhuma predefinição encontrada",
        "load": "Carregar",
        "delete": "Excluir",
        "confirm_load_title": "Confirmar Carregamento",
        "confirm_load_message": "Tem certeza de que deseja carregar a predefinição '{selected_preset}'?\nIsso substituirá as configurações atuais.",
        "confirm_delete_title": "Confirmar Exclusão",
        "confirm_delete_message": "Tem certeza de que deseja excluir a predefinição '{selected_preset}'?",
        "warning": "Aviso",
        "select_preset_to_load": "Por favor, selecione uma predefinição para carregar.",
        "select_preset_to_delete": "Por favor, selecione uma predefinição para excluir.",
        "error": "Erro",
        "preset_not_found": "Arquivo de predefinição não encontrado: {preset_file_path}",
        "error_loading_preset": "Erro ao carregar predefinição: {e}",
        "error_saving_preset": "Erro ao salvar predefinição: {e}",
        "error_deleting_preset": "Erro ao excluir predefinição: {e}",
        "success": "Sucesso",
        "preset_loaded_successfully": "Predefinição '{selected_preset}' carregada com sucesso para {agent_name}!",
        "preset_saved_successfully": "Predefinição '{preset_name}' salva com sucesso para {agent_name}!",
        "preset_deleted_successfully": "Predefinição '{selected_preset}' excluída com sucesso!",
        "enter_preset_name_error": "Por favor, digite um nome para a predefinição.",
        "ask_ai_placeholder": "Peça ajuda à IA ou para fazer uma alteração...",
        "ask_ai_button": "Perguntar à IA",
        "chat_title": "Chat com Assistente de IA",
        "chat_input_placeholder": "Digite sua mensagem aqui...",
        "chat_send_button": "Enviar",
        "pin_dialog_title": "Inserir PIN",
        "enter_pin_prompt": "Para enviar um relatório, insira o PIN que você recebeu do bot do Discord",
        "report_auth_required_message": "Para usar o /report, você precisa autenticar sua conta Discord. Digite /login no Discord para obter um PIN e insira-o na caixa que aparecerá. Isso nos ajuda a identificar você para melhor suporte, pois os moderadores recebem o histórico do chat."
    }
}

def center_window(window, width, height):
    """Centers a tkinter window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def run_update_check_and_exit_if_needed():
    update_url = "https://raw.githubusercontent.com/K1ngPT-X/R6-Recoil-Control/refs/heads/main/Version.txt"
    try:
        response = requests.get(update_url)
        response.raise_for_status()
        latest_version = response.text.strip()
        
        if latest_version > __version__:
            from CTkMessagebox import CTkMessagebox
            msg = CTkMessagebox(title="New Version Available",
                                message=f"A new version ({latest_version}) is available! Your current version is ({__version__}).\nDo you want to download now?",
                                option_1="No", option_2="Yes", icon="question")
            response = msg.get()
            if response == "Yes":
                download_link = f"https://github.com/K1ngPT-X/R6-Recoil-Control/releases/download/v{latest_version}/R6-Recoil-Control.exe"
                
                downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
                os.makedirs(downloads_folder, exist_ok=True)
                output_path = os.path.join(downloads_folder, f"R6-Recoil-Control_v{latest_version}.exe")
                
                try:
                    with requests.get(download_link, stream=True) as r:
                        r.raise_for_status()
                        with open(output_path, 'wb') as f:
                            shutil.copyfileobj(r.raw, f)
                    CTkMessagebox(title="Download Complete", message=f"The new version has been downloaded to:\n{output_path}\nThe application will be updated and restarted automatically.", icon="info").get()

                    current_app_path = os.path.join(CONFIG_DIR, "output", "R6-Recoil-Control.exe")
                    updater_script_path = os.path.join(script_dir, "update.exe")
                    
                    subprocess.Popen([updater_script_path, current_app_path, output_path])
                    
                    sys.exit()

                except requests.exceptions.RequestException as req_e:
                    logging.error(f"Could not download the update: {req_e}\nPlease check the link or your connection.")
                    CTkMessagebox(title="Download Error", message=f"Could not download the update: {req_e}\nPlease check the link or your connection.", icon="cancel").get()
                except Exception as e:
                    logging.error(f"An error occurred while saving the file: {e}")
                    CTkMessagebox(title="Error", message=f"An error occurred while saving the file: {e}", icon="cancel").get()
        else:
            logging.info("You already have the latest version.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error checking for updates: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while checking for updates: {e}")

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
from rate_limiter import RateLimiter

try:
    from recoil_controller import RecoilController
except ImportError:
    logging.error("Module 'recoil_controller' not found.")
    sys.exit(1)


class SettingsDialog(customtkinter.CTkToplevel):
    def __init__(self, recoil_controller, main_app_instance, parent=None):
        super().__init__(parent)
        self.recoil_controller = recoil_controller
        self.main_app_instance = main_app_instance
        center_window(self, 450, 650)
        self.configure(fg_color=COLOR_BACKGROUND)
        self.init_ui()
        self.update_ui_text()

    def _(self, key, **kwargs):
        return self.main_app_instance._(key, **kwargs)

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll_frame = customtkinter.CTkScrollableFrame(self, fg_color=COLOR_BACKGROUND)
        scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        self.general_frame = customtkinter.CTkFrame(scroll_frame, fg_color=COLOR_FRAME, border_width=0)
        self.general_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.general_frame.grid_columnconfigure(1, weight=1)

        self.general_label = customtkinter.CTkLabel(self.general_frame, text="", font=FONT_SUBTITLE)
        self.general_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")
        
        self.language_label = customtkinter.CTkLabel(self.general_frame, text="", font=FONT_BODY)
        self.language_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.language_menu = customtkinter.CTkOptionMenu(self.general_frame, values=["English", "Português"], command=self.on_language_change, font=FONT_BODY)
        self.language_menu.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        current_language = getattr(self.recoil_controller.settings, 'language', 'en')
        self.language_menu.set("Português" if current_language == "pt" else "English")

        self.settings_labels = {}
        settings_items = {
            "shoot_delay": ("shoot_delay_spinbox", "shoot_delay"),
            "max_shots": ("max_shots_spinbox", "max_shots"),
        }

        for i, (key, (widget_name, setting_key)) in enumerate(settings_items.items(), start=2):
            label = customtkinter.CTkLabel(self.general_frame, text="", font=FONT_BODY)
            label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
            self.settings_labels[key] = label
            entry = customtkinter.CTkEntry(self.general_frame, font=FONT_BODY)
            entry.insert(0, str(getattr(self.recoil_controller.settings, setting_key)))
            entry.grid(row=i, column=1, sticky="ew", padx=10, pady=5)
            entry.bind("<Return>", self.update_settings_event)
            entry.bind("<FocusOut>", self.update_settings_event)
            setattr(self, widget_name, entry)

        self.hotkeys_frame = customtkinter.CTkFrame(scroll_frame, fg_color=COLOR_FRAME, border_width=0)
        self.hotkeys_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.hotkeys_frame.grid_columnconfigure(1, weight=1)

        self.hotkeys_label = customtkinter.CTkLabel(self.hotkeys_frame, text="", font=FONT_SUBTITLE)
        self.hotkeys_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(5, 10), sticky="w")

        self.hotkey_items_labels = {}
        self.hotkey_record_buttons = {}
        hotkey_items = {
            "primary_weapon_1": ("primary_hotkey_input", "primary_weapon_hotkey"),
            "primary_weapon_2": ("primary_hotkey_2_input", "primary_weapon_hotkey_2"),
            "secondary_weapon_1": ("secondary_hotkey_input", "secondary_weapon_hotkey"),
            "secondary_weapon_2": ("secondary_hotkey_2_input", "secondary_weapon_hotkey_2"),
        }

        for i, (key, (widget_name, setting_key)) in enumerate(hotkey_items.items(), start=1):
            label = customtkinter.CTkLabel(self.hotkeys_frame, text="", font=FONT_BODY)
            label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
            self.hotkey_items_labels[key] = label

            entry = customtkinter.CTkEntry(self.hotkeys_frame, state="readonly", font=FONT_BODY)
            entry.grid(row=i, column=1, sticky="ew", padx=10, pady=5)
            entry.configure(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, ", ".join(getattr(self.recoil_controller.settings, setting_key)))
            entry.configure(state="readonly")
            setattr(self, widget_name, entry)
            
            button = customtkinter.CTkButton(self.hotkeys_frame, text="", width=80, font=FONT_BUTTON, command=lambda e=entry, sk=setting_key: self.start_hotkey_capture(e, sk))
            button.grid(row=i, column=2, padx=10, pady=5)
            self.hotkey_record_buttons[key] = button

        self.tbag_frame = customtkinter.CTkFrame(scroll_frame, fg_color=COLOR_FRAME, border_width=0)
        self.tbag_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.tbag_frame.grid_columnconfigure(1, weight=1)

        self.tbag_label = customtkinter.CTkLabel(self.tbag_frame, text="", font=FONT_SUBTITLE)
        self.tbag_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(5, 10), sticky="w")

        self.tbag_activation_label = customtkinter.CTkLabel(self.tbag_frame, text="", font=FONT_BODY)
        self.tbag_activation_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.t_bag_hotkey_input = customtkinter.CTkEntry(self.tbag_frame, state="readonly", font=FONT_BODY)
        self.t_bag_hotkey_input.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        self.tbag_hotkey_record_button = customtkinter.CTkButton(self.tbag_frame, text="", width=80, font=FONT_BUTTON, command=lambda: self.start_hotkey_capture(self.t_bag_hotkey_input, "t_bag_hotkey"))
        self.tbag_hotkey_record_button.grid(row=1, column=2, padx=10, pady=5)
        self.t_bag_hotkey_input.configure(state="normal")
        self.t_bag_hotkey_input.delete(0, tk.END)
        self.t_bag_hotkey_input.insert(0, ", ".join(getattr(self.recoil_controller.settings, setting_key)))
        self.t_bag_hotkey_input.configure(state="readonly")

        self.tbag_action_key_label = customtkinter.CTkLabel(self.tbag_frame, text="", font=FONT_BODY)
        self.tbag_action_key_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.t_bag_key_input = customtkinter.CTkEntry(self.tbag_frame, state="readonly", font=FONT_BODY)
        self.t_bag_key_input.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        self.tbag_key_record_button = customtkinter.CTkButton(self.tbag_frame, text="", width=80, font=FONT_BUTTON, command=lambda: self.start_hotkey_capture(self.t_bag_key_input, "t_bag_key"))
        self.tbag_key_record_button.grid(row=2, column=2, padx=10, pady=5)
        self.t_bag_key_input.configure(state="normal")
        self.t_bag_key_input.delete(0, tk.END)
        self.t_bag_key_input.insert(0, self.recoil_controller.settings.t_bag_key)
        self.t_bag_key_input.configure(state="readonly")

        self.tbag_delay_label = customtkinter.CTkLabel(self.tbag_frame, text="", font=FONT_BODY)
        self.tbag_delay_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.t_bag_delay_spinbox = customtkinter.CTkEntry(self.tbag_frame, font=FONT_BODY)
        self.t_bag_delay_spinbox.insert(0, str(self.recoil_controller.settings.t_bag_delay))
        self.t_bag_delay_spinbox.grid(row=3, column=1, sticky="ew", padx=10, pady=5)
        self.t_bag_delay_spinbox.bind("<Return>", self.update_settings_event)
        self.t_bag_delay_spinbox.bind("<FocusOut>", self.update_settings_event)

        self.version_label = customtkinter.CTkLabel(scroll_frame, text="", font=FONT_BODY, text_color="gray50")
        self.version_label.grid(row=3, column=0, columnspan=2, pady=(20, 10))
        
        self.hotkey_capture_mode = False
        self.current_hotkey_field = None

    def update_ui_text(self):
        self.title(self._("settings"))
        self.general_label.configure(text=self._("general"))
        self.language_label.configure(text=self._("language"))
        
        for key, label in self.settings_labels.items():
            label.configure(text=self._(key))

        self.hotkeys_label.configure(text=self._("hotkeys"))
        for key, label in self.hotkey_items_labels.items():
            label.configure(text=self._(key))
        for _, button in self.hotkey_record_buttons.items():
            button.configure(text=self._("record"))

        self.tbag_label.configure(text=self._("tbag_macro"))
        self.tbag_activation_label.configure(text=self._("activation_hotkey"))
        self.tbag_action_key_label.configure(text=self._("action_key"))
        self.tbag_delay_label.configure(text=self._("delay_s"))
        self.tbag_hotkey_record_button.configure(text=self._("record"))
        self.tbag_key_record_button.configure(text=self._("record"))

        self.version_label.configure(text=self._("version_info", __version__=__version__))
        
    def update_settings(self):
        try:
            self.recoil_controller.settings.shoot_delay = float(self.shoot_delay_spinbox.get())
            self.recoil_controller.settings.max_shots = int(self.max_shots_spinbox.get())
            self.recoil_controller.settings.t_bag_delay = float(self.t_bag_delay_spinbox.get())
        except ValueError:
            logging.error("Invalid input values for settings. Please enter valid numbers.")

    def on_language_change(self, choice):
        language_code = "pt" if choice == "Português" else "en"
        self.recoil_controller.settings.language = language_code
        self.main_app_instance.save_settings()
        self.main_app_instance.update_ui_language()
        self.update_ui_text()

    def start_hotkey_capture(self, input_field, setting_key):
        self.current_hotkey_field = input_field
        self.setting_key_to_update = setting_key
        self.hotkey_capture_mode = True
        
        if self.current_hotkey_field is not None:
            self.current_hotkey_field.configure(state="normal")
            self.current_hotkey_field.delete(0, tk.END)
            self.current_hotkey_field.insert(0, self._("press_key_prompt"))
            self.current_hotkey_field.configure(state="readonly")

    def stop_hotkey_capture(self, hotkey_string):
        if self.hotkey_capture_mode:
            self.hotkey_capture_mode = False
            if self.current_hotkey_field is not None:
                self.current_hotkey_field.configure(state="normal")
                self.current_hotkey_field.delete(0, tk.END)
                self.current_hotkey_field.insert(0, hotkey_string)
                self.current_hotkey_field.configure(state="readonly")
            
            if self.setting_key_to_update == "t_bag_key":
                 setattr(self.recoil_controller.settings, self.setting_key_to_update, hotkey_string)
            else:
                setattr(self.recoil_controller.settings, self.setting_key_to_update, [hotkey_string])

        if self.setting_key_to_update in ["primary_weapon_hotkey", "secondary_weapon_hotkey", "primary_weapon_hotkey_2", "secondary_weapon_hotkey_2", "t_bag_hotkey", "t_bag_key"]:
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


class PresetsDialog(customtkinter.CTkToplevel):
    def __init__(self, recoil_controller, main_app_instance, icon_cache, parent=None):
        super().__init__(parent)
        self.recoil_controller = recoil_controller
        self.main_app_instance = main_app_instance
        self.icon_cache = icon_cache
        center_window(self, 800, 600)
        self.configure(fg_color=COLOR_BACKGROUND)

        self.current_page_attackers = 0
        self.current_page_defenders = 0
        self.items_per_page = 18

        self.init_ui()
        self.update_ui_text()

    def _(self, key, **kwargs):
        return self.main_app_instance._(key, **kwargs)

    def update_ui_text(self):
        self.title(self._("agent_presets"))
        self.tabview.configure(segmented_button_fg_color=COLOR_FRAME)
        
        self.tabview._segmented_button._buttons_dict["Attackers"].configure(text=self._("attackers"))
        self.tabview._segmented_button._buttons_dict["Defenders"].configure(text=self._("defenders"))

        self.attackers_prev_button.configure(text=self._("previous"))
        self.attackers_next_button.configure(text=self._("next"))
        self.defenders_prev_button.configure(text=self._("previous"))
        self.defenders_next_button.configure(text=self._("next"))
        
        self.show_page("attackers")
        self.show_page("defenders")

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = customtkinter.CTkTabview(self, fg_color=COLOR_FRAME)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.attackers_tab = self.tabview.add("Attackers") 
        self.defenders_tab = self.tabview.add("Defenders")

        self.attackers_tab.configure(fg_color=COLOR_BACKGROUND)
        self.defenders_tab.configure(fg_color=COLOR_BACKGROUND)

        self.setup_agent_tab(self.attackers_tab, "attackers")
        self.setup_agent_tab(self.defenders_tab, "defenders")

    def setup_agent_tab(self, tab, agent_type):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        agents_grid_frame = customtkinter.CTkScrollableFrame(tab, fg_color=COLOR_BACKGROUND)
        agents_grid_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        agents_grid_frame.grid_columnconfigure(tuple(range(6)), weight=1)
        
        nav_frame = customtkinter.CTkFrame(tab, fg_color=COLOR_BACKGROUND)
        nav_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        nav_frame.grid_columnconfigure(1, weight=1)

        prev_button = customtkinter.CTkButton(nav_frame, text="", font=FONT_BUTTON, fg_color=COLOR_FRAME, hover_color=COLOR_ACCENT, command=lambda: self.change_page(agent_type, -1))
        prev_button.grid(row=0, column=0, padx=10, pady=5)
        
        page_label = customtkinter.CTkLabel(nav_frame, text="", font=FONT_BODY)
        page_label.grid(row=0, column=1, padx=10, pady=5)

        next_button = customtkinter.CTkButton(nav_frame, text="", font=FONT_BUTTON, fg_color=COLOR_FRAME, hover_color=COLOR_ACCENT, command=lambda: self.change_page(agent_type, 1))
        next_button.grid(row=0, column=2, padx=10, pady=5)

        if agent_type == "attackers":
            self.attackers_agents = self.get_agent_list("attackers")
            self.attackers_grid = agents_grid_frame
            self.attackers_page_label = page_label
            self.attackers_prev_button = prev_button
            self.attackers_next_button = next_button
            self.total_pages_attackers = self._calculate_total_pages(self.attackers_agents)
            self.show_page("attackers")
        else:
            self.defenders_agents = self.get_agent_list("defenders")
            self.defenders_grid = agents_grid_frame
            self.defenders_page_label = page_label
            self.defenders_prev_button = prev_button
            self.defenders_next_button = next_button
            self.total_pages_defenders = self._calculate_total_pages(self.defenders_agents)
            self.show_page("defenders")
            
    def _calculate_total_pages(self, agent_list):
        num_agents = len(agent_list)
        if num_agents == 0:
            return 0
            
        total_pages = (num_agents + self.items_per_page - 1) // self.items_per_page
        
        rem = num_agents % self.items_per_page
        if rem > 0 and rem <= 2 and total_pages > 1:
            total_pages -= 1
            
        return total_pages

    def get_agent_list(self, agent_type):
        if agent_type == "attackers":
            return [
                "Striker", "Sledge", "Thatcher", "Ash", "Thermite", "Twitch",
                "Montagne", "Glaz", "Fuze", "Blitz", "IQ", "Buck",
                "Blackbeard", "Capitao", "Hibana", "Jackal", "Ying", "Zofia",
                "Dokkaebi", "Finka", "Lion", "Maverick", "Nomad", "Gridlock",
                "Nokk", "Amaru", "Kali", "Iana", "Ace", "Zero",
                "Flores", "Osa", "Sens", "Grim", "Brava", "Ram",
                "Deimos", "Rauora"
            ]
        elif agent_type == "defenders":
            return [
                "Sentry", "Smoke", "Mute", "Castle", "Pulse", "Doc",
                "Rook", "Kapkan", "Tachanka", "Jager", "Bandit", "Frost",
                "Valkyrie", "Caveira", "Echo", "Mira", "Lesion", "Ela",
                "Vigil", "Maestro", "Alibi", "Clash", "Kaid", "Mozzie",
                "Warden", "Goyo", "Wamai", "Oryx", "Melusi", "Aruni",
                "Thunderbird", "Thorn", "Azami", "Solis", "Fenrir",
                "Tubarao", "Skopos"
            ]
        return []

    def change_page(self, agent_type, direction):
        if agent_type == "attackers":
            self.current_page_attackers += direction
            self.show_page("attackers")
        else:
            self.current_page_defenders += direction
            self.show_page("defenders")

    def show_page(self, agent_type):
        if agent_type == "attackers":
            current_page = self.current_page_attackers
            total_pages = self.total_pages_attackers
            agents = self.attackers_agents
            grid = self.attackers_grid
            page_label = self.attackers_page_label
            prev_button = self.attackers_prev_button
            next_button = self.attackers_next_button
        else:
            current_page = self.current_page_defenders
            total_pages = self.total_pages_defenders
            agents = self.defenders_agents
            grid = self.defenders_grid
            page_label = self.defenders_page_label
            prev_button = self.defenders_prev_button
            next_button = self.defenders_next_button

        for widget in grid.winfo_children():
            widget.destroy()

        start_index = current_page * self.items_per_page
        
        is_last_page = (current_page == total_pages - 1)
        if is_last_page:
            agents_to_display = agents[start_index:]
        else:
            agents_to_display = agents[start_index : start_index + self.items_per_page]

        row, col = 0, 0
        for agent_name in agents_to_display:
            base_path = os.path.join(script_dir, "Agents")
            icon_path = os.path.join(base_path, agent_type, f"{agent_name.lower()}.png")
            
            icon = self.icon_cache.get(icon_path)
            if icon:
                agent_presets_dir = os.path.join(CONFIG_DIR, "presets", agent_name.lower().replace(" ", "_"))
                has_presets = os.path.exists(agent_presets_dir) and any(f.endswith(".json") for f in os.listdir(agent_presets_dir))
                
                button_color = COLOR_ACCENT_DARK if has_presets else COLOR_FRAME

                button = customtkinter.CTkButton(
                    grid,
                    image=icon,
                    text=agent_name,
                    compound="top",
                    font=FONT_BODY,
                    fg_color=button_color,
                    hover_color=COLOR_ACCENT,
                    command=lambda n=agent_name: self.select_agent(n)
                )
                button.grid(row=row, column=col, padx=5, pady=5)
                col += 1
                if col >= 6:
                    col = 0
                    row += 1

        page_label.configure(text=self._("page_info", current_page=current_page + 1, total_pages=total_pages))
        prev_button.configure(state="normal" if current_page > 0 else "disabled")
        next_button.configure(state="normal" if current_page < total_pages - 1 else "disabled")

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
        center_window(self, 450, 300)
        self.configure(fg_color=COLOR_BACKGROUND)
        
        self.title_font = FONT_SUBTITLE
        
        self.init_ui()
        self.update_ui_text()

    def _(self, key, **kwargs):
        return self.main_app_instance._(key, **kwargs)

    def update_ui_text(self):
        self.title(self._("presets_for", agent_name=self.agent_name))
        self.save_preset_label.configure(text=self._("save_preset"))
        self.preset_name_input.configure(placeholder_text=self._("enter_preset_name"))
        self.save_button.configure(text=self._("save"))
        self.manage_existing_label.configure(text=self._("manage_existing"))
        self.load_button.configure(text=self._("load"))
        self.delete_button.configure(text=self._("delete"))
        self.populate_presets_combobox()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=0)
        self.grid_rowconfigure(2, weight=1)
        
        save_frame = customtkinter.CTkFrame(self, fg_color=COLOR_FRAME, border_width=0)
        save_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        save_frame.grid_columnconfigure(0, weight=1)

        self.save_preset_label = customtkinter.CTkLabel(save_frame, text="", font=self.title_font)
        self.save_preset_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")
        
        self.preset_name_input = customtkinter.CTkEntry(save_frame, placeholder_text="", font=FONT_BODY)
        self.preset_name_input.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        self.save_button = customtkinter.CTkButton(save_frame, text="", font=FONT_BUTTON, fg_color=COLOR_ACCENT, hover_color=COLOR_HOVER, command=lambda: self.main_app_instance._perform_save_preset(self.agent_name, self.preset_name_input.get().strip()))
        self.save_button.grid(row=1, column=1, padx=(0, 10), pady=10)

        manage_frame = customtkinter.CTkFrame(self, fg_color=COLOR_FRAME, border_width=0)
        manage_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        manage_frame.grid_columnconfigure(0, weight=1)

        self.manage_existing_label = customtkinter.CTkLabel(manage_frame, text="", font=self.title_font)
        self.manage_existing_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(5, 10), sticky="w")

        self.preset_combo_box = customtkinter.CTkOptionMenu(manage_frame, values=[""], font=FONT_BODY, fg_color=COLOR_FRAME, button_color=COLOR_ACCENT, button_hover_color=COLOR_HOVER, command=self.on_preset_selected)
        self.preset_combo_box.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        self.load_button = customtkinter.CTkButton(manage_frame, text="", width=80, font=FONT_BUTTON, command=lambda: self.main_app_instance._perform_load_preset(self.agent_name, self.preset_combo_box.get()))
        self.load_button.grid(row=1, column=1, padx=(5, 5), pady=10)

        self.delete_button = customtkinter.CTkButton(manage_frame, text="", width=80, font=FONT_BUTTON, command=lambda: self.main_app_instance._perform_delete_preset(self.agent_name, self.preset_combo_box.get()), fg_color=COLOR_DANGER, hover_color="#C82333")
        self.delete_button.grid(row=1, column=2, padx=(0, 10), pady=10)

        self.populate_presets_combobox()

    def on_preset_selected(self, choice):
        self.preset_name_input.delete(0, tk.END)
        if choice != self._("no_presets_found"):
            self.preset_name_input.insert(0, choice)

    def populate_presets_combobox(self):
        agent_presets_dir = os.path.join(CONFIG_DIR, "presets", self.agent_name.lower().replace(" ", "_"))
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
            self.preset_combo_box.configure(values=[self._("no_presets_found")])
            self.preset_combo_box.set(self._("no_presets_found"))
            self.load_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

    def load_preset(self):
        selected_preset = self.preset_combo_box.get()
        if selected_preset == self._("no_presets_found") or not selected_preset:
            msg = CTkMessagebox(title=self._("warning"), message=self._("select_preset_to_load"), icon="warning")
            msg.get()
            return

        msg = CTkMessagebox(title=self._("confirm_load_title"),
                            message=self._("confirm_load_message", selected_preset=selected_preset),
                            option_1="No", option_2="Yes", icon="question")
        response = msg.get()
        if response != "Yes":
            return

        agent_presets_dir = os.path.join(CONFIG_DIR, "presets", self.agent_name.lower().replace(" ", "_"))
        preset_file_path = os.path.join(agent_presets_dir, f"{selected_preset}.json")

        if not os.path.exists(preset_file_path):
            msg = CTkMessagebox(title=self._("error"), message=self._("preset_not_found", preset_file_path=preset_file_path), icon="cancel")
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

            msg = CTkMessagebox(title=self._("success"), message=self._("preset_loaded_successfully", selected_preset=selected_preset, agent_name=self.agent_name), icon="info")
            msg.get()
            self.destroy()
        except Exception as e:
            msg = CTkMessagebox(title=self._("error"), message=self._("error_loading_preset", e=e), icon="cancel")
            msg.get()

class ChatDialog(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.recoil_controller = parent.recoil_controller
        self.rate_limiter = parent.rate_limiter
        self.chat_history_list = []
        self.thinking_bubble = None

        center_window(self, 500, 600)
        self.configure(fg_color=COLOR_BACKGROUND)
        self.title(self.parent._("chat_title"))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        header_frame.grid_columnconfigure(2, weight=1)

        self.chat_title_label = customtkinter.CTkLabel(header_frame, text=self.parent._("chat_title"), font=FONT_SUBTITLE, text_color=COLOR_ACCENT)
        self.chat_title_label.grid(row=0, column=1, padx=0, pady=0)

        self.rate_limit_frame = customtkinter.CTkFrame(header_frame, fg_color="transparent")
        self.rate_limit_frame.grid(row=0, column=2, padx=0, pady=0, sticky="ne")
        self.rate_limit_frame.grid_columnconfigure(0, weight=1)

        self.rpm_label = customtkinter.CTkLabel(self.rate_limit_frame, text="RPM 5/5", font=FONT_BODY, text_color="gray70")
        self.rpm_label.pack(anchor="e")

        self.rpd_label = customtkinter.CTkLabel(self.rate_limit_frame, text="RPD 100/100", font=FONT_BODY, text_color="gray70")
        self.rpd_label.pack(anchor="e")

        self.chat_history_frame = customtkinter.CTkScrollableFrame(self, fg_color=COLOR_FRAME, corner_radius=10)
        self.chat_history_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="nsew")
        self.chat_history_frame.grid_columnconfigure(0, weight=1)


        input_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.chat_input = customtkinter.CTkEntry(input_frame, placeholder_text=self.parent._("chat_input_placeholder"), font=FONT_BODY, corner_radius=10, fg_color=COLOR_FRAME, border_color=COLOR_ACCENT, border_width=1)
        self.chat_input.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.chat_input.bind("<Return>", self.send_message_event)

        self.send_button = customtkinter.CTkButton(input_frame, text=self.parent._("chat_send_button"), font=FONT_BUTTON, width=80, command=self.send_message, fg_color=COLOR_ACCENT, hover_color=COLOR_HOVER, corner_radius=10)
        self.send_button.grid(row=0, column=1)
        
    def _update_rate_limit_display(self):
        try:
            response = requests.get(f"{NGROK_BASE_URL}/rate-limit-status")
            response.raise_for_status()
            data = response.json()
            current_rpm_used = data.get("current_rpm", 0)
            current_rpd_used = data.get("current_rpd", 0)

            rpm_remaining = 5 - current_rpm_used
            rpd_remaining = 100 - current_rpd_used

            self.rpm_label.configure(text=f"RPM {rpm_remaining}/5")
            self.rpd_label.configure(text=f"RPD {rpd_remaining}/100")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching rate limit status: {e}")
        finally:
            pass

    def send_message_event(self, event):
        self.send_message()

    def send_message(self):
        user_prompt = self.chat_input.get().strip()
        if not user_prompt:
            return

        self.add_message("You", user_prompt)
        self.chat_input.delete(0, tk.END)

        if user_prompt.lower() == "/report":
            if not self.recoil_controller.settings.discord_user_id:
                self.add_button_message(
                    "RecoilAI",
                    self.parent._("report_auth_required_message"),
                    self.parent._("Authenticate with Discord"),
                    self._handle_report_authentication
                )
                return
            else:
                self._send_report_to_server()
                return

        is_allowed, message = self.rate_limiter.check_request()
        if not is_allowed:
            self.add_message("RecoilAI", message)
            return

        self.send_button.configure(state="disabled")
        self.add_message("RecoilAI", "Thinking...", is_thinking=True)

        def _ai_request_thread():
            try:
                payload = {
                    "prompt": user_prompt,
                    "current_settings": self.recoil_controller.settings.to_dict(),
                    "chat_history": self.chat_history_list,
                    "discord_user_id": self.recoil_controller.settings.discord_user_id
                }
                response = requests.post(f"{NGROK_BASE_URL}/ai", json=payload)
                response.raise_for_status()
                ai_response = response.json()
                self.after(0, self.parent.process_ai_response, ai_response, self)
                self.after(0, self._update_rate_limit_display)
            except Exception as e:
                self.after(0, self.parent.process_ai_response, {"response_text": f"Error: {e}", "new_settings": None}, self)
                self.after(0, self._update_rate_limit_display)

        threading.Thread(target=_ai_request_thread, daemon=True).start()

    def add_message(self, sender, message, is_thinking=False):
        if self.thinking_bubble:
            self.thinking_bubble.destroy()
            self.thinking_bubble = None

        if sender == "You":
            pack_anchor = "e"
            justify_align = "right"
            bubble_color = COLOR_ACCENT
            text_color = "white"
        else:
            pack_anchor = "w"
            justify_align = "left"
            bubble_color = "#3A3A3A"
            text_color = COLOR_TEXT

        bubble_container = customtkinter.CTkFrame(self.chat_history_frame, fg_color="transparent")
        bubble_container.pack(fill="x", padx=5, pady=0)

        bubble = customtkinter.CTkFrame(bubble_container, fg_color=bubble_color, corner_radius=15)
        bubble.pack(anchor=pack_anchor, padx=10, pady=5, ipadx=5)

        sender_label = customtkinter.CTkLabel(bubble, text=sender, font=(FONT_FAMILY, 11, "bold"), text_color=text_color, justify=justify_align)
        sender_label.pack(anchor=pack_anchor, padx=15, pady=(10, 0), fill='x')

        message_label = customtkinter.CTkLabel(bubble, text=message, font=FONT_BODY, text_color=text_color, wraplength=350, justify=justify_align)
        message_label.pack(anchor=pack_anchor, expand=True, fill="x", padx=15, pady=(0, 10))

        if is_thinking:
            self.thinking_bubble = bubble_container

        self.update_idletasks()
        self.chat_history_frame._parent_canvas.yview_moveto(1.0)

        if not is_thinking:
            self.chat_history_list.append(f"{sender}: {message}")

    def add_button_message(self, sender, message, button_text, button_command):
        pack_anchor = "w"
        justify_align = "left"
        bubble_color = "#3A3A3A"
        text_color = COLOR_TEXT

        bubble_container = customtkinter.CTkFrame(self.chat_history_frame, fg_color="transparent")
        bubble_container.pack(fill="x", padx=5, pady=0)

        bubble = customtkinter.CTkFrame(bubble_container, fg_color=bubble_color, corner_radius=15)
        bubble.pack(anchor=pack_anchor, padx=10, pady=5, ipadx=5)

        sender_label = customtkinter.CTkLabel(bubble, text=sender, font=(FONT_FAMILY, 11, "bold"), text_color=text_color, justify=justify_align)
        sender_label.pack(anchor=pack_anchor, padx=15, pady=(10, 0), fill='x')

        message_label = customtkinter.CTkLabel(bubble, text=message, font=FONT_BODY, text_color=text_color, wraplength=350, justify=justify_align)
        message_label.pack(anchor=pack_anchor, expand=True, fill="x", padx=15, pady=(0, 10))

        action_button = customtkinter.CTkButton(bubble, text=button_text, font=FONT_BUTTON, command=button_command, fg_color=COLOR_ACCENT, hover_color=COLOR_HOVER)
        action_button.pack(pady=(0, 10), padx=15)

        self.update_idletasks()
        self.chat_history_frame._parent_canvas.yview_moveto(1.0)

        self.chat_history_list.append(f"{sender}: {message} [Button: {button_text}]")

    def _send_report_to_server(self):
        payload = {
            "chat_history": self.chat_history_list,
            "discord_user_id": self.recoil_controller.settings.discord_user_id
        }
        try:
            response = requests.post(f"{NGROK_BASE_URL}/report", json=payload)
            response.raise_for_status()
            result = response.json()
            self.add_message("RecoilAI", result.get("message", "Relatório enviado com sucesso!"))
        except requests.exceptions.RequestException as e:
            self.add_message("RecoilAI", f"Erro ao enviar relatório: {e}")

    def _handle_report_authentication(self):
        authenticated = self.parent._request_pin_and_authenticate()
        if authenticated:
            self._send_report_to_server()

class PinInputDialog(customtkinter.CTkToplevel):
    def __init__(self, parent, title, prompt):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        center_window(self, 300, 150)
        self.configure(fg_color=COLOR_BACKGROUND)
        self.grab_set()
        self.focus_set()
        self.transient(parent)

        self.pin_value = None

        self.label = customtkinter.CTkLabel(self, text=prompt, font=FONT_BODY)
        self.label.pack(pady=10)

        self.entry = customtkinter.CTkEntry(self, font=FONT_BODY, width=200)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", self._on_submit)

        self.submit_button = customtkinter.CTkButton(self, text="Submit", command=self._on_submit, font=FONT_BUTTON)
        self.submit_button.pack(pady=10)

    def _on_submit(self, event=None):
        self.pin_value = self.entry.get().strip()
        self.destroy()

    def get_input(self):
        self.parent.wait_window(self)
        return self.pin_value

class AboutDialog(customtkinter.CTkToplevel):
    def __init__(self, parent=None, recoil_controller=None):
        super().__init__(parent)
        self.parent = parent
        self.recoil_controller = recoil_controller
        center_window(self, 400, 250)
        self.configure(fg_color=COLOR_BACKGROUND)
        self.update_idletasks()

        self.grab_set()
        self.focus_set()
        self.transient(parent)

        self.main_frame = customtkinter.CTkFrame(self, fg_color=COLOR_FRAME)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.title_label = customtkinter.CTkLabel(self.main_frame, text="", font=FONT_TITLE)
        self.title_label.pack(pady=(0, 5))
        self.version_label = customtkinter.CTkLabel(self.main_frame, text="", font=FONT_BODY, text_color="gray60")
        self.version_label.pack(pady=(0, 15))

        self.creator_label = customtkinter.CTkLabel(self.main_frame, text="", font=FONT_BODY)
        self.creator_label.pack(pady=5)
        
        button_checkbox_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        button_checkbox_frame.pack(pady=20, fill="x")
        button_checkbox_frame.grid_columnconfigure(0, weight=1)

        self.do_not_show_again_checkbox = customtkinter.CTkCheckBox(button_checkbox_frame, text="", font=FONT_BODY, command=self.toggle_show_on_startup)
        if self.recoil_controller and not self.recoil_controller.settings.show_about_on_startup:
            self.do_not_show_again_checkbox.select()
        else:
            self.do_not_show_again_checkbox.deselect()
        self.do_not_show_again_checkbox.grid(row=0, column=0, sticky="w")

        self.close_button = customtkinter.CTkButton(button_checkbox_frame, text="", font=FONT_BUTTON, command=self.destroy)
        self.close_button.grid(row=0, column=1, sticky="e")
        
        self.update_ui_text()

    def _(self, key, **kwargs):
        if self.parent:
            return self.parent._(key, **kwargs)
        return key

    def update_ui_text(self):
        self.title(self._("about"))
        self.title_label.configure(text=self._("app_title"))
        self.version_label.configure(text=self._("version_info", __version__=__version__))
        self.creator_label.configure(text=self._("created_by"))
        self.do_not_show_again_checkbox.configure(text=self._("do_not_show_again"))
        self.close_button.configure(text=self._("close"))

    def toggle_show_on_startup(self):
        if self.recoil_controller:
            self.recoil_controller.settings.show_about_on_startup = not self.do_not_show_again_checkbox.get()
            if self.parent:
                self.parent.save_settings()

class AboutDialog(customtkinter.CTkToplevel):
    def __init__(self, parent=None, recoil_controller=None):
        super().__init__(parent)
        self.parent = parent
        self.recoil_controller = recoil_controller
        center_window(self, 400, 250)
        self.configure(fg_color=COLOR_BACKGROUND)
        self.update_idletasks()

        self.grab_set()
        self.focus_set()
        self.transient(parent)

        self.main_frame = customtkinter.CTkFrame(self, fg_color=COLOR_FRAME)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.title_label = customtkinter.CTkLabel(self.main_frame, text="", font=FONT_TITLE)
        self.title_label.pack(pady=(0, 5))
        self.version_label = customtkinter.CTkLabel(self.main_frame, text="", font=FONT_BODY, text_color="gray60")
        self.version_label.pack(pady=(0, 15))

        self.creator_label = customtkinter.CTkLabel(self.main_frame, text="", font=FONT_BODY)
        self.creator_label.pack(pady=5)
        
        button_checkbox_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        button_checkbox_frame.pack(pady=20, fill="x")
        button_checkbox_frame.grid_columnconfigure(0, weight=1)

        self.do_not_show_again_checkbox = customtkinter.CTkCheckBox(button_checkbox_frame, text="", font=FONT_BODY, command=self.toggle_show_on_startup)
        if self.recoil_controller and not self.recoil_controller.settings.show_about_on_startup:
            self.do_not_show_again_checkbox.select()
        else:
            self.do_not_show_again_checkbox.deselect()
        self.do_not_show_again_checkbox.grid(row=0, column=0, sticky="w")

        self.close_button = customtkinter.CTkButton(button_checkbox_frame, text="", font=FONT_BUTTON, command=self.destroy)
        self.close_button.grid(row=0, column=1, sticky="e")
        
        self.update_ui_text()

    def _(self, key, **kwargs):
        if self.parent:
            return self.parent._(key, **kwargs)
        return key

    def update_ui_text(self):
        self.title(self._("about"))
        self.title_label.configure(text=self._("app_title"))
        self.version_label.configure(text=self._("version_info", __version__=__version__))
        self.creator_label.configure(text=self._("created_by"))
        self.do_not_show_again_checkbox.configure(text=self._("do_not_show_again"))
        self.close_button.configure(text=self._("close"))

    def toggle_show_on_startup(self):
        if self.recoil_controller:
            self.recoil_controller.settings.show_about_on_startup = not self.do_not_show_again_checkbox.get()
            if self.parent:
                self.parent.save_settings()

class RecoilControllerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.recoil_controller = RecoilController()
        self.rate_limiter = RateLimiter(rpm_limit=5, rpd_limit=200)
        self.load_settings()
        self.agent_icon_cache = {}

        if self.recoil_controller.settings.show_about_on_startup:
            self.about_dialog = AboutDialog(self, recoil_controller=self.recoil_controller)
            self.about_dialog.wait_window()

        self.overrideredirect(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.weapon_switcher = customtkinter.CTkSegmentedButton(
            self,
            values=[self._("primary"), self._("secondary")],
            command=self._switch_weapon_view,
            font=FONT_BUTTON,
            selected_color=COLOR_ACCENT,
            selected_hover_color=COLOR_HOVER
        )
        self.weapon_switcher.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.recoil_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.recoil_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.recoil_frame.grid_columnconfigure(0, weight=1)
        
        self.create_recoil_widgets()

        bottom_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        
        self.t_bag_enabled_checkbox = customtkinter.CTkCheckBox(bottom_frame, text="", font=FONT_BODY, command=self.toggle_t_bag_enabled)
        self.t_bag_enabled_checkbox.grid(row=0, column=0, columnspan=3, padx=5, pady=(5, 10), sticky="w")
        self.t_bag_enabled_checkbox.select() if self.recoil_controller.settings.t_bag_enabled else self.t_bag_enabled_checkbox.deselect()

        button_frame = customtkinter.CTkFrame(bottom_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.settings_button = customtkinter.CTkButton(button_frame, text="", font=FONT_BUTTON, command=self.open_settings)
        self.settings_button.grid(row=0, column=0, padx=5, sticky="ew")

        self.presets_button = customtkinter.CTkButton(button_frame, text="", font=FONT_BUTTON, command=self.open_presets_dialog)
        self.presets_button.grid(row=0, column=1, padx=5, sticky="ew")

        self.chat_button = customtkinter.CTkButton(button_frame, text="", font=FONT_BUTTON, command=self.open_chat)
        self.chat_button.grid(row=0, column=2, padx=5, sticky="ew")

        self.toggle_button = customtkinter.CTkButton(self, text="", command=self.toggle_recoil, height=40, font=FONT_TITLE)
        self.toggle_button.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="ew")
        self.recoil_active = False

        self.active_weapon = "primary"
        self._switch_weapon_view("Primary")

        self.update_main_ui_recoil_values()
        self.update_ui_language()

        self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press, on_release=self._on_key_release)
        self.keyboard_listener.start()

        self.pynput_mouse_listener = mouse.Listener(on_click=self._on_mouse_click, on_scroll=self._on_scroll_event)
        self.pynput_mouse_listener.start()
        
        threading.Thread(target=self._preload_agent_icons, daemon=True).start()

    def _preload_agent_icons(self):
        """Pre-loads agent icons into the cache on a background thread."""
        agent_types = ["attackers", "defenders"]
        for agent_type in agent_types:
            base_path = os.path.join(script_dir, "Agents")
            agent_path = os.path.join(base_path, agent_type)

            if not os.path.exists(agent_path):
                continue
            
            agent_files = os.listdir(agent_path)

            for filename in agent_files:
                if not filename.endswith(".png"):
                    continue

                icon_path = os.path.join(agent_path, filename)
                if icon_path not in self.agent_icon_cache:
                    try:
                        img = Image.open(icon_path)
                        icon = customtkinter.CTkImage(light_image=img, dark_image=img, size=(64, 64))
                        self.agent_icon_cache[icon_path] = icon
                        time.sleep(0.01)
                    except Exception as e:
                        print(f"Failed to pre-load icon {icon_path}: {e}")

    def create_recoil_widgets(self):
        self.recoil_y_label = customtkinter.CTkLabel(self.recoil_frame, text="", font=FONT_BODY)
        self.recoil_y_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))
        self.recoil_y_entry = customtkinter.CTkEntry(self.recoil_frame, width=80, font=FONT_BODY)
        self.recoil_y_entry.grid(row=1, column=0, sticky="w", padx=10, pady=(0,5))
        self.recoil_y_slider = customtkinter.CTkSlider(self.recoil_frame, from_=0, to=2000, number_of_steps=2000)
        self.recoil_y_slider.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,10))

        self.recoil_x_label = customtkinter.CTkLabel(self.recoil_frame, text="", font=FONT_BODY)
        self.recoil_x_label.grid(row=3, column=0, sticky="w", padx=10, pady=(5,0))
        self.recoil_x_entry = customtkinter.CTkEntry(self.recoil_frame, width=80, font=FONT_BODY)
        self.recoil_x_entry.grid(row=4, column=0, sticky="w", padx=10, pady=(0,5))
        self.recoil_x_slider = customtkinter.CTkSlider(self.recoil_frame, from_=-5000, to=5000, number_of_steps=10000)
        self.recoil_x_slider.grid(row=5, column=0, sticky="ew", padx=10, pady=(0,10))
        
        self.secondary_weapon_enabled_checkbox = customtkinter.CTkCheckBox(self.recoil_frame, text="", font=FONT_BODY, command=self.toggle_secondary_weapon_enabled)

    def _switch_weapon_view(self, weapon_type_display):
        if weapon_type_display == self._("primary"):
            self.active_weapon = "primary"
            self.recoil_controller.settings.active_weapon = "primary"
        elif weapon_type_display == self._("secondary"):
            self.active_weapon = "secondary"
            self.recoil_controller.settings.active_weapon = "secondary"
        else:
            self.active_weapon = weapon_type_display.lower()
        
        self.recoil_y_entry.unbind("<Return>")
        self.recoil_y_slider.configure(command=None)
        self.recoil_x_entry.unbind("<Return>")
        self.recoil_x_slider.configure(command=None)
        
        if self.active_weapon == "primary":
            self.recoil_y_entry.bind("<Return>", self._update_primary_recoil_y_from_entry)
            self.recoil_y_slider.configure(command=self._update_primary_recoil_y_from_slider_scaled)
            self.recoil_x_entry.bind("<Return>", self._update_primary_recoil_x_from_entry)
            self.recoil_x_slider.configure(command=self._update_primary_recoil_x_from_slider_scaled)
            self.secondary_weapon_enabled_checkbox.grid_forget()
        else:
            self.recoil_y_entry.bind("<Return>", self._update_secondary_recoil_y_from_entry)
            self.recoil_y_slider.configure(command=self._update_secondary_recoil_y_from_slider_scaled)
            self.recoil_x_entry.bind("<Return>", self._update_secondary_recoil_x_from_entry)
            self.recoil_x_slider.configure(command=self._update_secondary_recoil_x_from_slider_scaled)
            self.secondary_weapon_enabled_checkbox.grid(row=6, column=0, padx=10, pady=15, sticky="w")
            
        self.update_main_ui_recoil_values()
        
    def update_toggle_button_color(self):
        if self.recoil_active:
            self.toggle_button.configure(text=self._("enabled"), fg_color=COLOR_SUCCESS, hover_color="#0B7A0D")
        else:
            self.toggle_button.configure(text=self._("disabled"), fg_color=COLOR_DANGER, hover_color="#C82333")

    def toggle_t_bag_enabled(self):
        is_checked = self.t_bag_enabled_checkbox.get() == 1
        self.recoil_controller.settings.t_bag_enabled = is_checked
        self.recoil_controller.logger.info(f"Enable T-bag Macro: {is_checked}")
        self.save_settings()

    def toggle_secondary_weapon_enabled(self):
        is_checked = self.secondary_weapon_enabled_checkbox.get() == 1
        self.recoil_controller.settings.secondary_weapon_enabled = is_checked
        self.recoil_controller.logger.info(f"Enable Secondary Weapon: {is_checked}")
        self.save_settings()

    def _update_primary_recoil_y_from_slider_scaled(self, value):
        scaled_value = value / 100.0
        self.recoil_controller.settings.primary_recoil_y = scaled_value
        self.recoil_y_entry.delete(0, tk.END)
        self.recoil_y_entry.insert(0, f"{scaled_value:.2f}")
        if self.active_weapon == "primary":
            self.recoil_controller.set_recoil_y(scaled_value)
        self.save_settings()

    def _update_primary_recoil_x_from_slider_scaled(self, value):
        scaled_value = value / 1000.0
        self.recoil_controller.settings.primary_recoil_x = scaled_value
        self.recoil_x_entry.delete(0, tk.END)
        self.recoil_x_entry.insert(0, f"{scaled_value:.3f}")
        if self.active_weapon == "primary":
            self.recoil_controller.set_recoil_x(scaled_value)
        self.save_settings()

    def _update_secondary_recoil_y_from_slider_scaled(self, value):
        scaled_value = value / 100.0
        self.recoil_controller.settings.secondary_recoil_y = scaled_value
        self.recoil_y_entry.delete(0, tk.END)
        self.recoil_y_entry.insert(0, f"{scaled_value:.2f}")
        if self.active_weapon == "secondary":
            self.recoil_controller.set_recoil_y(scaled_value)
        self.save_settings()

    def _update_secondary_recoil_x_from_slider_scaled(self, value):
        scaled_value = value / 1000.0
        self.recoil_controller.settings.secondary_recoil_x = scaled_value
        self.recoil_x_entry.delete(0, tk.END)
        self.recoil_x_entry.insert(0, f"{scaled_value:.3f}")
        if self.active_weapon == "secondary":
            self.recoil_controller.set_recoil_x(scaled_value)
        self.save_settings()

    def _update_primary_recoil_y_from_entry(self, event):
        try:
            value = float(self.recoil_y_entry.get())
            self.recoil_controller.settings.primary_recoil_y = value
            self.recoil_y_slider.set(int(value * 100))
            if self.active_weapon == "primary":
                self.recoil_controller.set_recoil_y(value)
            self.save_settings()
        except ValueError:
            CTkMessagebox(title="Error", message="Invalid value for Primary Recoil Y. Please enter a number.", icon="cancel").get()
            self.recoil_y_entry.delete(0, tk.END)
            self.recoil_y_entry.insert(0, f"{self.recoil_controller.settings.primary_recoil_y:.2f}")

    def _update_primary_recoil_x_from_entry(self, event):
        try:
            value = float(self.recoil_x_entry.get())
            self.recoil_controller.settings.primary_recoil_x = value
            self.recoil_x_slider.set(int(value * 1000))
            if self.active_weapon == "primary":
                self.recoil_controller.set_recoil_x(value)
            self.save_settings()
        except ValueError:
            CTkMessagebox(title="Error", message="Invalid value for Primary Recoil X. Please enter a number.", icon="cancel").get()
            self.recoil_x_entry.delete(0, tk.END)
            self.recoil_x_entry.insert(0, f"{self.recoil_controller.settings.primary_recoil_x:.3f}")

    def _update_secondary_recoil_y_from_entry(self, event):
        try:
            value = float(self.recoil_y_entry.get())
            self.recoil_controller.settings.secondary_recoil_y = value
            self.recoil_y_slider.set(int(value * 100))
            if self.active_weapon == "secondary":
                self.recoil_controller.set_recoil_y(value)
            self.save_settings()
        except ValueError:
            CTkMessagebox(title="Error", message="Invalid value for Secondary Recoil Y. Please enter a number.", icon="cancel").get()
            self.recoil_y_entry.delete(0, tk.END)
            self.recoil_y_entry.insert(0, f"{self.recoil_controller.settings.secondary_recoil_y:.2f}")

    def _update_secondary_recoil_x_from_entry(self, event):
        try:
            value = float(self.recoil_x_entry.get())
            self.recoil_controller.settings.secondary_recoil_x = value
            self.recoil_x_slider.set(int(value * 1000))
            if self.active_weapon == "secondary":
                self.recoil_controller.set_recoil_x(value)
            self.recoil_controller.set_recoil_x(value)
            self.save_settings()
        except ValueError:
            CTkMessagebox(title="Error", message="Invalid value for Secondary Recoil X. Please enter a number.", icon="cancel").get()
            self.recoil_x_entry.delete(0, tk.END)
            self.recoil_x_entry.insert(0, f"{self.recoil_controller.settings.secondary_recoil_x:.3f}")

    def _on_key_press(self, key):
        if hasattr(self, 'settings_dialog') and self.settings_dialog and self.settings_dialog.winfo_exists() and self.settings_dialog.hotkey_capture_mode:
            self.settings_dialog.process_captured_key(key)
            return

        hotkey_string = self._get_key_string(key)
        self._process_hotkey(hotkey_string)

    def _on_key_release(self, key):
        if not self.recoil_active:
            return
            
        hotkey_string = self._get_key_string(key)
        if hotkey_string in self.recoil_controller.settings.t_bag_hotkey:
            if self.recoil_controller.t_bag_active:
                self.recoil_controller.stop_t_bag()

    def update_main_ui_recoil_values(self):
        if self.active_weapon == "primary":
            self.recoil_y_slider.set(int(self.recoil_controller.settings.primary_recoil_y * 100))
            self.recoil_y_entry.delete(0, tk.END)
            self.recoil_y_entry.insert(0, f"{self.recoil_controller.settings.primary_recoil_y:.2f}")

            self.recoil_x_slider.set(int(self.recoil_controller.settings.primary_recoil_x * 1000))
            self.recoil_x_entry.delete(0, tk.END)
            self.recoil_x_entry.insert(0, f"{self.recoil_controller.settings.primary_recoil_x:.3f}")

            self.recoil_controller.set_recoil_y(self.recoil_controller.settings.primary_recoil_y)
            self.recoil_controller.set_recoil_x(self.recoil_controller.settings.primary_recoil_x)
        else:
            self.recoil_y_slider.set(int(self.recoil_controller.settings.secondary_recoil_y * 100))
            self.recoil_y_entry.delete(0, tk.END)
            self.recoil_y_entry.insert(0, f"{self.recoil_controller.settings.secondary_recoil_y:.2f}")

            self.recoil_x_slider.set(int(self.recoil_controller.settings.secondary_recoil_x * 1000))
            self.recoil_x_entry.delete(0, tk.END)
            self.recoil_x_entry.insert(0, f"{self.recoil_controller.settings.secondary_recoil_x:.3f}")
            
            self.recoil_controller.set_recoil_y(self.recoil_controller.settings.secondary_recoil_y)
            self.recoil_controller.set_recoil_x(self.recoil_controller.settings.secondary_recoil_x)
        
        if hasattr(self, 'secondary_weapon_enabled_checkbox'):
            self.secondary_weapon_enabled_checkbox.select() if self.recoil_controller.settings.secondary_weapon_enabled else self.secondary_weapon_enabled_checkbox.deselect()

    def _get_key_string(self, key):
        """Converts a pynput key object to a string, handling different keyboard layouts."""
        try:
            if hasattr(key, 'vk') and key.vk is not None:
                if 96 <= key.vk <= 105:
                    return f"NUMPAD_{key.vk - 96}"
                elif 112 <= key.vk <= 123:
                    return f"F{key.vk - 111}"
                elif key.vk == 20:
                    return "CAPS_LOCK"
                elif key.vk == 162:
                    return "CTRL_L"
                elif key.vk == 163:
                    return "CTRL_R"
                elif key.vk == 160:
                    return "SHIFT_L"
                elif key.vk == 161:
                    return "SHIFT_R"
                elif key.vk == 164:
                    return "ALT_L"
                elif key.vk == 165:
                    return "ALT_R"
                elif key.vk == 8:
                    return "BACKSPACE"
                elif key.vk == 9:
                    return "TAB"
                elif key.vk == 13:
                    return "ENTER"
                elif key.vk == 27:
                    return "ESC"
                elif key.vk == 32:
                    return "SPACE"
                elif key.vk == 45:
                    return "INSERT"
                elif key.vk == 46:
                    return "DELETE"
                elif key.vk == 36:
                    return "HOME"
                elif key.vk == 35:
                    return "END"
                elif key.vk == 33:
                    return "PAGE_UP"
                elif key.vk == 34:
                    return "PAGE_DOWN"
                elif key.vk == 37:
                    return "LEFT"
                elif key.vk == 38:
                    return "UP"
                elif key.vk == 39:
                    return "RIGHT"
                elif key.vk == 40:
                    return "DOWN"
                
                if hasattr(key, 'char') and key.char is not None:
                    return str(key.char).upper()
                else:
                    return str(key).replace('Key.', '').upper()
            else:
                if hasattr(key, 'char') and key.char is not None:
                    return str(key.char).upper()
                else:
                    return str(key).replace('Key.', '').upper()
        except AttributeError:
            return str(key).replace('Key.', '').upper()

    def _get_mouse_hotkey_string(self, button):
        """Converts a mouse button event to a hotkey string."""
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
        
        if self.recoil_controller.t_bag_active:
            self.recoil_controller.stop_t_bag()
            self.recoil_controller.logger.info("T-bag stopped due to mouse click.")


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
        self.recoil_controller.logger.info("Settings dialog closed. Re-registering hotkeys.")
        self.save_settings()

    def open_presets_dialog(self):
        self.presets_dialog = PresetsDialog(self.recoil_controller, self, self.agent_icon_cache)
        self.presets_dialog.grab_set()
        self.presets_dialog.wait_window()

    def open_chat(self):
        chat_dialog = ChatDialog(self)
        chat_dialog.grab_set()
        chat_dialog.wait_window()

    def _request_pin_and_authenticate(self):
        pin_dialog = PinInputDialog(self, self._("pin_dialog_title"), self._("enter_pin_prompt"))
        pin = pin_dialog.get_input()

        if pin:
            try:
                response = requests.post(f"{NGROK_BASE_URL}/check-pin", json={"pin": pin})
                response.raise_for_status()
                result = response.json()

                if result.get("success"):
                    self.recoil_controller.settings.discord_user_id = result.get("discord_user_id")
                    self.save_settings()
                    CTkMessagebox(title=self._("success"), message="Autenticação bem-sucedida!", icon="info").get()
                    return True
                else:
                    CTkMessagebox(title=self._("error"), message=result.get("message", "PIN inválido ou já utilizado."), icon="cancel").get()
                    return False
            except requests.exceptions.RequestException as e:
                CTkMessagebox(title=self._("error"), message=f"Erro de comunicação com o servidor: {e}", icon="cancel").get()
                return False
        return False

    def load_settings(self):
        settings_path = os.path.join(CONFIG_DIR, "settings.cfg")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    loaded_settings_dict = json.load(f)
                self.recoil_controller.settings = self.recoil_controller.settings.from_dict(loaded_settings_dict)
                
                self.recoil_controller.settings.language = loaded_settings_dict.get("language", "en")
                self.recoil_controller.settings.discord_user_id = loaded_settings_dict.get("discord_user_id", None)

                self.recoil_controller.logger.info("Settings loaded successfully.")
                self.recoil_controller.logger.info(f"Loaded Settings: Sensitivity={self.recoil_controller.settings.sensitivity}, Smoothing Factor={self.recoil_controller.settings.smoothing_factor}")
            except Exception as e:
                self.recoil_controller.logger.error(f"Error loading settings: {e}")
        else:
            if not hasattr(self.recoil_controller.settings, 'language'):
                self.recoil_controller.settings.language = "en"
            self.recoil_controller.logger.info("settings.cfg not found. Using default settings.")

    def save_settings(self):
        settings_path = os.path.join(CONFIG_DIR, "settings.cfg")
        try:
            settings_dict = self.recoil_controller.settings.to_dict()
            if hasattr(self.recoil_controller.settings, 'language'):
                settings_dict['language'] = self.recoil_controller.settings.language
            else:
                settings_dict['language'] = 'en'
            
            settings_dict['discord_user_id'] = self.recoil_controller.settings.discord_user_id

            with open(settings_path, 'w') as f:
                json.dump(settings_dict, f, indent=4)
            self.recoil_controller.logger.info("Settings saved successfully.")
        except Exception as e:
            self.recoil_controller.logger.error(f"Error saving settings: {e}")

    def toggle_script_running(self):
        if self.recoil_controller.script_running:
            self.recoil_controller.stop()
            self.recoil_active = False
            print("Main script DISABLED")
        else:
            self.recoil_controller.start()
            self.recoil_active = True
            print("Main script ENABLED")
        self.update_toggle_button_color()

    def toggle_recoil(self):
        if self.recoil_active:
            self.recoil_controller.stop()
            self.recoil_active = False
            self.recoil_controller.logger.info("Recoil Disabled.")
        else:
            self.recoil_controller.start()
            self.recoil_active = True
            self.recoil_controller.logger.info("Recoil Enabled.")
        self.update_toggle_button_color()

    

    def process_ai_response(self, ai_response, chat_dialog):
        chat_dialog.add_message("RecoilAI", ai_response.get("response_text", ""))
        new_settings = ai_response.get("new_settings")
        ui_actions = ai_response.get("ui_actions", [])
        
        current_rpm_used = ai_response.get("current_rpm", 0)
        current_rpd_used = ai_response.get("current_rpd", 0)
        
        rpm_remaining = 5 - current_rpm_used
        rpd_remaining = 100 - current_rpd_used

        chat_dialog.rpm_label.configure(text=f"RPM {rpm_remaining}/5")
        chat_dialog.rpd_label.configure(text=f"RPD {rpd_remaining}/100")

        if new_settings:
            for setting_key, setting_value in new_settings.items():
                if setting_key == "t_bag_key":
                    setattr(self.recoil_controller.settings, setting_key, str(setting_value))
                elif isinstance(setting_value, bool):
                    setattr(self.recoil_controller.settings, setting_key, bool(setting_value))
                elif isinstance(setting_value, (int, float)):
                    setattr(self.recoil_controller.settings, setting_key, float(setting_value))
                else:
                    setattr(self.recoil_controller.settings, setting_key, setting_value)
            
            self.update_main_ui_recoil_values()
            self.save_settings()
            if hasattr(self, 'settings_dialog') and self.settings_dialog and self.settings_dialog.winfo_exists():
                self.settings_dialog.update_ui_text()
                self.settings_dialog.update_settings()
            if hasattr(self, 't_bag_enabled_checkbox'):
                self.t_bag_enabled_checkbox.select() if self.recoil_controller.settings.t_bag_enabled else self.t_bag_enabled_checkbox.deselect()
            if hasattr(self, 'secondary_weapon_enabled_checkbox'):
                self.secondary_weapon_enabled_checkbox.select() if self.recoil_controller.settings.secondary_weapon_enabled else self.secondary_weapon_enabled_checkbox.deselect()

        for action_data in ui_actions:
            action_type = action_data.get("action")
            params = action_data.get("params", {})
            self._perform_ui_action(action_type, params)

        chat_dialog.send_button.configure(state="normal")

    def _perform_ui_action(self, action_type, params):
        if action_type == "save_preset":
            agent_name = params.get("agent_name")
            preset_name = params.get("preset_name")
            if agent_name and preset_name:
                self._perform_save_preset(agent_name, preset_name)
        elif action_type == "load_preset":
            agent_name = params.get("agent_name")
            preset_name = params.get("preset_name")
            if agent_name and preset_name:
                self._perform_load_preset(agent_name, preset_name)
        elif action_type == "toggle_tbag_macro":
            enabled = params.get("enabled")
            if enabled is not None:
                self._perform_toggle_tbag_macro(enabled)
        elif action_type == "toggle_secondary_weapon":
            enabled = params.get("enabled")
            if enabled is not None:
                self._perform_toggle_secondary_weapon(enabled)
        elif action_type == "delete_preset":
            agent_name = params.get("agent_name")
            preset_name = params.get("preset_name")
            if agent_name and preset_name:
                self._perform_delete_preset(agent_name, preset_name)
        elif action_type == "toggle_recoil_state":
            enabled = params.get("enabled")
            if enabled is not None:
                self.toggle_recoil()
        else:
            logging.warning(f"Unknown UI action: {action_type}")

    def _perform_save_preset(self, agent_name, preset_name):
        agent_presets_dir = os.path.join(CONFIG_DIR, "presets", agent_name.lower().replace(" ", "_"))
        os.makedirs(agent_presets_dir, exist_ok=True)

        preset_file_path = os.path.join(agent_presets_dir, f"{preset_name}.json")

        settings_to_save = {
            "primary_recoil_y": self.recoil_controller.settings.primary_recoil_y,
            "primary_recoil_x": self.recoil_controller.settings.primary_recoil_x,
            "secondary_recoil_y": self.recoil_controller.settings.secondary_recoil_y,
            "secondary_recoil_x": self.recoil_controller.settings.secondary_recoil_x,
            "secondary_weapon_enabled": self.recoil_controller.settings.secondary_weapon_enabled,
        }

        try:
            with open(preset_file_path, 'w') as f:
                json.dump(settings_to_save, f, indent=4)
            CTkMessagebox(title=self._("success"), message=self._("preset_saved_successfully", preset_name=preset_name, agent_name=agent_name), icon="info").get()
            if hasattr(self, 'presets_dialog') and self.presets_dialog and self.presets_dialog.winfo_exists():
                self.presets_dialog.populate_presets_combobox()
        except Exception as e:
            CTkMessagebox(title=self._("error"), message=self._("error_saving_preset", e=e), icon="cancel").get()
        logging.info(f"AI requested saving preset '{preset_name}' for {agent_name}")

    def _perform_load_preset(self, agent_name, preset_name):
        agent_presets_dir = os.path.join(CONFIG_DIR, "presets", agent_name.lower().replace(" ", "_"))
        preset_file_path = os.path.join(agent_presets_dir, f"{preset_name}.json")

        if not os.path.exists(preset_file_path):
            CTkMessagebox(title=self._("error"), message=self._("preset_not_found", preset_file_path=preset_file_path), icon="cancel").get()
            return

        try:
            with open(preset_file_path, 'r') as f:
                loaded_settings = json.load(f)
            
            self.recoil_controller.settings.primary_recoil_y = loaded_settings.get("primary_recoil_y", 0.0)
            self.recoil_controller.settings.primary_recoil_x = loaded_settings.get("primary_recoil_x", 0.0)
            self.recoil_controller.settings.secondary_recoil_y = loaded_settings.get("secondary_recoil_y", 0.0)
            self.recoil_controller.settings.secondary_recoil_x = loaded_settings.get("secondary_recoil_x", 0.0)
            self.recoil_controller.settings.secondary_weapon_enabled = loaded_settings.get("secondary_weapon_enabled", False)

            self.update_main_ui_recoil_values()
            self.save_settings()

            CTkMessagebox(title=self._("success"), message=self._("preset_loaded_successfully", selected_preset=preset_name, agent_name=agent_name), icon="info").get()
            if hasattr(self, 'presets_dialog') and self.presets_dialog and self.presets_dialog.winfo_exists():
                self.presets_dialog.populate_presets_combobox()
        except Exception as e:
            CTkMessagebox(title=self._("error"), message=self._("error_loading_preset", e=e), icon="cancel").get()
        logging.info(f"AI requested loading preset '{preset_name}' for {agent_name}")

    def _perform_toggle_tbag_macro(self, enabled):
        self.recoil_controller.settings.t_bag_enabled = enabled
        self.t_bag_enabled_checkbox.select() if enabled else self.t_bag_enabled_checkbox.deselect()
        self.save_settings()
        logging.info(f"AI requested T-bag macro {'enabled' if enabled else 'disabled'}")

    def _perform_toggle_secondary_weapon(self, enabled):
        self.recoil_controller.settings.secondary_weapon_enabled = enabled
        if self.active_weapon == "secondary":
            self.secondary_weapon_enabled_checkbox.select() if enabled else self.secondary_weapon_enabled_checkbox.deselect()
        self.save_settings()
        logging.info(f"AI requested secondary weapon {'enabled' if enabled else 'disabled'}")

    def _perform_delete_preset(self, agent_name, preset_name):
        agent_presets_dir = os.path.join(CONFIG_DIR, "presets", agent_name.lower().replace(" ", "_"))
        preset_file_path = os.path.join(agent_presets_dir, f"{preset_name}.json")

        if not os.path.exists(preset_file_path):
            CTkMessagebox(title=self._("error"), message=self._("preset_not_found", preset_file_path=preset_file_path), icon="cancel").get()
            return

        try:
            os.remove(preset_file_path)
            CTkMessagebox(title=self._("success"), message=self._("preset_deleted_successfully", selected_preset=preset_name), icon="info").get()
            if hasattr(self, 'presets_dialog') and self.presets_dialog and self.presets_dialog.winfo_exists():
                self.presets_dialog.populate_presets_combobox()
        except Exception as e:
            CTkMessagebox(title=self._("error"), message=self._("error_deleting_preset", e=e), icon="cancel").get()
        logging.info(f"AI requested deleting preset '{preset_name}' for {agent_name}")

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
        if hotkey_string == 'F6':
            self.toggle_recoil()
            return
        if hotkey_string == 'F7':
            self.open_settings()
            return
        if hotkey_string == 'F8':
            self.toggle_script_running()
            return

        if not self.recoil_active:
            return

        if hotkey_string in self.recoil_controller.settings.primary_weapon_hotkey or hotkey_string in self.recoil_controller.settings.primary_weapon_hotkey_2:
            self.active_weapon = "primary"
            self.recoil_controller.settings.active_weapon = "primary"
            self.recoil_controller.active_weapon = "primary"
            self.recoil_controller.base_recoil_y = self.recoil_controller.settings.primary_recoil_y
            self.recoil_controller.base_recoil_x = self.recoil_controller.settings.primary_recoil_x
            self.update_main_ui_recoil_values()
            self.recoil_controller.logger.info(f"Primary weapon activated by hotkey: {hotkey_string}. Slider values now control primary recoil.")

        elif hotkey_string in self.recoil_controller.settings.secondary_weapon_hotkey or             hotkey_string in self.recoil_controller.settings.secondary_weapon_hotkey_2:
            if self.recoil_controller.settings.secondary_weapon_enabled:
                self.active_weapon = "secondary"
                self.recoil_controller.settings.active_weapon = "secondary"
                self.recoil_controller.active_weapon = "secondary"
                self.recoil_controller.base_recoil_y = self.recoil_controller.settings.secondary_recoil_y
                self.recoil_controller.base_recoil_x = self.recoil_controller.settings.secondary_recoil_x
                self.update_main_ui_recoil_values()
                self.recoil_controller.logger.info(f"Secondary weapon activated by hotkey: {hotkey_string}. Slider values now control secondary recoil.")
            else:
                self.recoil_controller.logger.warning(f"Secondary weapon disabled in settings. Hotkey {hotkey_string} ignored.")

        elif hotkey_string in self.recoil_controller.settings.t_bag_hotkey:
            if self.recoil_controller.settings.t_bag_enabled:
                if not self.recoil_controller.t_bag_active:
                    self.recoil_controller.start_t_bag()

    def _(self, key, **kwargs):
        """Gets a translation from the current language dictionary."""
        lang_dict = TRANSLATIONS.get(self.recoil_controller.settings.language, TRANSLATIONS["en"])
        return lang_dict.get(key, key).format(**kwargs)

    def update_ui_language(self):
        """Updates all UI text elements to the currently selected language."""
        self.title(self._("app_title"))
        self.configure(fg_color=COLOR_BACKGROUND)

        self.weapon_switcher.configure(values=[self._("primary"), self._("secondary")])
        self.weapon_switcher.set(self._(self.active_weapon))
        self.recoil_y_label.configure(text=self._("vertical_recoil"))
        self.recoil_x_label.configure(text=self._("horizontal_recoil"))
        self.secondary_weapon_enabled_checkbox.configure(text=self._("enable_secondary_weapon"))
        self.t_bag_enabled_checkbox.configure(text=self._("enable_tbag_macro"))
        self.settings_button.configure(text=self._("settings"))
        self.presets_button.configure(text=self._("presets"))
        self.chat_button.configure(text=self._("ask_ai_button"))
        
        self.update_toggle_button_color()


if __name__ == '__main__':
    customtkinter.set_appearance_mode("Dark")
    customtkinter.set_default_color_theme("blue")

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    run_update_check_and_exit_if_needed()
    
    app = RecoilControllerApp()
    
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
