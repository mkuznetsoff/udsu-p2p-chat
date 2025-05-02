{
  description = "Python Qt development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
    
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          pyqt5
          rsa
          qrcode
          pillow
        ]);
        
      in {
        devShell = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.qt5.qttools
            pkgs.glib
            pkgs.libsForQt5.wrapQtAppsHook
          ];

          shellHook = ''
            
            export QT_QPA_PLATFORM_PLUGIN_PATH="${pkgs.qt5.qtbase.bin}/lib/qt-${pkgs.qt5.qtbase.version}/plugins/platforms"
            export LD_LIBRARY_PATH="${pkgs.glib}/lib:$LD_LIBRARY_PATH"
            
            export TMPDIR=/tmp
            export "LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
            export VENV_DIR=$(mktemp -d)
            python -m venv $VENV_DIR
            source $VENV_DIR/bin/activate
            echo "Virtual environment is ready and activated in $VENV_DIR."

            fish

          '';
        };
      });
}
