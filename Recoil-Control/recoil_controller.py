"""
Módulo RecoilController
Este módulo contém as classes para controle do mouse, escuta de eventos do mouse,
configurações de recoil e o controlador principal do sistema de recoil.
"""

import logging
import threading
import time
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

from pynput import mouse
from pynput.mouse import Button, Listener
from scipy import signal
from scipy.stats import pearsonr

# Disable specific pylint warnings for win32 modules that may not be fully analyzable
# pylint: disable=E1101, C0103

class MouseController:
    """Controlador do mouse usando win32api"""
    
    def __init__(self):
        self.position = (0, 0)
        self._remainder_x = 0.0 # Inicializa acumulador para movimentos fracionários em X
        self._remainder_y = 0.0 # Inicializa acumulador para movimentos fracionários em Y
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
            # self.logger.debug(f"[MouseController] Movimento efetivo: dx={int_dx}, dy={int_dy}")
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
        self.shoot_delay = 0.01  # Delay between corrections
        self.max_shots = 1000    # Maximum shots per burst
        self.smoothing_factor: float = 0.5
        self.sensitivity: float = 1.0

        self.max_movement: int = 500
        self.timeout = 30        # Timeout for operations

        # Hotkey settings (new)
        self.primary_weapon_hotkey: List[str] = ['F9'] # Example: F9 for primary weapon
        self.primary_weapon_hotkey_2: List[str] = [] # Second hotkey for primary weapon
        self.secondary_weapon_hotkey: List[str] = ['F10'] # Example: F10 for secondary weapon
        self.secondary_weapon_hotkey_2: List[str] = [] # Second hotkey for secondary weapon

        # Persistent recoil values for primary and secondary weapons
        self.primary_recoil_y = 0.0
        self.primary_recoil_x = 0.0
        self.secondary_recoil_y = 0.0
        self.secondary_recoil_x = 0.0

        # Option to enable/disable secondary weapon
        self.secondary_weapon_enabled = False


    def to_dict(self):
        """Converte as configurações para um dicionário para serialização."""
        return {
            "shoot_delay": self.shoot_delay,
            "max_shots": self.max_shots,
            "smoothing_factor": self.smoothing_factor,
            "sensitivity": self.sensitivity,
            "max_movement": self.max_movement,
            "timeout": self.timeout,
            "primary_weapon_hotkey": self.primary_weapon_hotkey,
            "primary_weapon_hotkey_2": self.primary_weapon_hotkey_2,
            "secondary_weapon_hotkey": self.secondary_weapon_hotkey,
            "secondary_weapon_hotkey_2": self.secondary_weapon_hotkey_2,
            "secondary_weapon_enabled": self.secondary_weapon_enabled,
        }

    @classmethod
    def from_dict(cls, data):
        """Cria uma instância de RecoilSettings a partir de um dicionário."""
        settings = cls()
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        return settings

