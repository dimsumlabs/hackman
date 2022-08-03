{ pkgs ? import <nixpkgs> { } }:

let
  pythonEnv = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = ./.;
  };

in
pkgs.mkShell {
  packages = [
    pythonEnv
    pkgs.poetry

    pkgs.redis

    pkgs.fpm
  ];
}
