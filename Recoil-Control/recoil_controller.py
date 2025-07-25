"""
Módulo RecoilController
Este módulo contém as classes para controle do mouse, escuta de eventos do mouse,
configurações de recoil e o controlador principal do sistema de recoil.
"""

import logging
import threading
import time
import ctypes
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Literal
import socket
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

import numpy as np
import win32api
import win32con
import win32gui
import random
from pynput import mouse, keyboard
from pynput.mouse import Button, Listener
from scipy.interpolate import CubicSpline

KEY_MAP = {
    'TAB': win32con.VK_TAB,
    'ENTER': win32con.VK_RETURN,
    'CTRL': win32con.VK_CONTROL,
    'CTRL_L': win32con.VK_LCONTROL,
    'CTRL_R': win32con.VK_RCONTROL,
    'SHIFT': win32con.VK_SHIFT,
    'SHIFT_L': win32con.VK_LSHIFT,
    'SHIFT_R': win32con.VK_RSHIFT,
    'ALT': win32con.VK_MENU,
    'ALT_L': win32con.VK_LMENU,
    'ALT_R': win32con.VK_RMENU,
    'CAPS_LOCK': win32con.VK_CAPITAL,
    'ESC': win32con.VK_ESCAPE,
    'SPACE': win32con.VK_SPACE,
    'LEFT': win32con.VK_LEFT,
    'UP': win32con.VK_UP,
    'RIGHT': win32con.VK_RIGHT,
    'DOWN': win32con.VK_DOWN,
    'DELETE': win32con.VK_DELETE,
    'BACKSPACE': win32con.VK_BACK,
    'INSERT': win32con.VK_INSERT,
    'HOME': win32con.VK_HOME,
    'END': win32con.VK_END,
    'PAGE_UP': win32con.VK_PRIOR,
    'PAGE_DOWN': win32con.VK_NEXT,
    **{f'F{i}': getattr(win32con, f'VK_F{i}') for i in range(1, 13)},
    **{f'NUMPAD_{i}': getattr(win32con, f'VK_NUMPAD{i}') for i in range(10)},
}


class MouseController:
    """Controlador do mouse usando win32api"""
    
    def __init__(self):
        self.position = (0, 0)
        self._remainder_x = 0.0
        self._remainder_y = 0.0
        self.update_position()
    
    def update_position(self):
        """Atualiza posição atual do mouse"""
        self.position = win32gui.GetCursorPos()
    
    def move(self, dx, dy):
        """Move o mouse relativamente, acumulando movimentos fracionários."""
        self._remainder_x += dx
        self._remainder_y += dy

        int_dx = int(self._remainder_x)
        int_dy = int(self._remainder_y)

        if int_dx != 0 or int_dy != 0:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int_dx, int_dy)
            self._remainder_x -= int_dx
            self._remainder_y -= int_dy
        self.update_position()
    
    def move_to(self, x, y):
        """Move o mouse para posição absoluta"""
        win32api.SetCursorPos((int(x), int(y)))
        self.update_position()

class MouseListener:
    """Listener para eventos do mouse"""
    
    def __init__(self, callback_on_click=None, callback_on_move=None):
        self.callback_on_click = callback_on_click
        self.callback_on_move = callback_on_move
        self.listener = None
        self.is_listening = False
    
    def start_listening(self):
        """Inicia o listener"""
        if not self.is_listening:
            self.listener = Listener(
                on_click=self._on_click,
                on_move=self._on_move
            )
            self.listener.start()
            self.is_listening = True
    
    def stop_listening(self):
        """Para o listener"""
        if self.is_listening and self.listener:
            self.listener.stop()
            self.is_listening = False
    
    def _on_click(self, x, y, button, pressed):
        """Callback para cliques do mouse"""
        if self.callback_on_click:
            self.callback_on_click(x, y, button, pressed)
    
    def _on_move(self, x, y):
        """Callback para movimento do mouse"""
        if self.callback_on_move:
            self.callback_on_move(x, y)

class RecoilSettings:
    """Configurações do sistema de recoil"""
    
    def __init__(self):
        self.language = "en"
        self.discord_user_id: Optional[str] = None
        self.shoot_delay = 0.01
        self.max_shots = 1000
        self.smoothing_factor: float = 0.5
        self.sensitivity: float = 1.0

        self.max_movement: int = 500
        self.timeout = 30

        self.primary_weapon_hotkey: List[str] = ['F9']
        self.primary_weapon_hotkey_2: List[str] = []
        self.secondary_weapon_hotkey: List[str] = ['F10']
        self.secondary_weapon_hotkey_2: List[str] = []

        self.primary_recoil_y = 0.0
        self.primary_recoil_x = 0.0
        self.secondary_recoil_y = 0.0
        self.secondary_recoil_x = 0.0

        self.secondary_weapon_enabled = False
        self.show_about_on_startup = True

        self.t_bag_hotkey: List[str] = ['F11']
        self.t_bag_enabled: bool = False
        self.t_bag_delay: float = 0.05
        self.t_bag_key: str = 'C'
        self.active_weapon: str = 'primary'


    def to_dict(self):
        """Converts settings to a dictionary for serialization."""
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data):
        """Creates a RecoilSettings instance from a dictionary."""
        settings = cls()
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        return settings

