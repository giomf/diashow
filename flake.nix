{
  description = "A simple python flake";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };
  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };

      # Variable to easily change Python version
      pythonVersion = "313"; # 311 for Python 3.11, 312 for Python 3.12, etc.

      # Use this variable to select the right package set
      pp = pkgs."python${pythonVersion}Packages";
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pkgs.ruff
          pkgs.ty
          pkgs.uv
          pp.python
        ];
      };
    };
}
