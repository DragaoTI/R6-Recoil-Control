# Guia de Uso do Recoil Control

Este guia explica como usar o aplicativo Recoil Control para gerenciar as configurações de recuo da arma e os presets de agentes.

https://github.com/user-attachments/assets/459f8606-34a4-4efe-a69f-15d24bfd72f1

## Estrutura de Arquivos

Certifique-se de que as pastas `Agents` e `presets` estejam no mesmo diretório do script principal `main.py`.

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

## Como Iniciar o Aplicativo

Para iniciar o aplicativo, execute o script `main.py`:

```bash
python main.py
```

## Funcionalidades Principais

### Controle de Recuo

*   **Ativar/Desativar Recuo**: O botão principal na interface (`Disabled`/`Enabled`) alterna o controle de recuo.
    *   **Vermelho**: Recuo desativado.
    *   **Verde**: Recuo ativado.
*   **Ajustar Valores de Recuo**:
    *   Use os **sliders** para ajustar visualmente os valores de recuo vertical (Y) e horizontal (X) para a arma primária e secundária.
    *   Você também pode **clicar e digitar** os valores diretamente nos campos de entrada ao lado dos sliders para maior precisão. Pressione `Enter` após digitar para aplicar a alteração.
*   **Arma Ativa**: O aplicativo alterna automaticamente entre o controle de recuo da arma primária e secundária com base nas hotkeys configuradas.

### Configurações (Settings)

Clique no botão "Settings" para abrir a janela de configurações:

*   **Hotkeys**:
    *   **Primary Weapon Hotkey 1 & 2**: Defina as teclas ou botões do mouse para alternar para a arma primária. Clique em "Record" e pressione a tecla/botão desejado.
    *   **Secondary Weapon Hotkey 1 & 2**: Defina as teclas ou botões do mouse para alternar para a arma secundária. Clique em "Record" e pressione a tecla/botão desejado.
*   **Secondary Weapon Enabled**: Marque ou desmarque esta caixa para ativar ou desativar o controle de recuo para a arma secundária.
*   **Shoot Delay**: Ajusta o atraso entre as correções de recuo.
*   **Sensitivity**: Ajusta a sensibilidade geral do controle de recuo.
*   **Max Movement**: Define o movimento máximo permitido para a correção de recuo.

As configurações são salvas automaticamente no arquivo `settings.cfg` sempre que você faz uma alteração.

### Gerenciamento de Presets

Clique no botão "Presets" para abrir a janela de gerenciamento de presets:

1.  **Seleção de Agente**: Escolha entre "Attackers" (Atacantes) ou "Defenders" (Defensores) para ver a lista de agentes. Clique no ícone de um agente para gerenciar seus presets.
2.  **Gerenciar Presets para o Agente Selecionado**:
    *   **Save Preset (Salvar Preset)**: Digite um nome no campo "Preset Name" e clique em "Save Preset" para salvar as configurações de recuo atuais (X e Y para ambas as armas, e se a arma secundária está ativada) como um novo preset para o agente selecionado.
    *   **Load Preset (Carregar Preset)**: Selecione um preset existente na caixa de seleção "Load Existing Preset" e clique em "Load Preset" para aplicar essas configurações. Uma confirmação será solicitada.
    *   **Delete Preset (Excluir Preset)**: Selecione um preset existente na caixa de seleção e clique em "Delete Preset" para removê-lo. Uma confirmação será solicitada.

---
**Observação**: Este aplicativo foi projetado para ajudar no controle de recuo no R6 (Rainbow Six). Use-o de forma responsável e de acordo com os termos de serviço dos jogos. 
