{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.python312Packages.pyqt5
    pkgs.qt5.qttools
    pkgs.glib  # Добавляем glib для libgthread-2.0.so.0
    pkgs.python312Packages.rsa
    pkgs.python312Packages.qrcode
    pkgs.python312Packages.pillow
  ];

  LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${pkgs.glib}/lib";
  QT_QPA_PLATFORM_PLUGIN_PATH = "${pkgs.qt5.qtbase.bin}/lib/qt-${pkgs.qt5.qtbase.version}/plugins/platforms";
}
