import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models/sensor_profiles.dart';

/// Responsive grid of grouped command buttons for a sensor profile.
class CommandGrid extends StatelessWidget {
  final SensorProfile profile;
  final ValueChanged<String> onCommandSend;

  const CommandGrid({
    super.key,
    required this.profile,
    required this.onCommandSend,
  });

  int _columnCount(double width) {
    if (width >= 900) return 4;
    if (width >= 600) return 3;
    return 2;
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final cols = _columnCount(constraints.maxWidth);
        return ListView.builder(
          padding: const EdgeInsets.all(12),
          itemCount: profile.groups.length,
          itemBuilder: (_, gi) {
            final group = profile.groups[gi];
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: 12, bottom: 8),
                  child: Text(
                    group.title,
                    style: const TextStyle(
                      color: Color(0xFF0EADB2),
                      fontSize: 15,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: cols,
                    mainAxisSpacing: 8,
                    crossAxisSpacing: 8,
                    childAspectRatio: 1.3,
                  ),
                  itemCount: group.buttons.length,
                  itemBuilder: (_, bi) {
                    final btn = group.buttons[bi];
                    return _CommandButton(
                      btn: btn,
                      color: group.color,
                      onTap: () {
                        HapticFeedback.mediumImpact();
                        onCommandSend(btn.cmd);
                      },
                    );
                  },
                ),
              ],
            );
          },
        );
      },
    );
  }
}

class _CommandButton extends StatelessWidget {
  final CommandButton btn;
  final Color color;
  final VoidCallback onTap;

  const _CommandButton({
    required this.btn,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: color,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        splashColor: Colors.white24,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                btn.icon,
                style: const TextStyle(fontSize: 24),
              ),
              const SizedBox(height: 4),
              Text(
                btn.label,
                textAlign: TextAlign.center,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                btn.cmd,
                style: const TextStyle(
                  color: Colors.white54,
                  fontSize: 10,
                  fontFamily: 'RobotoMono',
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
