{
  description = "Hackman";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, poetry2nix }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs lib.systems.flakeExposed;

      poetry2nix' = forAllSystems (system: let
        pkgs = nixpkgs.legacyPackages.${system};
      in poetry2nix.lib.mkPoetry2Nix { inherit pkgs; });

    in
      {
        devShells = forAllSystems (system: let
          pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.callPackage ./shell.nix {
            poetry2nix = poetry2nix'.${system};
          };
        });

        packages = forAllSystems (system: let
          pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.callPackage ./default.nix {
            poetry2nix = poetry2nix'.${system};
          };
        });
      };
}
