{ pkgs, poetry2nix }:

let
  pythonEnv = poetry2nix.mkPoetryEnv {
    python = pkgs.python39;
    projectDir = ./.;
    overrides = poetry2nix.overrides.withDefaults (import ./python-overrides.nix pkgs);
  };

in
pkgs.mkShell {
  packages = [
    pkgs.poetry
    pythonEnv

    pkgs.redis
    pkgs.postgresql

    pkgs.hivemind  # Run Procfile

    pkgs.fpm
  ];
}
