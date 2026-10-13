import 'package:flutter/material.dart';

/// Unicode icons mapped to button labels, matching the Python BUTTON_ICONS dict.
const Map<String, String> buttonIcons = {
  // Axis selection
  'All Axes': '✦',
  'North/South': '↕',
  'East/West': '↔',
  'Vertical': '⬍',
  // Mass & Calibration
  'Centre Mass': '⊕',
  'Show Mass': '⚖',
  'Motor (-)': '◀',
  'Motor (+)': '▶',
  'Zero Mass Pos': '⊘',
  'Cal Enable ON': '◉',
  'Cal Enable OFF': '○',
  'All Cal ON': '⬤',
  'All Cal OFF': '◯',
  // Gain
  'Vel * 1': '①',
  'Vel * 2': '②',
  'Vel * 4': '④',
  'Vel * 10': '⑩',
  'Acc * 1': '❶',
  'Acc * 5': '❺',
  'Acc * 10': '❿',
  'Acc * 50': '㊿',
  'Low Gain': '▽',
  'High Gain': '△',
  '0.5g Gain': '▫',
  '1g Gain': '◻',
  '2g Gain': '◼',
  '4g Gain': '⬛',
  // Advanced
  'Sign-On Msg': 'ℹ',
  'Short (30s)': '⏱',
  'Short Period': '⏱',
  'Mid (60s)': '⏲',
  'Long (120s)': '⏳',
  'Long Period': '⏳',
  'Show Params': '☰',
  'Store Params': '💾',
  'Save ADC Zero': '📌',
  'Read ADC Zero': '📋',
  'Print Title': '🏷',
  'Lock Axes': '🔒',
  'Unlock Axes': '🔓',
};

/// Color themes for button group types, matching Python THEMES dict.
const Map<String, Color> groupColors = {
  'axis': Color(0xFF1e5a7a),
  'mass': Color(0xFF8b5e3c),
  'gain': Color(0xFF5e3d7a),
  'adv': Color(0xFF4a5568),
};

class CommandButton {
  final String label;
  final String cmd;
  String get icon => buttonIcons[label] ?? '•';

  const CommandButton({required this.label, required this.cmd});
}

class ButtonGroup {
  final String title;
  final String type;
  final List<CommandButton> buttons;
  Color get color => groupColors[type] ?? const Color(0xFF4a5568);

  const ButtonGroup({
    required this.title,
    required this.type,
    required this.buttons,
  });
}

class SensorProfile {
  final String name;
  final List<ButtonGroup> groups;

  const SensorProfile({required this.name, required this.groups});

  static SensorProfile getProfile(String key) {
    return profiles[key] ?? profiles['pico']!;
  }