class RecoilController:
    """Controlador principal do sistema de recoil"""
    
    def __init__(self):
        self.settings = RecoilSettings()
        self.mouse_controller = MouseController()
        self.mouse_listener = MouseListener(
            callback_on_click=self._on_mouse_click,
            callback_on_move=self._on_mouse_move
        )
        
        # Estado do sistema
        self.script_running = False
        self.lbutton_held = False
        self.rbutton_held = False
        self.current_agent = "default"
        self.current_scope = "default"
        self.current_factor = 1.0

        # Valores base para recoil horizontal e vertical (os valores ATIVOS atualmente)
        self.base_recoil_x = 0.0
        self.base_recoil_y = 0.0 
        self._recoil_lock = threading.Lock() # Adicionar lock para acesso thread-safe
        
        # Inicializar a thread de correção de recoil
        self._recoil_correction_thread = None 
        
        # Analytics
        self.shot_count = 0
        self.session_stats = {
            'total_shots': 0,
            'total_corrections': 0,
            'session_start': time.time()
        }
        self._last_correction = (0.0, 0.0) # Inicializa _last_correction
        
        # Logger
        self.logger = logging.getLogger(__name__)

    def set_recoil_x(self, value: float):
        """Atualiza o valor do recoil horizontal que está sendo ativamente aplicado (base_recoil_x)."""
        with self._recoil_lock:
            self.base_recoil_x = value
            self.logger.info(f"[RecoilController] Recoil X ativo atualizado para: {value:.2f}")

    def set_recoil_y(self, value: float):
        """Atualiza o valor do recoil vertical que está sendo ativamente aplicado (base_recoil_y)."""
        with self._recoil_lock:
            self.base_recoil_y = value
            self.logger.info(f"[RecoilController] Recoil Y ativo atualizado para: {value:.2f}")
        
    def start(self):
        """Inicia o sistema"""
        self.script_running = True
        self.logger.info("[RecoilController] Iniciando listener do mouse...")
        self.mouse_listener.start_listening()
        self.logger.info("[RecoilController] Sistema de recoil iniciado.")
        
    def stop(self):
        """Para o sistema"""
        self.script_running = False
        self.logger.info("[RecoilController] Parando listener do mouse...")
        self.mouse_listener.stop_listening()
        self.logger.info("[RecoilController] Sistema de recoil parado.")
        
    def _on_mouse_click(self, x, y, button, pressed):
        """Callback para cliques do mouse"""
        self.logger.info(f"[RecoilController] Clique do mouse: {button} - Pressionado: {pressed}");
        if button == Button.right:
            self.rbutton_held = pressed
            self.logger.debug(f"[RecoilController] Botão direito: {self.rbutton_held}");
        elif button == Button.left:
            self.lbutton_held = pressed
            self.logger.debug(f"[RecoilController] Botão esquerdo: {self.lbutton_held}");
            
        # Lógica de controle de recoil baseada nos estados dos botões
        if self.rbutton_held and self.lbutton_held: # Ambos os botões estão pressionados
            if not (self._recoil_correction_thread and self._recoil_correction_thread.is_alive()): # Apenas inicia a correção se não estiver já a correr
                self.logger.info("[RecoilController] Ambos os botões (direito e esquerdo) pressionados. Iniciando correção de recoil...")
                self._start_recoil_correction()
        elif not (self.rbutton_held and self.lbutton_held): # Se um ou ambos os botões foram soltos, e não ambos estão pressionados
            if self._recoil_correction_thread and self._recoil_correction_thread.is_alive(): # Só para se a thread estiver ativa
                self.logger.info("[RecoilController] Um dos botões (direito ou esquerdo) foi solto. Parando correção de recoil...")
                self._stop_recoil_correction()
    
    def _on_mouse_move(self, x, y):
        """Callback para movimento do mouse"""
        # O pynput.mouse.Listener passa x, y mas não precisamos deles aqui.
        # Usamos *args para aceitar quaisquer argumentos e ignorá-los.
        self.mouse_controller.update_position()

    
    def _start_recoil_correction(self):
        """Inicia correção de recoil"""
        if not self._recoil_correction_thread or not self._recoil_correction_thread.is_alive():
            self.logger.info("[RecoilController] Iniciando thread de correção de recoil.")
            self.script_running = True # Garante que o script esteja marcado como rodando
            self._recoil_correction_thread = threading.Thread(target=self._recoil_correction_loop, daemon=True)
            self._recoil_correction_thread.start()
        else:
            self.logger.info("[RecoilController] Thread de correção de recoil já está ativa.")

    def _stop_recoil_correction(self):
        """Para correção de recoil"""
        self.logger.info("[RecoilController] Parando thread de correção de recoil.")
        # self.script_running = False # Removido: esta linha causava o encerramento completo do script

    def _recoil_correction_loop(self):
        """Loop de correção de recoil"""
        self.logger.info("[RecoilController] Loop de correção de recoil iniciado.")
        try:
            while self.script_running and self.rbutton_held and self.lbutton_held:
                # Implementação da correção de recoil...
                with self._recoil_lock:
                    recoil_y = self.base_recoil_y
                    recoil_x = self.base_recoil_x

                if recoil_y > 0 or recoil_x != 0: # Apenas move se houver recoil para aplicar
                    dx, dy = self.get_adjusted_recoil(self.settings.sensitivity)
                    # Aplicar suavização se dx ou dy forem muito grandes (opcional)
                    # dx = dx * self.settings.smoothing_factor
                    # dy = dy * self.settings.smoothing_factor

                    # Limitar o movimento para evitar pulos grandes (segurança)
                    dx = max(-self.settings.max_movement, min(self.settings.max_movement, dx))
                    dy = max(-self.settings.max_movement, min(self.settings.max_movement, dy))
                    
                    if abs(dx) > 0.01 or abs(dy) > 0.01: # Adicionado threshold para evitar movimentos minúsculos
                        self.mouse_controller.move(dx, dy)
                        self._last_correction = (dx, dy) # Atualiza a última correção
                        self.logger.debug(f"[RecoilController] Aplicando correção: dx={dx:.2f}, dy={dy:.2f}")

                time.sleep(self.settings.shoot_delay) # Pequeno atraso para simular cadência de tiro
        except Exception as e:
            self.logger.error(f"[RecoilController] Erro inesperado no loop de correção de recoil: {e}")
        finally:
            self.logger.info("[RecoilController] Loop de correção de recoil encerrado.")

    def get_adjusted_recoil(self, factor: float) -> Tuple[float, float]:
        """Calcula correção de recoil ajustada usando base_recoil_x e base_recoil_y"""
        
        with self._recoil_lock: # Adquirir lock para ler
            # Usa os valores base de recoil
            base_horizontal = self.base_recoil_x
            base_vertical = self.base_recoil_y
            self.logger.info(f"Calculando recoil - Base H: {base_horizontal:.2f}, Base V: {base_vertical:.2f}, Fator: {factor:.2f}")
        
        # Aplica fator de correção
        adjusted_horizontal = base_horizontal * factor * self.settings.sensitivity
        adjusted_vertical = base_vertical * factor * self.settings.sensitivity
        
        # Neste ponto, sem suavização, adjusted_horizontal/vertical já são os valores finais
        self._last_correction = (adjusted_horizontal, adjusted_vertical) # Ainda mantém o último valor para debug futuro
        
        # Limitadores de segurança (mantidos)
        adjusted_horizontal = max(-self.settings.max_movement, 
                                min(self.settings.max_movement, adjusted_horizontal))
        adjusted_vertical = max(-self.settings.max_movement, 
                              min(self.settings.max_movement, adjusted_vertical))
        
        return (adjusted_horizontal, adjusted_vertical)

    def _test_recoil(self, factor: float):
        """Testa fator de recoil"""
        self.logger.info("Testando fator de recoil: %.3f", factor)
        self.logger.info("Mantenha ambos os botões pressionados para testar")
        
        old_factor = self.current_factor
        self.current_factor = factor
        
        try:
            # Aguarda teste do usuário
            input("Pressione Enter após testar...")
            
            # Pergunta se deseja manter
            response = input("Deseja manter este fator? (s/n): ")
            if response.lower() not in ['s', 'sim', 'y', 'yes']:
                self.current_factor = old_factor
                self.logger.info("Fator anterior restaurado")
                
        except KeyboardInterrupt:
            self.current_factor = old_factor
            self.logger.info("Teste de fator de recoil cancelado.")

    def set_agent_scope(self, agent: str, scope: str):
        """Define o agente e o escopo atuais."""
        self.current_agent = agent
        self.current_scope = scope
        self.logger.info(f"Agente definido para: {agent}, Escopo para: {scope}")

    def get_session_stats(self) -> Dict:
        """Retorna as estatísticas da sessão atual."""
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
    controller.logger.info(f"RecoilController iniciado. PID: {os.getpid()}")
    # Mantenha a thread principal viva para permitir que as threads em segundo plano sejam executadas
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
        logging.info("RecoilController parado via KeyboardInterrupt.")

# Mover a execução principal para uma função, para que o módulo possa ser importado
if __name__ == "__main__":
    # Configurar o logger para salvar em arquivo
    logging.basicConfig(
        level=logging.DEBUG, # Nível DEBUG para logs mais detalhados
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='recoil_controller.log',
        filemode='w' # 'w' para sobrescrever a cada execução, 'a' para append
    )
    # Adicionar um handler para também imprimir no console, se desejar
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # Nível INFO para o console
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)

    run_recoil_controller_standalone() 