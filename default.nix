{ pkgs, poetry2nix }:

poetry2nix.mkPoetryApplication {
  python = pkgs.python39;
  projectDir = ./.;
  overrides = poetry2nix.overrides.withDefaults (import ./python-overrides.nix pkgs);
}
