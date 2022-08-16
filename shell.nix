{ pkgs ? import <nixpkgs> { } }:
let
  pythonEnv = pkgs.python39.withPackages(_: []);
in
pkgs.mkShell {
  packages = [
    pkgs.poetry
    pythonEnv

    pkgs.redis
    pkgs.postgresql

    pkgs.fpm
  ];
}