class RecoilController:
    """Main controller for the recoil system"""
    
    def __init__(self):
        self.settings = RecoilSettings()
        self.mouse_controller = MouseController()
        self.mouse_listener = MouseListener(
            callback_on_click=self._on_mouse_click,
            callback_on_move=self._on_mouse_move
        )
        
        self.script_running = False
        self.lbutton_held = False
        self.rbutton_held = False
        self.current_agent = "default"
        self.current_scope = "default"
        self.current_factor = 1.0

        self.base_recoil_x = 0.0
        self.base_recoil_y = 0.0 
        self._recoil_lock = threading.Lock()
        
        self._recoil_correction_thread = None 
        self._t_bag_thread = None
        self.t_bag_active = False
        
        self.shot_count = 0
        self.active_weapon = "primary"

        self.session_stats = {
            'total_shots': 0,
            'total_corrections': 0,
            'session_start': time.time()
        }
        self._last_correction = (0.0, 0.0)
        
        self.logger = logging.getLogger(__name__)

    def _get_key_string(self, key):
        """Converts a pynput key object to a string."""
        try:
            return key.char.upper()
        except AttributeError:
            return str(key).replace('Key.', '').upper()

    def set_recoil_x(self, recoil_x):
        self.base_recoil_x = recoil_x

    def set_recoil_y(self, value: float):
        """Updates the active vertical recoil value (base_recoil_y)."""
        with self._recoil_lock:
            self.base_recoil_y = value
            self.logger.info(f"[RecoilController] Active Recoil Y updated to: {value:.2f}")
        
    def start(self):
        """Starts the system."""
        self.script_running = True
        self.logger.info("[RecoilController] Starting mouse listener...")
        self.mouse_listener.start_listening()
        self.logger.info("[RecoilController] Recoil system started.")
        
    def stop(self):
        """Stops the system."""
        self.script_running = False
        self.logger.info("[RecoilController] Stopping mouse listener...")
        self.mouse_listener.stop_listening()
        self.logger.info("[RecoilController] Recoil system stopped.")
        
    def _on_mouse_click(self, x, y, button, pressed):
        """Callback for mouse clicks"""
        self.logger.info(f"[RecoilController] Mouse click: {button} - Pressed: {pressed}");
        if button == Button.right:
            self.rbutton_held = pressed
            self.logger.debug(f"[RecoilController] Right button: {self.rbutton_held}");
        elif button == Button.left:
            self.lbutton_held = pressed
            self.logger.debug(f"[RecoilController] Left button: {self.lbutton_held}");
            
        if self.rbutton_held and self.lbutton_held:
            if not (self._recoil_correction_thread and self._recoil_correction_thread.is_alive()):
                self.logger.info("[RecoilController] Both buttons (right and left) pressed. Starting recoil correction...")
                self._start_recoil_correction()
        elif not (self.rbutton_held and self.lbutton_held):
            if self._recoil_correction_thread and self._recoil_correction_thread.is_alive():
                self.logger.info("[RecoilController] One of the buttons (right or left) released. Stopping recoil correction...")
                self._stop_recoil_correction()
    
    def _on_mouse_move(self, x, y):
        """Callback for mouse movement"""
        self.mouse_controller.update_position()

    
    def _get_eased_progress(self, current_shot, max_shots, speed):
        """Calculates eased progress along the path based on speed."""
        if current_shot > max_shots:
            current_shot = max_shots
        progress = float(current_shot) / float(max_shots)

        if speed == 1.0:
            return progress

        if speed > 1.0:
            return 1.0 - (1.0 - progress) ** speed
        else:
            exponent = 1.0 / speed
            return progress ** exponent

    def _start_recoil_correction(self):
        """Starts recoil correction"""
        if not self._recoil_correction_thread or not self._recoil_correction_thread.is_alive():
            self.logger.info("[RecoilController] Starting recoil correction thread.")
            self.script_running = True
            self.shot_count = 0
            self.previous_cumulative_y = 0.0
            self.previous_cumulative_x = 0.0
            self.correction_start_time = time.time()
            self.horizontal_shot_count = 0
            self.horizontal_started = False
            self._recoil_correction_thread = threading.Thread(target=self._recoil_correction_loop, daemon=True)
            self._recoil_correction_thread.start()
        else:
            self.logger.info("[RecoilController] Recoil correction thread is already active.")

    def _stop_recoil_correction(self):
        """Stops recoil correction"""
        self.logger.info("[RecoilController] Stopping recoil correction thread.")
        self.script_running = False

    def _recoil_correction_loop(self):
        """Recoil correction loop"""
        self.logger.info("[RecoilController] Recoil correction loop started.")
        try:
            while self.script_running and self.rbutton_held and self.lbutton_held:
                self.shot_count += 1
                self.logger.debug(f"[RecoilController] Shot Count: {self.shot_count}")

                with self._recoil_lock:
                    recoil_y = self.base_recoil_y
                    recoil_x = self.base_recoil_x

                if recoil_y != 0 or recoil_x != 0:
                    dx, dy = self.get_adjusted_recoil(self.settings.sensitivity, recoil_x, recoil_y)

                    dx = max(-self.settings.max_movement, min(self.settings.max_movement, dx))
                    dy = max(-self.settings.max_movement, min(self.settings.max_movement, dy))
                    
                    if abs(dx) > 0.01 or abs(dy) > 0.01:
                        self.mouse_controller.move(dx, dy)
                        self._last_correction = (dx, dy)
                        self.logger.debug(f"[RecoilController] Applying correction: dx={dx:.2f}, dy={dy:.2f}")

                time.sleep(self.settings.shoot_delay)
        except Exception as e:
            self.logger.error(f"[RecoilController] Unexpected error in recoil correction loop: {e}")
        finally:
            self.logger.info("[RecoilController] Recoil correction loop ended.")

    def start_t_bag(self):
        if not self.settings.t_bag_enabled:
            return
        
        if not self.t_bag_active:
            self.t_bag_active = True
            if not self._t_bag_thread or not self._t_bag_thread.is_alive():
                self._t_bag_thread = threading.Thread(target=self._t_bag_loop, daemon=True)
                self._t_bag_thread.start()
                self.logger.info("T-bag thread started.")

    def stop_t_bag(self):
        if self.t_bag_active:
            self.t_bag_active = False
            self.logger.info("T-bag thread stopped.")

    def _t_bag_loop(self):
        key_str = self.settings.t_bag_key.upper()
        vk_code = KEY_MAP.get(key_str)

        if vk_code is None:
            try:
                vk_code = win32api.VkKeyScan(key_str[0]) & 0xff
            except Exception:
                self.logger.error(f"Could not get virtual key code for T-bag key: {key_str}")
                vk_code = win32con.VK_C

        if vk_code is None:
             self.logger.error(f"Could not determine vk_code for {key_str}, defaulting to C")
             vk_code = win32con.VK_C

        while self.t_bag_active:
            scan_code = win32api.MapVirtualKey(vk_code, 0)
            win32api.keybd_event(vk_code, scan_code, 0, 0)
            time.sleep(self.settings.t_bag_delay)
            win32api.keybd_event(vk_code, scan_code, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(self.settings.t_bag_delay)

    def get_adjusted_recoil(self, factor: float, recoil_x: float, recoil_y: float) -> Tuple[float, float]:
        """Calculates adjusted recoil correction using provided recoil_x and recoil_y."""
        
        adjusted_horizontal = recoil_x * factor
        adjusted_vertical = recoil_y * factor
        
        self._last_correction = (adjusted_horizontal, adjusted_vertical)
        
        adjusted_horizontal = max(-self.settings.max_movement, 
                                min(self.settings.max_movement, adjusted_horizontal))
        adjusted_vertical = max(-self.settings.max_movement, 
                              min(self.settings.max_movement, adjusted_vertical))
        
        return (adjusted_horizontal, adjusted_vertical)

    def get_sensitivity_adjusted_recoil(self, recoil_value):
        """Applies sensitivity scaling to a raw recoil value."""
        dpi_factor = 800 / self.settings.mouse_dpi 
        game_sens_factor = 5.0 / self.settings.game_sensitivity

        adjusted_value = recoil_value * dpi_factor * self.settings.sensitivity
        
        return adjusted_value

    def move_mouse(self, dx, dy):
        if not self.script_running:
            return

        scaled_dx = self.get_sensitivity_adjusted_recoil(dx)
        scaled_dy = self.get_sensitivity_adjusted_recoil(dy)

        current_x, current_y = win32api.GetCursorPos()
        new_x = int(current_x + scaled_dx)
        new_y = int(current_y + scaled_dy)

        max_movement = self.settings.max_movement
        if max_movement > 0:
            if abs(new_x - current_x) > max_movement:
                new_x = current_x + max_movement if new_x > current_x else current_x - max_movement
            if abs(new_y - current_y) > max_movement:
                new_y = current_y + max_movement if new_y > current_y else current_y - max_movement

        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, new_x - current_x, new_y - current_y, 0, 0)

    def set_agent_scope(self, agent: str, scope: str):
        """Sets the current agent and scope."""
        self.current_agent = agent
        self.current_scope = scope
        self.logger.info(f"Agent set to: {agent}, Scope set to: {scope}")

    def get_session_stats(self) -> Dict:
        """Returns current session statistics."""
        return {
            'total_shots': self.session_stats['total_shots'],
            'total_corrections': self.session_stats['total_corrections'],
            'session_duration': time.time() - self.session_stats['session_start'],
            'current_factor': self.current_factor
        }

def run_recoil_controller_standalone():
    import os
    controller = RecoilController()
    controller.start()
    controller.logger.info(f"RecoilController started. PID: {os.getpid()}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
        logging.info("RecoilController stopped via KeyboardInterrupt.")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='recoil_controller.log',
        filemode='w'
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)

    run_recoil_controller_standalone()
