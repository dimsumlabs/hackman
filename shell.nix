{ pkgs ? import <nixpkgs> { } }:
let
  pythonEnv = pkgs.python3.withPackages(_: []);
in
pkgs.mkShell {
  packages = [
    pkgs.poetry
    pythonEnv

    pkgs.redis

    pkgs.fpm
  ];
}
