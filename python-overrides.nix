pkgs:
self: super: let
  addSetupTools = drv: drv.overridePythonAttrs(old: {
    nativeBuildInputs = old.nativeBuildInputs ++ [
      self.setuptools
    ];
  });
in {
  mote = addSetupTools super.mote;
  types-cffi = addSetupTools super.types-cffi;

  # Disable compiled mypy.
  # It's faster, but compilation times are long.
  mypy = (super.mypy.override { preferWheel = true; }).overridePythonAttrs(old: {
    MYPY_USE_MYPYC = false;
  });
}