  static const Map<String, SensorProfile> profiles = {
    'pico': SensorProfile(
      name: 'θ Theta Pico',
      groups: [
        ButtonGroup(title: '1. Target Axis Select', type: 'axis', buttons: [
          CommandButton(label: 'All Axes', cmd: 'A'),
          CommandButton(label: 'North/South', cmd: 'N'),
          CommandButton(label: 'East/West', cmd: 'E'),
          CommandButton(label: 'Vertical', cmd: 'Z'),
        ]),
        ButtonGroup(title: '2. Mass & Calibration Control', type: 'mass', buttons: [
          CommandButton(label: 'Centre Mass', cmd: 'C'),
          CommandButton(label: 'Show Mass', cmd: 'M'),
          CommandButton(label: 'Motor (-)', cmd: '<'),
          CommandButton(label: 'Motor (+)', cmd: '>'),
          CommandButton(label: 'Cal Enable ON', cmd: 'I'),
          CommandButton(label: 'Cal Enable OFF', cmd: 'K'),
          CommandButton(label: 'All Cal ON', cmd: 'T'),
          CommandButton(label: 'All Cal OFF', cmd: 'R'),
        ]),
        ButtonGroup(title: '3. Gain Control', type: 'gain', buttons: [
          CommandButton(label: 'Vel * 1', cmd: '1V'),
          CommandButton(label: 'Vel * 2', cmd: '2V'),
          CommandButton(label: 'Vel * 4', cmd: '4V'),
          CommandButton(label: 'Vel * 10', cmd: '10V'),
          CommandButton(label: 'Acc * 1', cmd: '1A'),
          CommandButton(label: 'Acc * 5', cmd: '5A'),
          CommandButton(label: 'Acc * 10', cmd: '10A'),
          CommandButton(label: 'Acc * 50', cmd: '50A'),
        ]),
        ButtonGroup(title: '4. Advanced System', type: 'adv', buttons: [
          CommandButton(label: 'Short (30s)', cmd: 'S'),
          CommandButton(label: 'Mid (60s)', cmd: 'L'),
          CommandButton(label: 'Long (120s)', cmd: 'B'),
          CommandButton(label: 'Show Params', cmd: 'D'),
          CommandButton(label: 'Store Params', cmd: 'Q'),
          CommandButton(label: 'Save ADC Zero', cmd: '9'),
          CommandButton(label: 'Read ADC Zero', cmd: '%'),
        ]),
      ],
    ),
    'theta': SensorProfile(
      name: 'θ Theta Standard',
      groups: [
        ButtonGroup(title: '1. Target Axis Select', type: 'axis', buttons: [
          CommandButton(label: 'All Axes', cmd: 'A'),
          CommandButton(label: 'North/South', cmd: 'N'),
          CommandButton(label: 'East/West', cmd: 'E'),
          CommandButton(label: 'Vertical', cmd: 'Z'),
        ]),
        ButtonGroup(title: '2. Mass & Calibration Control', type: 'mass', buttons: [
          CommandButton(label: 'Centre Mass', cmd: 'C'),
          CommandButton(label: 'Show Mass', cmd: 'M'),
          CommandButton(label: 'Motor (-)', cmd: '<'),
          CommandButton(label: 'Motor (+)', cmd: '>'),
          CommandButton(label: 'Zero Mass Pos', cmd: '='),
          CommandButton(label: 'Cal Enable ON', cmd: 'I'),
          CommandButton(label: 'Cal Enable OFF', cmd: 'K'),
        ]),
        ButtonGroup(title: '3. Gain Control', type: 'gain', buttons: [
          CommandButton(label: 'Low Gain', cmd: 'G'),
          CommandButton(label: 'High Gain', cmd: 'H'),
        ]),
        ButtonGroup(title: '4. Advanced System', type: 'adv', buttons: [
          CommandButton(label: 'Sign-On Msg', cmd: '?'),
          CommandButton(label: 'Short Period', cmd: 'S'),
          CommandButton(label: 'Long Period', cmd: 'B'),
          CommandButton(label: 'Show Params', cmd: 'D'),
        ]),
      ],
    ),
    'sigma': SensorProfile(
      name: 'Σ Sigma',
      groups: [
        ButtonGroup(title: '1. Target Axis Select', type: 'axis', buttons: [
          CommandButton(label: 'All Axes', cmd: 'A'),
          CommandButton(label: 'North/South', cmd: 'N'),
          CommandButton(label: 'East/West', cmd: 'E'),
          CommandButton(label: 'Vertical', cmd: 'Z'),
        ]),
        ButtonGroup(title: '2. Mass & Calibration Control', type: 'mass', buttons: [
          CommandButton(label: 'Centre Mass', cmd: 'C'),
          CommandButton(label: 'Show Mass', cmd: 'M'),
          CommandButton(label: 'Motor (-)', cmd: '<'),
          CommandButton(label: 'Motor (+)', cmd: '>'),
          CommandButton(label: 'Zero Mass Pos', cmd: '='),
        ]),
        ButtonGroup(title: '3. Gain Control', type: 'gain', buttons: [
          CommandButton(label: '0.5g Gain', cmd: '1G'),
          CommandButton(label: '1g Gain', cmd: '2G'),
          CommandButton(label: '2g Gain', cmd: '3G'),
          CommandButton(label: '4g Gain', cmd: '4G'),
        ]),
        ButtonGroup(title: '4. Advanced System', type: 'adv', buttons: [
          CommandButton(label: 'Sign-On Msg', cmd: '?'),
          CommandButton(label: 'Show Params', cmd: 'D'),
        ]),
      ],
    ),
    'alpha': SensorProfile(
      name: 'α Alpha',
      groups: [
        ButtonGroup(title: '1. Target Axis Select', type: 'axis', buttons: [
          CommandButton(label: 'All Axes', cmd: 'A'),
          CommandButton(label: 'North/South', cmd: 'N'),
          CommandButton(label: 'East/West', cmd: 'E'),
          CommandButton(label: 'Vertical', cmd: 'Z'),
        ]),
        ButtonGroup(title: '2. Mass & Calibration Control', type: 'mass', buttons: [
          CommandButton(label: 'Centre Mass', cmd: 'C'),
          CommandButton(label: 'Show Mass', cmd: 'M'),
          CommandButton(label: 'Motor (-)', cmd: '<'),
          CommandButton(label: 'Motor (+)', cmd: '>'),
          CommandButton(label: 'Zero Mass Pos', cmd: '='),
          CommandButton(label: 'Cal Enable ON', cmd: 'I'),
          CommandButton(label: 'Cal Enable OFF', cmd: 'K'),
        ]),
        ButtonGroup(title: '3. Advanced System', type: 'adv', buttons: [
          CommandButton(label: 'Sign-On Msg', cmd: '?'),
          CommandButton(label: 'Short Period', cmd: 'S'),
          CommandButton(label: 'Long Period', cmd: 'B'),
          CommandButton(label: 'Show Params', cmd: 'D'),
          CommandButton(label: 'Store Params', cmd: 'Q'),
          CommandButton(label: 'Lock Axes', cmd: 'L'),
          CommandButton(label: 'Unlock Axes', cmd: 'U'),
        ]),
      ],
    ),
  };
}
